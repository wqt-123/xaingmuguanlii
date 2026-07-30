"""Users API routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserOut, UserCreate, UserUpdate
from app.utils.security import hash_password
from app.utils.pagination import success_response, error_response, make_paginated_response
from app.middleware.auth import get_current_user
from app.middleware.rbac import require_admin

router = APIRouter()


@router.get("")
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query("", max_length=128),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(User)
    count_q = select(func.count(User.id))
    if search:
        q = q.where(User.name.contains(search) | User.username.contains(search))
        count_q = count_q.where(User.name.contains(search) | User.username.contains(search))

    total = (await db.execute(count_q)).scalar()
    users = (await db.execute(q.offset((page - 1) * page_size).limit(page_size))).scalars().all()
    return make_paginated_response(
        [UserOut.model_validate(u).model_dump() for u in users],
        total, page, page_size
    )


@router.post("")
async def create_user(
    req: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    existing = await db.execute(select(User).where(User.username == req.username))
    if existing.scalar_one_or_none():
        return error_response(409, "用户名已存在")
    user = User(
        username=req.username,
        password_hash=hash_password(req.password),
        name=req.name,
        name_en=req.name_en,
        email=req.email,
        phone=req.phone,
        role=req.role,
        dept=req.dept,
        title=req.title,
    )
    db.add(user)
    await db.flush()
    return success_response(UserOut.model_validate(user).model_dump(), "用户创建成功")


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = await db.get(User, user_id)
    if not user:
        return error_response(404, "用户不存在")
    return success_response(UserOut.model_validate(user).model_dump())


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    req: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = await db.get(User, user_id)
    if not user:
        return error_response(404, "用户不存在")
    update_data = req.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(user, k, v)
    await db.flush()
    return success_response(UserOut.model_validate(user).model_dump(), "用户更新成功")


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = await db.get(User, user_id)
    if not user:
        return error_response(404, "用户不存在")
    await db.delete(user)
    await db.flush()
    return success_response(None, "用户已删除")
