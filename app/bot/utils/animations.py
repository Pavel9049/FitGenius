import asyncio
import random
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
	length = len(text)
	result = []
	for i in range(frames):
		ratio = i / (frames - 1)
		cut = int(length * ratio)
		frame = text[cut:]
		result.append(frame if frame else "")
	return result


def _gen_ultra_fade_frames(text: str, frames: int, seed: int) -> list[str]:
	# Плавное растворение: на каждом шаге случайно «гасим» часть символов по всему тексту
	if frames <= 1:
		return [""]
	rnd = random.Random(seed)
	indices = list(range(len(text)))
	# Фиксируем случайный порядок «гашения» символов, чтобы кадры были стабильны
	rnd.shuffle(indices)
	frames_out: list[str] = []
	for i in range(frames):
		ratio = i / (frames - 1)
		to_hide = int(len(indices) * ratio)
		hide_set = set(indices[:to_hide])
		chars = list(text)
		for idx in hide_set:
			c = chars[idx]
			# сохраняем переводы строк, остальное заменяем узким пробелом для мягкого затухания
			if c not in ("\n", "\r"):
				chars[idx] = "\u2009"  # thin space
		frame = "".join(chars)
		frames_out.append(frame)
	return frames_out


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
		elif style_key == "ultra":
			orig = message.text or ""
			frames_total = max(6, min(settings.animation_max_frames, int(settings.animation_total_ms / max(1, settings.animation_frame_ms))))
			seed = (message.message_id or 0) ^ len(orig)
			for frame in _gen_ultra_fade_frames(orig, frames_total, seed):
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