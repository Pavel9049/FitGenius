from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

router = Router(name=__name__)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
	await message.answer(
		"Привет! Я MyFitnessBot. Выбери язык и начнём. Команды: /help"
	)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
	await message.answer(
		"Доступные команды:\n/start — начало\n/help — помощь"
	)