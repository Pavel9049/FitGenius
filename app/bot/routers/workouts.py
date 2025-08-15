from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from sqlalchemy.orm import Session

from app.bot.i18n import t
from app.infra.db.session import get_session
from app.domain.services.workouts_service import WorkoutsService

router = Router(name=__name__)


@router.message(Command("start_workout"))
async def start_workout(message: Message, lang: str) -> None:
	await message.answer(t("workout_start", lang=lang))


@router.message(Command("done"))
async def complete_workout(message: Message, lang: str) -> None:
	with get_session() as session:  # type: Session
		service = WorkoutsService(session)
		user = service.ensure_user(tg_id=message.from_user.id, language=lang)
		log = service.complete_workout(user)
	await message.answer(t("workout_done", lang=lang, xp=log.xp_earned, stars=log.stars_earned))