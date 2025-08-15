from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from .utils import header
from newbot.ui.buttons import big_label

router = Router(name=__name__)


def kb_main() -> InlineKeyboardMarkup:
	rows = [
		[InlineKeyboardButton(text=big_label("Бесплатный день"), callback_data="trial:start")],
		[InlineKeyboardButton(text=big_label("Выбрать программу"), callback_data="nav:programs")],
		[InlineKeyboardButton(text=big_label("Профиль"), callback_data="nav:profile")],
		[InlineKeyboardButton(text=big_label("Фразы"), callback_data="nav:phrases")],
	]
	return InlineKeyboardMarkup(inline_keyboard=rows)


@router.message(CommandStart())
async def cmd_start(m: Message) -> None:
	await m.answer(header() + "\nДобро пожаловать в Fit‑Pro!", reply_markup=kb_main())


@router.callback_query(F.data == "nav:phrases")
async def cb_phrases(call: CallbackQuery) -> None:
	await call.message.edit_text(header() + "\n- Никогда не сдавайся\n- Сегодня лучше, чем вчера\n- Делай шаг вперёд")
	await call.answer()