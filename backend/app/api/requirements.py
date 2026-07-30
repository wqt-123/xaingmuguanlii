"""Requirements API routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.user import User
from app.models.requirement import Requirement
from app.models.requirement_change import RequirementChange
from app.schemas.requirement import RequirementCreate, RequirementUpdate, RequirementOut
from app.utils.pagination import success_response, error_response, make_paginated_response
from app.middleware.auth import get_current_user

router = APIRouter()


@router.get("")
async def list_requirements(
    project_id: int = Query(0), status: str = Query("", max_length=16),
    priority: str = Query("", max_length=4),
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(Requirement).order_by(Requirement.created_at.desc())
    count_q = select(func.count(Requirement.id))
    if project_id:
        q = q.where(Requirement.project_id == project_id)
        count_q = count_q.where(Requirement.project_id == project_id)
    if status:
        q = q.where(Requirement.status == status)
        count_q = count_q.where(Requirement.status == status)
    if priority:
        q = q.where(Requirement.priority == priority)
        count_q = count_q.where(Requirement.priority == priority)

    total = (await db.execute(count_q)).scalar()
    reqs = (await db.execute(q.offset((page - 1) * page_size).limit(page_size))).scalars().all()
    return make_paginated_response(
        [RequirementOut.model_validate(r).model_dump() for r in reqs], total, page, page_size
    )


@router.post("")
async def create_requirement(
    req: RequirementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    requirement = Requirement(**req.model_dump())
    db.add(requirement)
    await db.flush()
    return success_response(RequirementOut.model_validate(requirement).model_dump(), "需求创建成功")


@router.get("/{req_id}")
async def get_requirement(req_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    req = await db.get(Requirement, req_id)
    if not req:
        return error_response(404, "需求不存在")
    return success_response(RequirementOut.model_validate(req).model_dump())


@router.put("/{req_id}")
async def update_requirement(
    req_id: int, req_data: RequirementUpdate,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),
):
    req = await db.get(Requirement, req_id)
    if not req:
        return error_response(404, "需求不存在")
    for k, v in req_data.model_dump(exclude_unset=True).items():
        setattr(req, k, v)
    await db.flush()
    return success_response(RequirementOut.model_validate(req).model_dump(), "需求更新成功")


@router.delete("/{req_id}")
async def delete_requirement(req_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    req = await db.get(Requirement, req_id)
    if not req:
        return error_response(404, "需求不存在")
    await db.delete(req)
    await db.flush()
    return success_response(None, "需求已删除")


@router.post("/{req_id}/submit_review")
async def submit_review(req_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    req = await db.get(Requirement, req_id)
    if not req:
        return error_response(404, "需求不存在")
    req.status = "pending_review"
    await db.flush()
    return success_response(None, "需求已提交评审")


@router.get("/{req_id}/changes")
async def list_changes(req_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(RequirementChange).where(RequirementChange.requirement_id == req_id).order_by(RequirementChange.created_at.desc())
    )
    changes = result.scalars().all()
    return success_response([{"id": c.id, "change_desc": c.change_desc, "reason": c.reason,
                              "impact": c.impact, "status": c.status.value if hasattr(c.status, 'value') else c.status,
                              "requester_id": c.requester_id, "created_at": c.created_at.isoformat() if c.created_at else None}
                             for c in changes])
