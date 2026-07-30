"""Notifications API routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from app.database import get_db
from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import NotificationOut
from app.utils.pagination import success_response, make_paginated_response
from app.middleware.auth import get_current_user

router = APIRouter()


@router.get("")
async def list_notifications(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(Notification).where(Notification.user_id == current_user.id).order_by(Notification.created_at.desc())
    count_q = select(func.count(Notification.id)).where(Notification.user_id == current_user.id)

    total = (await db.execute(count_q)).scalar()
    notifs = (await db.execute(q.offset((page - 1) * page_size).limit(page_size))).scalars().all()
    unread = (await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == current_user.id, Notification.is_read == False
        )
    )).scalar()

    return make_paginated_response(
        [NotificationOut.model_validate(n).model_dump() for n in notifs], total, page, page_size
    )


@router.put("/{notif_id}/read")
async def mark_read(
    notif_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notif = await db.get(Notification, notif_id)
    if notif:
        notif.is_read = True
        await db.flush()
    return success_response(None, "已标记为已读")


@router.put("/read-all")
async def mark_all_read(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await db.execute(
        update(Notification).where(
            Notification.user_id == current_user.id
        ).values(is_read=True)
    )
    await db.flush()
    return success_response(None, "全部已读")
