"""Plan schemas."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PlanCreate(BaseModel):
    project_id: int
    name: str = Field(..., min_length=1, max_length=256)
    name_en: str = Field(default="", max_length=512)
    description: str = ""
    start_date: datetime
    end_date: datetime
    owner_id: int
    priority: str = "medium"


class PlanUpdate(BaseModel):
    name: Optional[str] = None
    name_en: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    owner_id: Optional[int] = None
    status: Optional[str] = None
    priority: Optional[str] = None


class PlanOut(BaseModel):
    id: int
    project_id: int
    name: str
    name_en: str = ""
    description: str = ""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    owner_id: int
    status: str = "draft"
    priority: str = "medium"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
