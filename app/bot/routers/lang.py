from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from app.bot.i18n import t
from app.bot.keyboards.lang import language_keyboard
from app.bot.state.user_prefs import set_user_language

router = Router(name=__name__)


@router.message(Command("lang"))
async def cmd_lang(message: Message, lang: str) -> None:
	await message.answer(t("choose_language", lang=lang), reply_markup=language_keyboard())


@router.callback_query(F.data.startswith("lang:"))
async def cb_lang(call: CallbackQuery, lang: str) -> None:
	code = call.data.split(":", 1)[1]
	set_user_language(call.from_user.id, code)
	await call.message.edit_reply_markup(reply_markup=None)
	await call.message.answer(t("language_changed", lang=code, language=code))
	await call.answer()