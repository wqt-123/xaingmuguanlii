"""Task dependency model."""
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class TaskDependency(Base):
    __tablename__ = "task_dependencies"
    __table_args__ = (
        UniqueConstraint("predecessor_id", "successor_id", name="uq_task_dep"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    predecessor_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    successor_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    dep_type: Mapped[str] = mapped_column(String(4), default="FS")  # FS, SS, FF, SF
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    predecessor = relationship("Task", back_populates="successors", foreign_keys=[predecessor_id])
    successor = relationship("Task", back_populates="predecessors", foreign_keys=[successor_id])
