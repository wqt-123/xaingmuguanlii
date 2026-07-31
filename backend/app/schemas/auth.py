"""Auth schemas."""
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=64)
    password: str = Field(..., min_length=1)


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=64)
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=1, max_length=64)
    gender: str = Field(default="", max_length=8)
    age: int = Field(default=0, ge=0, le=150)
    phone: str = Field(default="", max_length=32)
    email: str = Field(default="", max_length=128)
