import asyncio
from aiogram.types import Message
from app.core.config import get_settings


_STYLES = {
	"dots": ["…", "..", ".", ""],
	"blocks": ["██████████", "▓▓▓▓▓▓▓▓▓▓", "▒▒▒▒▒▒▒▒▒▒", "░░░░░░░░░░", ""],
	"dissolve": ["…", "· · ·", "·  ·  ·", " ", ""],
	"wipe": ["──────────", "───────", "────", "──", "",],
	"blink": [" ", "…", " ", "…", ""],
	"none": [""],
}


def _gen_fade_frames(text: str, frames: int) -> list[str]:
	if frames <= 1:
		return [""]
	# заменяем часть символов на пробелы шагами
	length = len(text)
	result = []
	for i in range(frames):
		ratio = i / (frames - 1)
		cut = int(length * ratio)
		frame = text[cut:]
		result.append(frame if frame else "")
	return result


async def evaporate_and_edit(message: Message, new_text: str, reply_markup=None) -> None:
	settings = get_settings()
	style_key = settings.animation_style
	frame_delay = max(0, settings.animation_frame_ms) / 1000.0
	try:
		await message.edit_reply_markup(reply_markup=None)
	except Exception:
		pass
	try:
		if style_key == "fade":
			orig = message.text or ""
			frames_total = max(3, min(settings.animation_max_frames, int(settings.animation_total_ms / max(1, settings.animation_frame_ms))))
			for frame in _gen_fade_frames(orig, frames_total):
				await message.edit_text(frame or " ", reply_markup=None)
				await asyncio.sleep(frame_delay)
		else:
			style = _STYLES.get(style_key, _STYLES["dots"])  # type: ignore[arg-type]
			for frame in style:
				await message.edit_text((frame or " "), reply_markup=None)
				await asyncio.sleep(frame_delay)
	except Exception:
		pass
	await message.edit_text(new_text, reply_markup=reply_markup)