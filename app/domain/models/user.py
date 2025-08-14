from __future__ import annotations

from datetime import datetime

from sqlalchemy import String, Integer, BigInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


class User(Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
	email: Mapped[str | None] = mapped_column(String(255), nullable=True)
	phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
	language: Mapped[str] = mapped_column(String(5), default="ru")
	xp: Mapped[int] = mapped_column(Integer, default=0)
	stars: Mapped[int] = mapped_column(Integer, default=0)
	streak: Mapped[int] = mapped_column(Integer, default=0)
	last_workout_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)