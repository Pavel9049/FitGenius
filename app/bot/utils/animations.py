import asyncio
from aiogram.types import Message


async def evaporate_and_edit(message: Message, new_text: str, reply_markup=None) -> None:
	try:
		current = message.text or ""
		# Фреймы испарения
		await message.edit_text(current + "\n…", reply_markup=None)
		await asyncio.sleep(0.08)
		await message.edit_text("▒▒▒▒▒▒▒▒▒▒", reply_markup=None)
		await asyncio.sleep(0.08)
		await message.edit_text("░░░░░░░░░░", reply_markup=None)
		await asyncio.sleep(0.08)
	except Exception:
		# Если редактирование невозможно, просто продолжим
		pass
	await message.edit_text(new_text, reply_markup=reply_markup)