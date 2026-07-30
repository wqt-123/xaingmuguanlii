"""Notification schemas."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NotificationOut(BaseModel):
    id: int
    user_id: int
    type: str = "info"
    title: str
    content: str = ""
    link: str = ""
    is_read: bool = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
