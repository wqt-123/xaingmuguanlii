"""Template schemas."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TemplateCreate(BaseModel):
    name: str = Field(..., max_length=128)
    type: str = Field(..., description="project, plan, requirement, defect")
    content: dict
    scope: str = "personal"


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[dict] = None
    scope: Optional[str] = None


class TemplateOut(BaseModel):
    id: int
    name: str
    type: str
    is_builtin: bool = False
    scope: str = "personal"
    content: dict
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
