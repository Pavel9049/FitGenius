# -----------------------------------------------------------
# bot.py – точка входа нашего Telegram‑бота FitGenius
# -----------------------------------------------------------

import logging
import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.filters import Command
from dotenv import load_dotenv

# ---------------------------   Конфиги   ---------------------------
# Читаем переменные из .env (в Replit они будут задаваться в Secrets)
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not set! Check .env or Replit Secrets")

# ---------------------------   Логи   ---------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------   Инициализация   ---------------------------
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# ---------------------------   Роутеры (обработчики)   ---------------------------
# Каждый обработчик находится в отдельном файле в папке handlers
# Мы импортируем их и «подключаем» к диспетчеру
from handlers import start, level, workout, stars, report

dp.include_router(start.router)
dp.include_router(level.router)
dp.include_router(workout.router)
dp.include_router(stars.router)
dp.include_router(report.router)

# ---------------------------   Команда /ping (для быстрой проверки) ---------------------------
@dp.message_handler(Command("ping"))
async def cmd_ping(message: types.Message):
    await message.reply("🏓 Pong! Бот живой.")


# ---------------------------   Запуск   ---------------------------
if __name__ == "__main__":
    logger.info("Starting FitGenius bot...")
    executor.start_polling(dp, skip_updates=True)
