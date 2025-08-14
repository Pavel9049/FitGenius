from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from sqlalchemy.orm import Session

from app.bot.i18n import t
from app.infra.db.session import get_session
from app.domain.services.workouts_service import WorkoutsService
from app.domain.services.payments_service import PaymentsService, PLANS

router = Router(name=__name__)


@router.message(Command("plans"))
async def plans(message: Message, lang: str) -> None:
	lines = ["Доступные планы:"]
	for key, meta in PLANS.items():
		lines.append(f"- {key}: {meta['price']}₽")
	lines.append("Купить: /buy <plan>")
	await message.answer("\n".join(lines))


@router.message(Command("buy"))
async def buy(message: Message, lang: str) -> None:
	parts = message.text.split()
	if len(parts) < 2:
		await message.answer("Укажите план: /buy beginner|novice|advanced|pro")
		return
	plan = parts[1]
	with get_session() as session:  # type: Session
		workout = WorkoutsService(session)
		user = workout.ensure_user(tg_id=message.from_user.id, language=lang)
		payment = PaymentsService(session)
		try:
			sub = payment.purchase(user, plan)
		except ValueError:
			await message.answer("Неизвестный план")
			return
	await message.answer(f"Оплата успешна. Доступ открыт до {sub.expires_at.date().isoformat()}.")