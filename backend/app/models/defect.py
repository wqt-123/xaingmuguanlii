"""Defect model."""
from datetime import datetime
from sqlalchemy import String, DateTime, Text, Enum as SQLEnum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class DefectSeverity(str, enum.Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    TRIVIAL = "trivial"


class DefectPriority(str, enum.Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DefectStatus(str, enum.Enum):
    NEW = "new"
    ASSIGNED = "assigned"
    FIXING = "fixing"
    FIXED = "fixed"
    VERIFIED = "verified"
    CLOSED = "closed"
    REOPENED = "reopened"


class Defect(Base):
    __tablename__ = "defects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    title_en: Mapped[str] = mapped_column(String(512), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    repro_steps: Mapped[str] = mapped_column(Text, default="")
    severity: Mapped[DefectSeverity] = mapped_column(
        SQLEnum(DefectSeverity, values_callable=lambda x: [e.value for e in x]),
        default=DefectSeverity.MINOR,
    )
    priority: Mapped[DefectPriority] = mapped_column(
        SQLEnum(DefectPriority, values_callable=lambda x: [e.value for e in x]),
        default=DefectPriority.MEDIUM,
    )
    module: Mapped[str] = mapped_column(String(128), default="")
    found_version: Mapped[str] = mapped_column(String(32), default="")
    fix_version: Mapped[str] = mapped_column(String(32), default="")
    assignee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[DefectStatus] = mapped_column(
        SQLEnum(DefectStatus, values_callable=lambda x: [e.value for e in x]),
        default=DefectStatus.NEW,
    )
    environment: Mapped[str] = mapped_column(String(256), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="defects")
    assignee = relationship("User", back_populates="assigned_defects", foreign_keys=[assignee_id])
    attachments = relationship("DefectAttachment", back_populates="defect", cascade="all, delete-orphan")
