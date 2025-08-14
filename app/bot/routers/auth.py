from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from app.bot.i18n import t

router = Router(name=__name__)


@router.message(CommandStart())
async def cmd_start(message: Message, lang: str) -> None:
	await message.answer(t("start", lang=lang))


@router.message(Command("help"))
async def cmd_help(message: Message, lang: str) -> None:
	await message.answer(t("help", lang=lang))