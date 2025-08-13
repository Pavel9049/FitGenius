import logging
import os
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Подключаем обработчики
from handlers import start, level, workout, stars, report
dp.include_router(start.router)
dp.include_router(level.router)
dp.include_router(workout.router)
dp.include_router(stars.router)
dp.include_router(report.router)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
