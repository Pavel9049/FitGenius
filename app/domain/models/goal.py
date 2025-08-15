from __future__ import annotations

from datetime import datetime

from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


class Goal(Base):
	__tablename__ = "goals"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
	title: Mapped[str] = mapped_column(String(200))
	due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
	is_completed: Mapped[bool] = mapped_column(Integer, default=0)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)