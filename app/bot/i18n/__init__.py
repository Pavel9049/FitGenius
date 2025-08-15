import json
from typing import Any
from importlib import resources

_LANG_FALLBACK = "ru"
_SUPPORTED = ("ru", "en", "es")

_messages: dict[str, dict[str, str]] = {}


def _load_messages() -> None:
	global _messages
	for code in _SUPPORTED:
		with resources.files(__package__).joinpath(f"{code}.json").open("r", encoding="utf-8") as f:
			_messages[code] = json.load(f)


_load_messages()


def t(key: str, lang: str | None = None, **kwargs: Any) -> str:
	code = (lang or _LANG_FALLBACK).lower()
	if code not in _SUPPORTED:
		code = _LANG_FALLBACK
	text = _messages.get(code, {}).get(key) or _messages[_LANG_FALLBACK].get(key) or key
	if kwargs:
		try:
			return text.format(**kwargs)
		except Exception:
			return text
	return text