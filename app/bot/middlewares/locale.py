from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from typing import Any, Callable, Awaitable, Dict

from app.bot.state.user_prefs import get_user_language


class LocaleMiddleware(BaseMiddleware):
	async def __call__(
		self,
		handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
		event: TelegramObject,
		data: Dict[str, Any],
	) -> Any:
		from_user: User | None = data.get("event_from_user")
		lang = "ru"
		if from_user:
			lang_pref = get_user_language(from_user.id)
			if lang_pref:
				lang = lang_pref
			else:
				lang = (from_user.language_code or "ru").split("-")[0]
		data["lang"] = lang
		return await handler(event, data)