from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import get_settings
from app.infra.db.base import Base


_settings = get_settings()

_is_sqlite = _settings.database_url.startswith("sqlite:")
_connect_args = {"check_same_thread": False} if _is_sqlite else {}

engine = create_engine(
	_settings.database_url,
	future=True,
	pool_pre_ping=True,
	connect_args=_connect_args,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
	# Import models to register metadata
	from app.domain.models import user as _  # noqa: F401
	from app.domain.models import subscription as _  # noqa: F401
	from app.domain.models import exercise as _  # noqa: F401
	from app.domain.models import program as _  # noqa: F401
	from app.domain.models import workout_log as _  # noqa: F401
	from app.domain.models import payment as _  # noqa: F401
	from app.domain.models import goal as _  # noqa: F401
	from app.domain.models import photo_report as _  # noqa: F401
	Base.metadata.create_all(bind=engine)
	# Lightweight migration for SQLite
	if _is_sqlite:
		with engine.begin() as conn:
			# add exercises.equipment
			cols = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(exercises)").fetchall()]
			if "equipment" not in cols:
				conn.execute(text("ALTER TABLE exercises ADD COLUMN equipment VARCHAR(16) DEFAULT 'gym';"))
			# add users.training_goal
			cols_u = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(users)").fetchall()]
			if "training_goal" not in cols_u:
				conn.execute(text("ALTER TABLE users ADD COLUMN training_goal VARCHAR(32);"))


@contextmanager
def get_session() -> Iterator[Session]:
	session = SessionLocal()
	try:
		yield session
	finally:
		session.close()