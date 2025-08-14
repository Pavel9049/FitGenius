from __future__ import annotations

from datetime import datetime

from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db.base import Base


class PhotoReport(Base):
	__tablename__ = "photo_reports"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
	image_url: Mapped[str] = mapped_column(String(500))
	cv_label: Mapped[str | None] = mapped_column(String(100), nullable=True)
	calories: Mapped[int | None] = mapped_column(Integer, nullable=True)
	protein_g: Mapped[int | None] = mapped_column(Integer, nullable=True)
	fat_g: Mapped[int | None] = mapped_column(Integer, nullable=True)
	carbs_g: Mapped[int | None] = mapped_column(Integer, nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)