"""User model and ProjectMember association."""
from datetime import datetime
from sqlalchemy import String, DateTime, Text, Enum as SQLEnum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    PM = "pm"
    MEMBER = "member"
    VIEWER = "viewer"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    name_en: Mapped[str] = mapped_column(String(128), default="")
    email: Mapped[str] = mapped_column(String(128), default="")
    phone: Mapped[str] = mapped_column(String(32), default="")
    avatar: Mapped[str] = mapped_column(String(256), default="")
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, values_callable=lambda x: [e.value for e in x]),
        default=UserRole.MEMBER,
    )
    dept: Mapped[str] = mapped_column(String(64), default="")
    title: Mapped[str] = mapped_column(String(64), default="")
    gender: Mapped[str] = mapped_column(String(8), default="")
    age: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String(16), default="active")  # active, pending, rejected
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    owned_projects = relationship("Project", back_populates="owner")
    member_of = relationship("ProjectMember", back_populates="user")
    assigned_tasks = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id")
    assigned_requirements = relationship("Requirement", back_populates="assignee", foreign_keys="Requirement.assignee_id")
    assigned_defects = relationship("Defect", back_populates="assignee", foreign_keys="Defect.assignee_id")
