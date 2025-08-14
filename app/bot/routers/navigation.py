from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from sqlalchemy.orm import Session

from app.bot.keyboards.main import main_menu_keyboard, levels_keyboard, types_keyboard
from app.infra.db.session import get_session
from app.domain.services.workouts_service import WorkoutsService
from app.domain.services.trial_service import TrialService
from app.domain.models.subscription import Subscription
from sqlalchemy import select

router = Router(name=__name__)


def _has_active_subscription(session: Session, tg_id: int) -> bool:
	from app.domain.models.user import User
	user = session.scalar(select(User).where(User.tg_id == tg_id))
	if not user:
		return False
	active = session.scalar(select(Subscription).where(Subscription.user_id == user.id, Subscription.status == "active"))
	return active is not None


@router.message(CommandStart())
async def start(message: Message, lang: str) -> None:
	with get_session() as session:
		workout = WorkoutsService(session)
		user = workout.ensure_user(tg_id=message.from_user.id, language=lang)
		trial_service = TrialService(session)
		trial_available = not trial_service.has_used_trial(user)
		has_active = _has_active_subscription(session, message.from_user.id)
	await message.answer(
		"Добро пожаловать! Выберите действие ниже:",
		reply_markup=main_menu_keyboard(trial_available, has_active),
	)


@router.callback_query(F.data == "start:trial")
async def cb_trial(call: CallbackQuery, lang: str) -> None:
	with get_session() as session:
		workout = WorkoutsService(session)
		user = workout.ensure_user(tg_id=call.from_user.id, language=lang)
		trial_service = TrialService(session)
		try:
			trial_service.grant_trial(user)
		except ValueError:
			await call.answer("Триал уже использован", show_alert=True)
			return
	await call.message.edit_text("Триал активирован на 24 часа. Перейдите к выбору программ.")
	await call.message.edit_reply_markup(reply_markup=None)
	await call.answer()


@router.callback_query(F.data == "start:programs")
async def cb_programs(call: CallbackQuery) -> None:
	await call.message.edit_text("Выберите уровень")
	await call.message.edit_reply_markup(reply_markup=levels_keyboard())
	await call.answer()


@router.callback_query(F.data == "start:pay")
async def cb_pay(call: CallbackQuery) -> None:
	await call.message.edit_text("Выберите план в /plans или используйте кнопки оплаты в следующей версии.")
	await call.message.edit_reply_markup(reply_markup=None)
	await call.answer()


@router.callback_query(F.data == "start:profile")
async def cb_profile(call: CallbackQuery) -> None:
	await call.message.edit_text("Профиль и прогресс появятся здесь.")
	await call.message.edit_reply_markup(reply_markup=None)
	await call.answer()


@router.callback_query(F.data == "start:help")
async def cb_help(call: CallbackQuery) -> None:
	await call.message.edit_text("Нажмите 'Выбрать программу' для каталога. Для доступа — активируйте триал или оплатите.")
	await call.message.edit_reply_markup(reply_markup=None)
	await call.answer()