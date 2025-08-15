from __future__ import annotations

import random
from functools import lru_cache
from pathlib import Path
from typing import List

_BASE = Path("/workspace/app/infra/content/phrases")
_LANG_MAP = {"ru": "ru.txt", "en": "en.txt", "es": "es.txt"}


@lru_cache(maxsize=8)
def _load_phrases(lang: str) -> List[str]:
	fname = _LANG_MAP.get(lang, _LANG_MAP["ru"])  # fallback ru
	path = _BASE / fname
	if not path.exists():
		return []
	lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
	return [l for l in lines if l]


def get_random_phrase(lang: str) -> str:
	phrases = _load_phrases(lang)
	if not phrases:
		phrases = _load_phrases("ru")
	if not phrases:
		return "Будь лучшей версией себя!"
	return random.choice(phrases)