"""Auth API - login, register with admin approval."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.utils.security import hash_password, verify_password, create_access_token
from app.utils.pagination import success_response, error_response
from app.middleware.auth import get_current_user

router = APIRouter()


@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == req.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.password_hash):
        return error_response(401, "用户名或密码错误")
    if user.status == "pending":
        return error_response(403, "账号正在等待管理员审核，请耐心等待")
    if user.status == "rejected":
        return error_response(403, "账号申请已被拒绝，请联系管理员")

    token = create_access_token(data={"sub": str(user.id), "username": user.username})
    return success_response({
        "access_token": token, "token_type": "bearer", "expires_in": 604800,
        "user": {"id": user.id, "username": user.username, "name": user.name,
                 "email": user.email or "", "role": user.role.value if hasattr(user.role, 'value') else user.role},
    })


@router.post("/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check existing
    u = (await db.execute(select(User).where(User.username == req.username))).scalar_one_or_none()
    if u: return error_response(409, "用户名已存在")
    # Phone uniqueness
    if req.phone:
        p = (await db.execute(select(User).where(User.phone == req.phone))).scalar_one_or_none()
        if p: return error_response(409, "手机号已被注册")
    # Strong password: at least 8 chars, letters + digits
    if len(req.password) < 8:
        return error_response(400, "密码至少8位")
    if not any(c.isalpha() for c in req.password) or not any(c.isdigit() for c in req.password):
        return error_response(400, "密码需包含字母和数字")

    user = User(
        username=req.username, password_hash=hash_password(req.password),
        name=req.name, email=req.email or "", phone=req.phone or "",
        gender=req.gender or "", age=req.age or 0,
        status="pending", role="member",
    )
    db.add(user)
    await db.flush()
    return success_response({"id": user.id}, "注册已提交，请等待管理员审核")


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return success_response({
        "id": current_user.id, "username": current_user.username,
        "name": current_user.name, "email": current_user.email or "",
        "phone": current_user.phone or "", "gender": current_user.gender or "",
        "age": current_user.age or 0, "status": current_user.status or "active",
        "role": current_user.role.value if hasattr(current_user.role, 'value') else current_user.role,
        "dept": current_user.dept or "", "title": current_user.title or "",
    })
