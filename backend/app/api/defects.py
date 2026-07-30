"""Defects API routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.user import User
from app.models.defect import Defect
from app.schemas.defect import DefectCreate, DefectUpdate, DefectStatusUpdate, DefectOut
from app.utils.pagination import success_response, error_response, make_paginated_response
from app.middleware.auth import get_current_user

router = APIRouter()


@router.get("")
async def list_defects(
    project_id: int = Query(0), status: str = Query("", max_length=16),
    severity: str = Query("", max_length=16), assignee_id: int = Query(0),
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(Defect).order_by(Defect.created_at.desc())
    count_q = select(func.count(Defect.id))
    if project_id:
        q = q.where(Defect.project_id == project_id)
        count_q = count_q.where(Defect.project_id == project_id)
    if status:
        q = q.where(Defect.status == status)
        count_q = count_q.where(Defect.status == status)
    if severity:
        q = q.where(Defect.severity == severity)
        count_q = count_q.where(Defect.severity == severity)
    if assignee_id:
        q = q.where(Defect.assignee_id == assignee_id)
        count_q = count_q.where(Defect.assignee_id == assignee_id)

    total = (await db.execute(count_q)).scalar()
    defects = (await db.execute(q.offset((page - 1) * page_size).limit(page_size))).scalars().all()
    return make_paginated_response(
        [DefectOut.model_validate(d).model_dump() for d in defects], total, page, page_size
    )


@router.post("")
async def create_defect(
    req: DefectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    defect = Defect(**req.model_dump())
    db.add(defect)
    await db.flush()
    return success_response(DefectOut.model_validate(defect).model_dump(), "缺陷创建成功")


@router.get("/{defect_id}")
async def get_defect(defect_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    defect = await db.get(Defect, defect_id)
    if not defect:
        return error_response(404, "缺陷不存在")
    return success_response(DefectOut.model_validate(defect).model_dump())


@router.put("/{defect_id}")
async def update_defect(
    defect_id: int, req: DefectUpdate,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),
):
    defect = await db.get(Defect, defect_id)
    if not defect:
        return error_response(404, "缺陷不存在")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(defect, k, v)
    await db.flush()
    return success_response(DefectOut.model_validate(defect).model_dump(), "缺陷更新成功")


@router.patch("/{defect_id}/status")
async def update_defect_status(
    defect_id: int, req: DefectStatusUpdate,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),
):
    defect = await db.get(Defect, defect_id)
    if not defect:
        return error_response(404, "缺陷不存在")
    defect.status = req.status
    await db.flush()
    return success_response(None, "缺陷状态已更新")


@router.delete("/{defect_id}")
async def delete_defect(defect_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    defect = await db.get(Defect, defect_id)
    if not defect:
        return error_response(404, "缺陷不存在")
    await db.delete(defect)
    await db.flush()
    return success_response(None, "缺陷已删除")


@router.get("/stats/summary")
async def defect_stats(
    project_id: int = Query(0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(Defect)
    if project_id:
        q = q.where(Defect.project_id == project_id)
    defects = (await db.execute(q)).scalars().all()

    by_severity = {}
    by_status = {}
    for d in defects:
        sev = d.severity.value if hasattr(d.severity, 'value') else d.severity
        st = d.status.value if hasattr(d.status, 'value') else d.status
        by_severity[sev] = by_severity.get(sev, 0) + 1
        by_status[st] = by_status.get(st, 0) + 1

    return success_response({
        "total": len(defects),
        "by_severity": by_severity,
        "by_status": by_status,
    })
