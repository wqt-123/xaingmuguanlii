"""Defect schemas."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DefectCreate(BaseModel):
    project_id: int
    title: str = Field(..., min_length=1, max_length=256)
    title_en: str = Field(default="", max_length=512)
    description: str = ""
    repro_steps: str = ""
    severity: str = "minor"
    priority: str = "medium"
    module: str = ""
    found_version: str = ""
    assignee_id: Optional[int] = None
    reporter_id: int
    environment: str = ""


class DefectUpdate(BaseModel):
    title: Optional[str] = None
    title_en: Optional[str] = None
    description: Optional[str] = None
    repro_steps: Optional[str] = None
    severity: Optional[str] = None
    priority: Optional[str] = None
    module: Optional[str] = None
    fix_version: Optional[str] = None
    assignee_id: Optional[int] = None
    environment: Optional[str] = None


class DefectStatusUpdate(BaseModel):
    status: str


class DefectOut(BaseModel):
    id: int
    project_id: int
    title: str
    title_en: str = ""
    description: str = ""
    severity: str = "minor"
    priority: str = "medium"
    module: str = ""
    found_version: str = ""
    fix_version: str = ""
    assignee_id: Optional[int] = None
    reporter_id: int
    status: str = "new"
    environment: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
