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


async def evaporate_and_edit(message: Message, new_text: str, reply_markup=None) -> None:
	settings = get_settings()
	style = _STYLES.get(settings.animation_style, _STYLES["dots"])  # type: ignore[arg-type]
	frame_delay = max(0, settings.animation_frame_ms) / 1000.0
	try:
		for frame in style:
			cur = frame if frame else ""
			await message.edit_text(cur or " ")
			await asyncio.sleep(frame_delay)
	except Exception:
		pass
	await message.edit_text(new_text, reply_markup=reply_markup)