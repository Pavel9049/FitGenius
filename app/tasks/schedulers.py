from __future__ import annotations

from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.infra.db.session import get_session
from app.domain.services.catalog_service import CatalogService
from app.domain.models.exercise import Exercise


def _refresh_video_links(session: Session) -> None:
	# Обновляем видео-ссылки (перегенерируем поисковую ссылку, чтобы попадать на актуальные ролики)
	exs = session.scalars(select(Exercise)).all()
	for ex in exs:
		ex.video_url = f"https://www.youtube.com/results?search_query={ex.name}+техника+выполнения"
	session.commit()


async def weekly_refresh_catalog() -> None:
	with get_session() as session:
		catalog = CatalogService(session)
		# Очистку существующих программ опустим на MVP; можно добавить пересборку в следующей итерации
		_refresh_video_links(session)


def setup_scheduler(scheduler: AsyncIOScheduler) -> None:
	# Каждое воскресенье в 03:00 по UTC
	trigger = CronTrigger(day_of_week="sun", hour=3, minute=0)
	scheduler.add_job(weekly_refresh_catalog, trigger=trigger, id="weekly_refresh_catalog", replace_existing=True)