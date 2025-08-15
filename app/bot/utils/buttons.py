from __future__ import annotations

# Telegram ограничивает длину текста кнопки (~64 символа). Делаем декор и паддинг безопасно.

def big_label(text: str) -> str:
	core = f"  {text}  "
	# Используем en space (U+2002) для мягкого расширения
	PAD_CHAR = "\u2002"
	target_len = max(24, min(52, 10 * len(text)))  # динамическая «крупность», но безопасно по лимиту
	pad_needed = max(0, target_len - len(core))
	left = PAD_CHAR * (pad_needed // 2)
	right = PAD_CHAR * (pad_needed - len(left))
	decorated = f"🟩{left}{core}{right}🟩"
	# Страхуемся от переполнения
	return decorated[:60]