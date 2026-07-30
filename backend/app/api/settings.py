"""User settings API - personal preferences."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.user_settings import UserSettings
from app.utils.security import hash_password, verify_password
from app.utils.pagination import success_response, error_response
from app.middleware.auth import get_current_user

router = APIRouter()


@router.get("/profile")
async def get_profile(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return success_response({
        "id": current_user.id, "username": current_user.username,
        "name": current_user.name, "name_en": current_user.name_en or "",
        "email": current_user.email or "", "phone": current_user.phone or "",
        "dept": current_user.dept or "", "title": current_user.title or "",
        "role": current_user.role.value if hasattr(current_user.role, 'value') else current_user.role,
    })


@router.put("/profile")
async def update_profile(
    name: str = "", email: str = "", phone: str = "", dept: str = "", title: str = "",
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),
):
    if name: current_user.name = name
    if email: current_user.email = email
    if phone: current_user.phone = phone
    if dept: current_user.dept = dept
    if title: current_user.title = title
    await db.flush()
    return success_response(None, "个人信息已更新")


@router.post("/change-password")
async def change_password(
    old_password: str, new_password: str,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),
):
    if not verify_password(old_password, current_user.password_hash):
        return error_response(400, "旧密码错误")
    if len(new_password) < 6:
        return error_response(400, "新密码至少6位")
    current_user.password_hash = hash_password(new_password)
    await db.flush()
    return success_response(None, "密码已更新")


@router.get("/preferences")
async def get_preferences(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(UserSettings).where(UserSettings.user_id == current_user.id))
    s = result.scalar_one_or_none()
    if not s:
        s = UserSettings(user_id=current_user.id)
        db.add(s)
        await db.flush()
    return success_response({
        "font_size": s.font_size, "language": s.language,
        "notify_enabled": s.notify_enabled,
    })


@router.put("/preferences")
async def update_preferences(
    font_size: str = "", language: str = "", notify_enabled: bool = None,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(UserSettings).where(UserSettings.user_id == current_user.id))
    s = result.scalar_one_or_none()
    if not s:
        s = UserSettings(user_id=current_user.id)
        db.add(s)
    if font_size: s.font_size = font_size
    if language: s.language = language
    if notify_enabled is not None: s.notify_enabled = notify_enabled
    await db.flush()
    return success_response(None, "偏好已更新")
