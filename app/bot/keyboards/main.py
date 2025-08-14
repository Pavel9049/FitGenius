from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_keyboard(trial_available: bool, has_active: bool) -> InlineKeyboardMarkup:
	rows = []
	if trial_available and not has_active:
		rows.append([InlineKeyboardButton(text="Бесплатный день", callback_data="start:trial")])
	rows.append([InlineKeyboardButton(text="Выбрать программу", callback_data="start:programs")])
	if not has_active:
		rows.append([InlineKeyboardButton(text="Оплатить", callback_data="start:pay")])
	rows.append([
		InlineKeyboardButton(text="Профиль", callback_data="start:profile"),
		InlineKeyboardButton(text="Помощь", callback_data="start:help"),
	])
	return InlineKeyboardMarkup(inline_keyboard=rows)


def levels_keyboard() -> InlineKeyboardMarkup:
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="Начинающий", callback_data="prog:level:beginner"),
				InlineKeyboardButton(text="Новичок", callback_data="prog:level:novice"),
			],
			[
				InlineKeyboardButton(text="Продвинутый", callback_data="prog:level:advanced"),
				InlineKeyboardButton(text="Профессионал", callback_data="prog:level:pro"),
			],
		]
	)


def types_keyboard() -> InlineKeyboardMarkup:
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="Сплит", callback_data="prog:type:split"),
				InlineKeyboardButton(text="Дом", callback_data="prog:type:home"),
				InlineKeyboardButton(text="Улица", callback_data="prog:type:street"),
			]
		]
	)


def muscle_groups_keyboard() -> InlineKeyboardMarkup:
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="Спина", callback_data="prog:mg:back"),
				InlineKeyboardButton(text="Бицепс", callback_data="prog:mg:biceps"),
			],
			[
				InlineKeyboardButton(text="Трицепс", callback_data="prog:mg:triceps"),
				InlineKeyboardButton(text="Плечи", callback_data="prog:mg:shoulders"),
			],
			[
				InlineKeyboardButton(text="Ноги", callback_data="prog:mg:legs"),
				InlineKeyboardButton(text="Предплечья", callback_data="prog:mg:forearms"),
			],
		]
	)