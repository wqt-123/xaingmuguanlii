"""Audit log model for operation tracking."""
from datetime import datetime
from sqlalchemy import String, DateTime, Text, JSON, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False)  # create, update, delete, approve, etc.
    target_type: Mapped[str] = mapped_column(String(32), nullable=False)  # project, plan, task, etc.
    target_id: Mapped[int] = mapped_column(Integer, nullable=False)
    detail: Mapped[dict] = mapped_column(JSON, default=dict)
    ip: Mapped[str] = mapped_column(String(45), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
