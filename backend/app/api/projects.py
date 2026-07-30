"""Projects API routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from app.database import get_db
from app.models.user import User
from app.models.project import Project, ProjectMember, MemberRole
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut
from app.utils.pagination import success_response, error_response, make_paginated_response
from app.middleware.auth import get_current_user

router = APIRouter()


@router.get("")
async def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query("", max_length=16),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(Project)
    count_q = select(func.count(Project.id))
    if status:
        q = q.where(Project.status == status)
        count_q = count_q.where(Project.status == status)

    total = (await db.execute(count_q)).scalar()
    projects = (await db.execute(q.offset((page - 1) * page_size).limit(page_size))).scalars().all()
    return make_paginated_response(
        [ProjectOut.model_validate(p).model_dump() for p in projects],
        total, page, page_size
    )


@router.post("")
async def create_project(
    req: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = await db.execute(select(Project).where(Project.key == req.key.upper()))
    if existing.scalar_one_or_none():
        return error_response(409, "项目标识已存在")

    project = Project(
        key=req.key.upper(),
        name=req.name,
        name_en=req.name_en,
        description=req.description,
        color=req.color,
        owner_id=current_user.id,
        start_date=req.start_date,
        end_date=req.end_date,
    )
    db.add(project)
    await db.flush()

    # Auto-add creator as owner member
    db.add(ProjectMember(project_id=project.id, user_id=current_user.id, role=MemberRole.OWNER))
    await db.flush()

    return success_response(ProjectOut.model_validate(project).model_dump(), "项目创建成功")


@router.get("/{project_id}")
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = await db.get(Project, project_id)
    if not project:
        return error_response(404, "项目不存在")
    return success_response(ProjectOut.model_validate(project).model_dump())


@router.put("/{project_id}")
async def update_project(
    project_id: int,
    req: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = await db.get(Project, project_id)
    if not project:
        return error_response(404, "项目不存在")
    update_data = req.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(project, k, v)
    await db.flush()
    return success_response(ProjectOut.model_validate(project).model_dump(), "项目更新成功")


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = await db.get(Project, project_id)
    if not project:
        return error_response(404, "项目不存在")
    await db.delete(project)
    await db.flush()
    return success_response(None, "项目已删除")


@router.get("/{project_id}/members")
async def list_members(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ProjectMember, User).join(User).where(ProjectMember.project_id == project_id)
    )
    rows = result.all()
    members = []
    for pm, u in rows:
        members.append({
            "id": u.id, "name": u.name, "name_en": u.name_en,
            "email": u.email, "avatar": u.avatar,
            "role": pm.role.value if hasattr(pm.role, 'value') else pm.role,
        })
    return success_response(members)


@router.post("/{project_id}/members")
async def add_member(
    project_id: int,
    user_id: int,
    role: str = "member",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    )
    if existing.scalar_one_or_none():
        return error_response(409, "该成员已在项目中")
    db.add(ProjectMember(project_id=project_id, user_id=user_id, role=role))
    await db.flush()
    return success_response(None, "成员添加成功")


@router.delete("/{project_id}/members/{user_id}")
async def remove_member(
    project_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await db.execute(
        delete(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    )
    await db.flush()
    return success_response(None, "成员已移除")
