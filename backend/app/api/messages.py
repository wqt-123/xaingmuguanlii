"""Messages API - inter-user messaging."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, or_, desc
from app.database import get_db
from app.models.user import User
from app.models.message import Message
from app.utils.pagination import success_response, error_response, make_paginated_response
from app.middleware.auth import get_current_user

router = APIRouter()


@router.get("/inbox")
async def inbox(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),
):
    q = select(Message).where(Message.receiver_id == current_user.id).order_by(desc(Message.sent_at))
    count_q = select(func.count(Message.id)).where(Message.receiver_id == current_user.id)
    total = (await db.execute(count_q)).scalar()
    msgs = (await db.execute(q.offset((page - 1) * page_size).limit(page_size))).scalars().all()

    # Get sender names
    sender_ids = list(set(m.sender_id for m in msgs))
    senders = {}
    if sender_ids:
        s = await db.execute(select(User.id, User.name).where(User.id.in_(sender_ids)))
        for row in s: senders[row[0]] = row[1]

    items = [{"id": m.id, "sender_id": m.sender_id, "sender_name": senders.get(m.sender_id, "?"),
              "subject": m.subject, "body": m.body, "is_read": m.is_read,
              "sent_at": m.sent_at.isoformat() if m.sent_at else None} for m in msgs]
    return make_paginated_response(items, total, page, page_size)


@router.get("/sent")
async def sent(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),
):
    q = select(Message).where(Message.sender_id == current_user.id).order_by(desc(Message.sent_at))
    count_q = select(func.count(Message.id)).where(Message.sender_id == current_user.id)
    total = (await db.execute(count_q)).scalar()
    msgs = (await db.execute(q.offset((page - 1) * page_size).limit(page_size))).scalars().all()

    receiver_ids = list(set(m.receiver_id for m in msgs))
    receivers = {}
    if receiver_ids:
        s = await db.execute(select(User.id, User.name).where(User.id.in_(receiver_ids)))
        for row in s: receivers[row[0]] = row[1]

    items = [{"id": m.id, "receiver_id": m.receiver_id, "receiver_name": receivers.get(m.receiver_id, "?"),
              "subject": m.subject, "body": m.body, "is_read": m.is_read,
              "sent_at": m.sent_at.isoformat() if m.sent_at else None} for m in msgs]
    return make_paginated_response(items, total, page, page_size)


@router.get("/unread-count")
async def unread_count(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    cnt = (await db.execute(
        select(func.count(Message.id)).where(Message.receiver_id == current_user.id, Message.is_read == False)
    )).scalar()
    return success_response({"count": cnt})


@router.post("")
async def send_message(
    receiver_id: int, subject: str = "", body: str = "",
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),
):
    msg = Message(sender_id=current_user.id, receiver_id=receiver_id, subject=subject, body=body)
    db.add(msg)
    await db.flush()
    return success_response({"id": msg.id}, "消息发送成功")


@router.put("/{msg_id}/read")
async def mark_read(msg_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    msg = await db.get(Message, msg_id)
    if msg and msg.receiver_id == current_user.id:
        msg.is_read = True
        await db.flush()
    return success_response(None, "已读")
