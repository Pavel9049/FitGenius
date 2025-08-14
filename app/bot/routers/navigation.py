from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
from sqlalchemy.orm import Session

from app.bot.keyboards.main import main_menu_keyboard, levels_keyboard, types_keyboard
from app.infra.db.session import get_session
from app.domain.services.workouts_service import WorkoutsService
from app.domain.services.trial_service import TrialService
from app.domain.models.subscription import Subscription
from sqlalchemy import select

import os
from app.infra.content.loader import import_workouts_dataset, import_splits_dataset, import_levels_dataset
from app.bot.utils.animations import evaporate_and_edit
from app.domain.services.phrases_service import get_random_phrase
from app.domain.services.banner_service import get_header, get_welcome_banner, generate_banner_image
from app.core.config import get_settings

router = Router(name=__name__)


_INITIALIZED = False

def _has_active_subscription(session: Session, tg_id: int) -> bool:
	from app.domain.models.user import User
	user = session.scalar(select(User).where(User.tg_id == tg_id))
	if not user:
		return False
	active = session.scalar(select(Subscription).where(Subscription.user_id == user.id, Subscription.status == "active"))
	return active is not None


def _terms_path(lang: str) -> str:
	fname = {"ru": "terms_ru.md", "en": "terms_en.md", "es": "terms_es.md"}.get(lang, "terms_ru.md")
	return f"/workspace/app/infra/content/legal/{fname}"


@router.message(CommandStart())
async def start(message: Message, lang: str) -> None:
	global _INITIALIZED
	if not _INITIALIZED:
		with get_session() as session:
			workouts_path = "/workspace/data/workouts.json"
			splits_path = "/workspace/data/splits.json"
			levels_path = "/workspace/data/levels.json"
			if os.path.exists(workouts_path):
				import_workouts_dataset(session, workouts_path)
			if os.path.exists(splits_path):
				import_splits_dataset(session, splits_path)
			if os.path.exists(levels_path):
				import_levels_dataset(session, levels_path)
		_INITIALIZED = True
	with get_session() as session:
		workout = WorkoutsService(session)
		user = workout.ensure_user(tg_id=message.from_user.id, language=lang)
		trial_service = TrialService(session)
		trial_available = not trial_service.has_used_trial(user)
		has_active = _has_active_subscription(session, message.from_user.id)
	try:
		await message.delete()
	except Exception:
		pass
	# Пытаемся отправить фото-баннер
	photo_path = generate_banner_image()
	try:
		msg = await message.answer_photo(FSInputFile(str(photo_path)), caption=get_settings().banner_title)
	except Exception:
		banner = get_welcome_banner()
		msg = await message.answer(banner)
	header = get_header()
	await evaporate_and_edit(msg, f"{header}\nДобро пожаловать! Выберите действие ниже:", reply_markup=main_menu_keyboard(trial_available, has_active))


@router.callback_query(F.data == "start:terms")
async def cb_terms(call: CallbackQuery, lang: str) -> None:
	path = _terms_path(lang)
	try:
		text = open(path, "r", encoding="utf-8").read()
	except Exception:
		text = "Пользовательское соглашение временно недоступно."
	if len(text) > 3500:
		text = text[:3500] + "\n..."
	header = get_header()
	await evaporate_and_edit(call.message, f"{header}\n{text}")
	await call.answer()


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
	header = get_header()
	await evaporate_and_edit(call.message, f"{header}\nТриал активирован на 24 часа. Перейдите к выбору программ.")
	await call.answer()


@router.callback_query(F.data == "start:programs")
async def cb_programs(call: CallbackQuery) -> None:
	header = get_header()
	await evaporate_and_edit(call.message, f"{header}\nВыберите уровень", reply_markup=levels_keyboard())
	await call.answer()


@router.callback_query(F.data == "start:pay")
async def cb_pay(call: CallbackQuery) -> None:
	header = get_header()
	await evaporate_and_edit(call.message, f"{header}\nВыберите план в /plans или используйте кнопки оплаты в следующей версии.")
	await call.answer()


@router.callback_query(F.data == "start:profile")
async def cb_profile(call: CallbackQuery, lang: str) -> None:
	with get_session() as session:
		from app.domain.models.user import User
		user = session.scalar(select(User).where(User.tg_id == call.from_user.id))
		if not user:
			header = get_header()
			await evaporate_and_edit(call.message, f"{header}\nПрофиль не найден.")
			await call.answer()
			return
		phrase = get_random_phrase(lang)
		header = get_header()
		text = f"{header}\nВаш профиль\nXP: {user.xp}\nЗвёзды: {user.stars}\nСерия дней (streak): {user.streak}\n\n{phrase}"
	await evaporate_and_edit(call.message, text)
	await call.answer()


@router.callback_query(F.data == "start:help")
async def cb_help(call: CallbackQuery) -> None:
	header = get_header()
	await evaporate_and_edit(call.message, f"{header}\nНажмите 'Выбрать программу' для каталога. Для доступа — активируйте триал или оплатите.")
	await call.answer()


@router.callback_query(F.data == "start:phrases")
async def cb_phrases(call: CallbackQuery, lang: str) -> None:
	header = get_header()
	phrases = [get_random_phrase(lang) for _ in range(3)]
	text = f"{header}\nМотивация на сегодня:\n- {phrases[0]}\n- {phrases[1]}\n- {phrases[2]}"
	await evaporate_and_edit(call.message, text)
	await call.answer()