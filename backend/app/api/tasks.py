"""Tasks API routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, or_
from app.database import get_db
from app.models.user import User
from app.models.task import Task
from app.models.milestone import Milestone
from app.models.dependency import TaskDependency
from app.schemas.task import TaskCreate, TaskUpdate, TaskStatusUpdate, TaskMove, TaskOut
from app.utils.pagination import success_response, error_response, make_paginated_response
from app.middleware.auth import get_current_user

router = APIRouter()


@router.get("")
async def list_tasks(
    plan_id: int = Query(0), project_id: int = Query(0),
    assignee_id: int = Query(0), status: str = Query("", max_length=16),
    parent_id: int = Query(-1),  # -1 = all, 0 = only root, >0 = children of parent
    page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(Task)
    count_q = select(func.count(Task.id))
    if plan_id:
        q = q.where(Task.plan_id == plan_id)
        count_q = count_q.where(Task.plan_id == plan_id)
    if project_id:
        q = q.where(Task.project_id == project_id)
        count_q = count_q.where(Task.project_id == project_id)
    if assignee_id:
        q = q.where(Task.assignee_id == assignee_id)
        count_q = count_q.where(Task.assignee_id == assignee_id)
    if status:
        q = q.where(Task.status == status)
        count_q = count_q.where(Task.status == status)
    if parent_id == 0:
        q = q.where(Task.parent_id.is_(None))
        count_q = count_q.where(Task.parent_id.is_(None))
    elif parent_id > 0:
        q = q.where(Task.parent_id == parent_id)
        count_q = count_q.where(Task.parent_id == parent_id)

    q = q.order_by(Task.sort_order, Task.created_at)
    total = (await db.execute(count_q)).scalar()
    tasks = (await db.execute(q.offset((page - 1) * page_size).limit(page_size))).scalars().all()
    return make_paginated_response(
        [TaskOut.model_validate(t).model_dump() for t in tasks], total, page, page_size
    )


@router.get("/my")
async def my_tasks(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Task).where(Task.assignee_id == current_user.id, Task.status != "done")
            .order_by(Task.priority, Task.end_date)
    )
    tasks = result.scalars().all()
    return success_response([TaskOut.model_validate(t).model_dump() for t in tasks])


@router.post("")
async def create_task(
    req: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = Task(**req.model_dump())
    db.add(task)
    await db.flush()
    return success_response(TaskOut.model_validate(task).model_dump(), "任务创建成功")


@router.get("/{task_id}")
async def get_task(task_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = await db.get(Task, task_id)
    if not task:
        return error_response(404, "任务不存在")
    return success_response(TaskOut.model_validate(task).model_dump())


@router.put("/{task_id}")
async def update_task(
    task_id: int, req: TaskUpdate,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),
):
    task = await db.get(Task, task_id)
    if not task:
        return error_response(404, "任务不存在")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(task, k, v)
    await db.flush()
    return success_response(TaskOut.model_validate(task).model_dump(), "任务更新成功")


@router.patch("/{task_id}/status")
async def update_task_status(
    task_id: int, req: TaskStatusUpdate,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),
):
    task = await db.get(Task, task_id)
    if not task:
        return error_response(404, "任务不存在")
    task.status = req.status
    await db.flush()
    return success_response(None, "任务状态已更新")


@router.put("/{task_id}/move")
async def move_task(
    task_id: int, req: TaskMove,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),
):
    task = await db.get(Task, task_id)
    if not task:
        return error_response(404, "任务不存在")
    if req.new_parent_id is not None:
        task.parent_id = req.new_parent_id
    if req.new_sort_order is not None:
        task.sort_order = req.new_sort_order
    await db.flush()
    return success_response(None, "任务已移动")


@router.delete("/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = await db.get(Task, task_id)
    if not task:
        return error_response(404, "任务不存在")
    await db.delete(task)
    await db.flush()
    return success_response(None, "任务已删除")


# Gantt data endpoint
@router.get("/gantt/{plan_id}")
async def get_gantt_data(plan_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    tasks_result = await db.execute(select(Task).where(Task.plan_id == plan_id))
    tasks = tasks_result.scalars().all()
    milestones_result = await db.execute(select(Milestone).where(Milestone.plan_id == plan_id))
    milestones = milestones_result.scalars().all()
    deps_result = await db.execute(
        select(TaskDependency).where(
            TaskDependency.predecessor_id.in_([t.id for t in tasks])
        )
    )
    deps = deps_result.scalars().all()
    return success_response({
        "tasks": [TaskOut.model_validate(t).model_dump() for t in tasks],
        "milestones": [{"id": m.id, "title": m.title, "date": m.date.isoformat() if m.date else None,
                         "status": m.status.value if hasattr(m.status, 'value') else m.status} for m in milestones],
        "dependencies": [{"id": d.id, "predecessor_id": d.predecessor_id, "successor_id": d.successor_id,
                           "dep_type": d.dep_type} for d in deps],
    })


# Task dependency endpoints
@router.post("/dependencies")
async def create_dependency(
    predecessor_id: int, successor_id: int, dep_type: str = "FS",
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),
):
    dep = TaskDependency(predecessor_id=predecessor_id, successor_id=successor_id, dep_type=dep_type)
    db.add(dep)
    await db.flush()
    return success_response({"id": dep.id, "predecessor_id": dep.predecessor_id,
                             "successor_id": dep.successor_id, "dep_type": dep.dep_type}, "依赖已创建")


@router.delete("/dependencies/{dep_id}")
async def delete_dependency(dep_id: int, db: AsyncSession = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    dep = await db.get(TaskDependency, dep_id)
    if dep:
        await db.delete(dep)
        await db.flush()
    return success_response(None, "依赖已删除")


@router.get("/dependencies/{plan_id}")
async def list_dependencies(plan_id: int, db: AsyncSession = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    tasks = (await db.execute(select(Task.id).where(Task.plan_id == plan_id))).scalars().all()
    tids = list(tasks)
    deps = (await db.execute(select(TaskDependency).where(
        or_(TaskDependency.predecessor_id.in_(tids), TaskDependency.successor_id.in_(tids))
    ))).scalars().all()
    return success_response([{"id": d.id, "predecessor_id": d.predecessor_id,
                              "successor_id": d.successor_id, "dep_type": d.dep_type} for d in deps])
