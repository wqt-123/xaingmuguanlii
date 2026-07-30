"""Milestone model."""
from datetime import datetime
from sqlalchemy import String, DateTime, Text, Enum as SQLEnum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class MilestoneStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"


class Milestone(Base):
    __tablename__ = "milestones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[MilestoneStatus] = mapped_column(
        SQLEnum(MilestoneStatus, values_callable=lambda x: [e.value for e in x]),
        default=MilestoneStatus.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    plan = relationship("Plan", back_populates="milestones")
