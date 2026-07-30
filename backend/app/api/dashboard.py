"""Dashboard API routes - real-time stats from database."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.plan import Plan
from app.models.task import Task
from app.models.requirement import Requirement
from app.models.defect import Defect
from app.utils.pagination import success_response
from app.middleware.auth import get_current_user

router = APIRouter()
now = datetime.now(timezone.utc)


@router.get("/summary")
async def dashboard_summary(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_projects = (await db.execute(select(func.count(Project.id)))).scalar()
    active_projects = (await db.execute(select(func.count(Project.id)).where(Project.status == "active"))).scalar()

    total_tasks = (await db.execute(select(func.count(Task.id)))).scalar()
    done_tasks = (await db.execute(select(func.count(Task.id)).where(Task.status == "done"))).scalar()
    completion_rate = round(done_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0

    overdue_tasks = (await db.execute(
        select(func.count(Task.id)).where(Task.end_date < now, Task.status != "done")
    )).scalar()

    pending_reqs = (await db.execute(
        select(func.count(Requirement.id)).where(Requirement.status == "pending_review")
    )).scalar()

    open_defects = (await db.execute(
        select(func.count(Defect.id)).where(Defect.status.not_in(["closed", "verified"]))
    )).scalar()

    return success_response({
        "total_projects": total_projects,
        "active_projects": active_projects,
        "task_completion_rate": completion_rate,
        "overdue_tasks": overdue_tasks,
        "pending_requirements": pending_reqs,
        "open_defects": open_defects,
    })


@router.get("/progress")
async def dashboard_progress(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    projects = (await db.execute(select(Project).where(Project.status == "active"))).scalars().all()
    progress = []
    for p in projects:
        total = (await db.execute(select(func.count(Task.id)).where(Task.project_id == p.id))).scalar()
        done = (await db.execute(
            select(func.count(Task.id)).where(Task.project_id == p.id, Task.status == "done")
        )).scalar()
        progress.append({
            "project_id": p.id,
            "project_name": p.name,
            "total_tasks": total,
            "completed_tasks": done,
            "completion_rate": round(done / total * 100, 1) if total > 0 else 0,
            "status": p.status.value if hasattr(p.status, 'value') else p.status,
        })
    return success_response(progress)


@router.get("/risks")
async def dashboard_risks(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    risks = []

    # Overdue tasks
    overdue = (await db.execute(
        select(Task).where(Task.end_date < now, Task.status != "done").limit(10)
    )).scalars().all()
    for t in overdue:
        risks.append({
            "id": t.id, "type": "overdue_task", "title": t.title,
            "severity": "high", "target_id": t.id,
            "due_date": t.end_date.isoformat() if t.end_date else None,
        })

    # High priority open defects
    severe = (await db.execute(
        select(Defect).where(Defect.severity.in_(["critical", "major"]), Defect.status.not_in(["closed", "verified"])).limit(5)
    )).scalars().all()
    for d in severe:
        risks.append({
            "id": d.id, "type": "severe_defect", "title": d.title,
            "severity": "high", "target_id": d.id, "due_date": None,
        })

    return success_response(risks)


@router.get("/my-todos")
async def my_todos(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    todos = []

    my_tasks = (await db.execute(
        select(Task).where(Task.assignee_id == current_user.id, Task.status.not_in(["done"])).limit(20)
    )).scalars().all()
    for t in my_tasks:
        todos.append({
            "id": t.id, "type": "task", "title": t.title,
            "priority": t.priority.value if hasattr(t.priority, 'value') else t.priority,
            "due_date": t.end_date.isoformat() if t.end_date else None,
            "status": t.status.value if hasattr(t.status, 'value') else t.status,
        })

    my_defects = (await db.execute(
        select(Defect).where(Defect.assignee_id == current_user.id, Defect.status.not_in(["closed", "verified"])).limit(10)
    )).scalars().all()
    for d in my_defects:
        todos.append({
            "id": d.id, "type": "defect", "title": d.title,
            "priority": d.priority.value if hasattr(d.priority, 'value') else d.priority,
            "due_date": None,
            "status": d.status.value if hasattr(d.status, 'value') else d.status,
        })

    return success_response(todos)
