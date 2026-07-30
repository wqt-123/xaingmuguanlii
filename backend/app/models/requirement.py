"""Requirement model."""
from datetime import datetime
from sqlalchemy import String, DateTime, Text, Enum as SQLEnum, ForeignKey, JSON, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class ReqPriority(str, enum.Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class ReqStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_DEV = "in_dev"
    DONE = "done"


class ReqSource(str, enum.Enum):
    PRODUCT = "product"
    USER_FEEDBACK = "user_feedback"
    BUSINESS = "business"
    TECH = "tech"
    OTHER = "other"


class Requirement(Base):
    __tablename__ = "requirements"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    title_en: Mapped[str] = mapped_column(String(512), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    source: Mapped[ReqSource] = mapped_column(
        SQLEnum(ReqSource, values_callable=lambda x: [e.value for e in x]),
        default=ReqSource.PRODUCT,
    )
    priority: Mapped[ReqPriority] = mapped_column(
        SQLEnum(ReqPriority, values_callable=lambda x: [e.value for e in x]),
        default=ReqPriority.P2,
    )
    estimated_effort: Mapped[float] = mapped_column(Float, default=0)
    proposer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    assignee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[ReqStatus] = mapped_column(
        SQLEnum(ReqStatus, values_callable=lambda x: [e.value for e in x]),
        default=ReqStatus.DRAFT,
    )
    tags: Mapped[dict] = mapped_column(JSON, default=list)
    version: Mapped[str] = mapped_column(String(32), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="requirements")
    assignee = relationship("User", back_populates="assigned_requirements", foreign_keys=[assignee_id])
    changes = relationship("RequirementChange", back_populates="requirement", cascade="all, delete-orphan")
