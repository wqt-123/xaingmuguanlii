"""Task schemas."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TaskCreate(BaseModel):
    plan_id: int
    project_id: int
    parent_id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=256)
    title_en: str = Field(default="", max_length=512)
    description: str = ""
    assignee_id: Optional[int] = None
    priority: str = "medium"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    estimated_hours: float = 0
    sort_order: int = 0
    labels: list = []


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    title_en: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    sort_order: Optional[int] = None
    labels: Optional[list] = None


class TaskStatusUpdate(BaseModel):
    status: str


class TaskMove(BaseModel):
    new_parent_id: Optional[int] = None
    new_sort_order: Optional[int] = None


class TaskOut(BaseModel):
    id: int
    plan_id: int
    project_id: int
    parent_id: Optional[int] = None
    title: str
    title_en: str = ""
    description: str = ""
    assignee_id: Optional[int] = None
    status: str = "todo"
    priority: str = "medium"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    estimated_hours: float = 0
    actual_hours: float = 0
    sort_order: int = 0
    labels: list = []
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
