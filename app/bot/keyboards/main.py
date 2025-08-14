from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.bot.utils.buttons import big_label


def main_menu_keyboard(trial_available: bool, has_active: bool) -> InlineKeyboardMarkup:
	rows = []
	if trial_available and not has_active:
		rows.append([InlineKeyboardButton(text=big_label("Бесплатный день"), callback_data="start:trial")])
	rows.append([InlineKeyboardButton(text=big_label("Выбрать программу"), callback_data="start:programs")])
	if not has_active:
		rows.append([InlineKeyboardButton(text=big_label("Оплатить"), callback_data="start:pay")])
	rows.append([InlineKeyboardButton(text=big_label("Профиль"), callback_data="start:profile")])
	rows.append([InlineKeyboardButton(text=big_label("Фразы"), callback_data="start:phrases")])
	rows.append([InlineKeyboardButton(text=big_label("Помощь"), callback_data="start:help")])
	rows.append([InlineKeyboardButton(text=big_label("Условия"), callback_data="start:terms")])
	return InlineKeyboardMarkup(inline_keyboard=rows)


def levels_keyboard() -> InlineKeyboardMarkup:
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text=big_label("Начинающий"), callback_data="prog:level:beginner"),
				InlineKeyboardButton(text=big_label("Новичок"), callback_data="prog:level:novice"),
			],
			[
				InlineKeyboardButton(text=big_label("Продвинутый"), callback_data="prog:level:advanced"),
				InlineKeyboardButton(text=big_label("Профессионал"), callback_data="prog:level:pro"),
			],
		]
	)


def types_keyboard() -> InlineKeyboardMarkup:
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text=big_label("Сплит"), callback_data="prog:type:split"),
				InlineKeyboardButton(text=big_label("Дом"), callback_data="prog:type:home"),
				InlineKeyboardButton(text=big_label("Улица"), callback_data="prog:type:street"),
				InlineKeyboardButton(text=big_label("Зал"), callback_data="prog:type:gym"),
			]
		]
	)


def muscle_groups_keyboard() -> InlineKeyboardMarkup:
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text=big_label("Спина"), callback_data="prog:mg:back"),
				InlineKeyboardButton(text=big_label("Бицепс"), callback_data="prog:mg:biceps"),
			],
			[
				InlineKeyboardButton(text=big_label("Трицепс"), callback_data="prog:mg:triceps"),
				InlineKeyboardButton(text=big_label("Плечи"), callback_data="prog:mg:shoulders"),
			],
			[
				InlineKeyboardButton(text=big_label("Ноги"), callback_data="prog:mg:legs"),
				InlineKeyboardButton(text=big_label("Предплечья"), callback_data="prog:mg:forearms"),
			],
			[
				InlineKeyboardButton(text=big_label("Пресс"), callback_data="prog:mg:core"),
			]
		]
	)