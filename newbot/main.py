from __future__ import annotations

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from newbot.routers import main_menu


async def main() -> None:
	token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
	if not token:
		raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
	logging.basicConfig(level=logging.INFO)
	bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
	try:
		await bot.delete_webhook(drop_pending_updates=True)
	except Exception:
		pass
	dp = Dispatcher()
	dp.include_router(main_menu.router)
	logging.info("NewBot Fit‑Pro starting polling")
	await dp.start_polling(bot)


if __name__ == "__main__":
	asyncio.run(main())