from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def language_keyboard() -> InlineKeyboardMarkup:
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="Русский", callback_data="lang:ru"),
				InlineKeyboardButton(text="English", callback_data="lang:en"),
				InlineKeyboardButton(text="Español", callback_data="lang:es"),
			]
		]
	)