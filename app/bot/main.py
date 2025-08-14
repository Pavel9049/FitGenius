import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.core.config import get_settings
from app.bot.routers import auth as auth_router
from app.bot.routers import lang as lang_router
from app.bot.routers import workouts as workouts_router
from app.bot.routers import payments as payments_router
from app.bot.routers import navigation as nav_router
from app.bot.routers import programs as programs_router
from app.bot.middlewares.locale import LocaleMiddleware
from app.bot.middlewares.access import AccessMiddleware
from app.infra.db.session import init_db


async def main() -> None:
	settings = get_settings()
	logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
	init_db()
	bot = Bot(
		token=settings.telegram_bot_token,
		default=DefaultBotProperties(parse_mode=ParseMode.HTML),
	)
	dp = Dispatcher()
	dp.message.middleware(LocaleMiddleware())
	dp.callback_query.middleware(LocaleMiddleware())
	dp.message.middleware(AccessMiddleware())
	dp.include_router(nav_router.router)
	dp.include_router(lang_router.router)
	dp.include_router(payments_router.router)
	dp.include_router(workouts_router.router)
	dp.include_router(auth_router.router)
	dp.include_router(programs_router.router)
	await dp.start_polling(bot)


if __name__ == "__main__":
	asyncio.run(main())