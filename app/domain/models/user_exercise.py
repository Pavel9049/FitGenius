from __future__ import annotations

from datetime import datetime

from sqlalchemy import Integer, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


class UserExerciseProfile(Base):
	__tablename__ = "user_exercise_profiles"
	__table_args__ = (UniqueConstraint("user_id", "exercise_id", name="uq_user_exercise"),)

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
	exercise_id: Mapped[int] = mapped_column(Integer, ForeignKey("exercises.id", ondelete="CASCADE"))
	estimated_1rm: Mapped[float | None] = mapped_column(Float, nullable=True)
	last_work_weight: Mapped[float | None] = mapped_column(Float, nullable=True)
	last_reps: Mapped[int | None] = mapped_column(Integer, nullable=True)
	updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)