from __future__ import annotations

_user_language: dict[int, str] = {}


def get_user_language(user_id: int) -> str | None:
	return _user_language.get(user_id)


def set_user_language(user_id: int, lang: str) -> None:
	_user_language[user_id] = lang