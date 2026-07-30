"""User schemas."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    username: str = Field(..., max_length=64)
    name: str = Field(..., max_length=64)
    name_en: str = Field(default="", max_length=128)
    email: str = Field(default="", max_length=128)
    phone: str = Field(default="", max_length=32)
    role: str = "member"
    dept: str = Field(default="", max_length=64)
    title: str = Field(default="", max_length=64)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)


class UserUpdate(BaseModel):
    name: Optional[str] = None
    name_en: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    dept: Optional[str] = None
    title: Optional[str] = None


class UserOut(UserBase):
    id: int
    avatar: str = ""
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
