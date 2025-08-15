from __future__ import annotations

from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


class Subscription(Base):
	__tablename__ = "subscriptions"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
	plan: Mapped[str] = mapped_column(String(32))  # beginner/novice/advanced/pro
	price_rub: Mapped[int] = mapped_column(Integer)
	started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
	expires_at: Mapped[datetime] = mapped_column(DateTime)
	status: Mapped[str] = mapped_column(String(16), default="active")