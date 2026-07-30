"""Review model - polymorphic reviews for plans, requirements, changes, milestones."""
from datetime import datetime
from sqlalchemy import String, DateTime, Text, Enum as SQLEnum, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import enum


class ReviewStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ReviewTarget(str, enum.Enum):
    PLAN = "plan"
    REQUIREMENT = "requirement"
    CHANGE = "change"
    MILESTONE = "milestone"


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    target_type: Mapped[ReviewTarget] = mapped_column(
        SQLEnum(ReviewTarget, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    target_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    reviewer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[ReviewStatus] = mapped_column(
        SQLEnum(ReviewStatus, values_callable=lambda x: [e.value for e in x]),
        default=ReviewStatus.PENDING,
    )
    comment: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
