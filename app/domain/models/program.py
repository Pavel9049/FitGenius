from __future__ import annotations

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


class WorkoutProgram(Base):
	__tablename__ = "workout_programs"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	level: Mapped[str] = mapped_column(String(32))  # beginner/novice/advanced/pro
	type: Mapped[str] = mapped_column(String(32))  # split/home/functional/yoga/stretching/gym
	name: Mapped[str] = mapped_column(String(100))
	description: Mapped[str | None] = mapped_column(String(500), nullable=True)


class ProgramExercise(Base):
	__tablename__ = "program_exercises"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	program_id: Mapped[int] = mapped_column(Integer, ForeignKey("workout_programs.id", ondelete="CASCADE"))
	exercise_id: Mapped[int] = mapped_column(Integer, ForeignKey("exercises.id", ondelete="CASCADE"))
	order_index: Mapped[int] = mapped_column(Integer, default=0)
	sets_desc: Mapped[str | None] = mapped_column(String(64), nullable=True)
	rest_desc: Mapped[str | None] = mapped_column(String(64), nullable=True)
	tip_text: Mapped[str | None] = mapped_column(String(200), nullable=True)