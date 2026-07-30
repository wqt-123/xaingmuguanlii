"""Requirement schemas."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class RequirementCreate(BaseModel):
    project_id: int
    title: str = Field(..., min_length=1, max_length=256)
    title_en: str = Field(default="", max_length=512)
    description: str = ""
    source: str = "product"
    priority: str = "P2"
    estimated_effort: float = 0
    proposer_id: int
    assignee_id: Optional[int] = None
    tags: list = []
    version: str = ""


class RequirementUpdate(BaseModel):
    title: Optional[str] = None
    title_en: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
    priority: Optional[str] = None
    estimated_effort: Optional[float] = None
    assignee_id: Optional[int] = None
    status: Optional[str] = None
    tags: Optional[list] = None
    version: Optional[str] = None


class RequirementOut(BaseModel):
    id: int
    project_id: int
    title: str
    title_en: str = ""
    description: str = ""
    source: str = "product"
    priority: str = "P2"
    estimated_effort: float = 0
    proposer_id: int
    assignee_id: Optional[int] = None
    status: str = "draft"
    tags: list = []
    version: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
