from __future__ import annotations

from datetime import datetime

from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


class Payment(Base):
	__tablename__ = "payments"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
	provider: Mapped[str] = mapped_column(String(32))
	amount_rub: Mapped[int] = mapped_column(Integer)
	currency: Mapped[str] = mapped_column(String(8), default="RUB")
	status: Mapped[str] = mapped_column(String(16), default="succeeded")
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
	metadata: Mapped[str | None] = mapped_column(String(500), nullable=True)