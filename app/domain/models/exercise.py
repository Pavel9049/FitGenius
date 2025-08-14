from __future__ import annotations

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


class Exercise(Base):
	__tablename__ = "exercises"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	muscle_group: Mapped[str] = mapped_column(String(50), index=True)
	name: Mapped[str] = mapped_column(String(100))
	video_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
	description: Mapped[str | None] = mapped_column(String(500), nullable=True)