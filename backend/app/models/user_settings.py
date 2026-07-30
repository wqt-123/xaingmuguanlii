"""User settings model for preferences."""
from sqlalchemy import String, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    font_size: Mapped[str] = mapped_column(String(8), default="medium")  # small, medium, large
    language: Mapped[str] = mapped_column(String(8), default="zh")  # zh, en
    notify_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
