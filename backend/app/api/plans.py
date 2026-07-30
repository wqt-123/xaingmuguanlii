"""Plans API routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.user import User
from app.models.plan import Plan
from app.schemas.plan import PlanCreate, PlanUpdate, PlanOut
from app.utils.pagination import success_response, error_response, make_paginated_response
from app.middleware.auth import get_current_user

router = APIRouter()


@router.get("")
async def list_plans(
    project_id: int = Query(0), page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query("", max_length=16),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(Plan)
    count_q = select(func.count(Plan.id))
    if project_id:
        q = q.where(Plan.project_id == project_id)
        count_q = count_q.where(Plan.project_id == project_id)
    if status:
        q = q.where(Plan.status == status)
        count_q = count_q.where(Plan.status == status)

    q = q.order_by(Plan.created_at.desc())
    total = (await db.execute(count_q)).scalar()
    plans = (await db.execute(q.offset((page - 1) * page_size).limit(page_size))).scalars().all()
    return make_paginated_response(
        [PlanOut.model_validate(p).model_dump() for p in plans], total, page, page_size
    )


@router.post("")
async def create_plan(
    req: PlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = Plan(**req.model_dump())
    db.add(plan)
    await db.flush()
    return success_response(PlanOut.model_validate(plan).model_dump(), "计划创建成功")


@router.get("/{plan_id}")
async def get_plan(plan_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = await db.get(Plan, plan_id)
    if not plan:
        return error_response(404, "计划不存在")
    return success_response(PlanOut.model_validate(plan).model_dump())


@router.put("/{plan_id}")
async def update_plan(
    plan_id: int, req: PlanUpdate,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),
):
    plan = await db.get(Plan, plan_id)
    if not plan:
        return error_response(404, "计划不存在")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(plan, k, v)
    await db.flush()
    return success_response(PlanOut.model_validate(plan).model_dump(), "计划更新成功")


@router.delete("/{plan_id}")
async def delete_plan(plan_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = await db.get(Plan, plan_id)
    if not plan:
        return error_response(404, "计划不存在")
    await db.delete(plan)
    await db.flush()
    return success_response(None, "计划已删除")


@router.post("/{plan_id}/submit")
async def submit_plan(plan_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = await db.get(Plan, plan_id)
    if not plan:
        return error_response(404, "计划不存在")
    plan.status = "pending"
    await db.flush()
    return success_response(None, "计划已提交审核")


@router.post("/{plan_id}/approve")
async def approve_plan(plan_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = await db.get(Plan, plan_id)
    if not plan:
        return error_response(404, "计划不存在")
    plan.status = "active"
    await db.flush()
    return success_response(None, "计划已通过审核")
