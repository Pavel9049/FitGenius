from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from sqlalchemy import select

from app.infra.db.session import get_session
from app.domain.models.user import User
from app.domain.models.subscription import Subscription


PAID_COMMANDS = {"start_workout", "done"}


class AccessMiddleware(BaseMiddleware):
	async def __call__(
		self,
		handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
		event: TelegramObject,
		data: Dict[str, Any],
	) -> Any:
		if isinstance(event, Message) and event.text and event.text.startswith("/"):
			cmd = event.text[1:].split()[0]
			if cmd in PAID_COMMANDS:
				with get_session() as session:
					user = session.scalar(select(User).where(User.tg_id == event.from_user.id))
					if not user:
						await event.answer("Доступ закрыт. Купите план: /plans")
						return
					active = session.scalar(
						select(Subscription).where(Subscription.user_id == user.id, Subscription.status == "active")
					)
					if not active:
						await event.answer("Доступ закрыт. Купите план: /plans")
						return
		return await handler(event, data)