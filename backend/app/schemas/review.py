"""Review schemas."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ReviewCreate(BaseModel):
    target_type: str = Field(..., description="plan, requirement, change, milestone")
    target_id: int
    reviewer_id: int
    comment: str = ""


class ReviewUpdate(BaseModel):
    status: str = Field(..., description="approved or rejected")
    comment: Optional[str] = None


class ReviewOut(BaseModel):
    id: int
    target_type: str
    target_id: int
    reviewer_id: int
    status: str = "pending"
    comment: str = ""
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
