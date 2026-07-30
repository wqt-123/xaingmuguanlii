"""Auth API routes - login, register."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.utils.security import hash_password, verify_password, create_access_token
from app.utils.pagination import success_response, error_response
from app.middleware.auth import get_current_user

router = APIRouter()


@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == req.username))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(req.password, user.password_hash):
        return error_response(401, "用户名或密码错误")

    token = create_access_token(data={"sub": str(user.id), "username": user.username})
    return success_response({
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 604800,
        "user": {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "name_en": user.name_en,
            "email": user.email,
            "role": user.role.value if hasattr(user.role, 'value') else user.role,
            "avatar": user.avatar,
        },
    })


@router.post("/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.username == req.username))
    if existing.scalar_one_or_none():
        return error_response(409, "用户名已存在")

    user = User(
        username=req.username,
        password_hash=hash_password(req.password),
        name=req.name,
        email=req.email,
    )
    db.add(user)
    await db.flush()

    token = create_access_token(data={"sub": str(user.id), "username": user.username})
    return success_response({
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 604800,
        "user": {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "role": "member",
        },
    })


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return success_response({
        "id": current_user.id,
        "username": current_user.username,
        "name": current_user.name,
        "name_en": current_user.name_en,
        "email": current_user.email,
        "phone": current_user.phone,
        "role": current_user.role.value if hasattr(current_user.role, 'value') else current_user.role,
        "dept": current_user.dept,
        "title": current_user.title,
        "avatar": current_user.avatar,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
    })
