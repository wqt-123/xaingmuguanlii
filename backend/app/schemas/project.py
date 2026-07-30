"""Project schemas."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ProjectCreate(BaseModel):
    key: str = Field(..., min_length=2, max_length=16)
    name: str = Field(..., min_length=1, max_length=128)
    name_en: str = Field(default="", max_length=256)
    description: str = ""
    color: str = Field(default="#FF4D2E", max_length=7)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    name_en: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ProjectOut(BaseModel):
    id: int
    key: str
    name: str
    name_en: str = ""
    description: str = ""
    color: str = "#FF4D2E"
    status: str = "active"
    owner_id: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
