from __future__ import annotations

from datetime import datetime

from sqlalchemy import Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


class WorkoutLog(Base):
	__tablename__ = "workout_logs"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
	program_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("workout_programs.id", ondelete="SET NULL"), nullable=True)
	performed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
	xp_earned: Mapped[int] = mapped_column(Integer, default=0)
	stars_earned: Mapped[int] = mapped_column(Integer, default=0)