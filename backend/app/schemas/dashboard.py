"""Dashboard response schemas."""
from pydantic import BaseModel
from typing import Optional


class DashboardSummary(BaseModel):
    total_projects: int = 0
    active_projects: int = 0
    task_completion_rate: float = 0
    overdue_tasks: int = 0
    pending_requirements: int = 0
    open_defects: int = 0


class ProjectProgress(BaseModel):
    project_id: int
    project_name: str
    total_tasks: int = 0
    completed_tasks: int = 0
    completion_rate: float = 0
    status: str = "active"


class RiskItem(BaseModel):
    id: int
    type: str
    title: str
    severity: str
    target_id: int
    due_date: Optional[str] = None


class TodoItem(BaseModel):
    id: int
    type: str
    title: str
    priority: str
    due_date: Optional[str] = None
    status: str
