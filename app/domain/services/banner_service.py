from __future__ import annotations

import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from app.core.config import get_settings

_SPORT_EMOJI = ["🏋️‍♂️", "🏃‍♀️", "🥇", "🔥", "💪", "🏆", "🚴", "🥊", "🧘", "⛹️"]
_SEPARATORS = ["═", "─", "━", "·", "•", "—"]
_ASSETS = Path("/workspace/app/infra/content/assets")
_ASSETS.mkdir(parents=True, exist_ok=True)


def get_header() -> str:
	icon = random.choice(_SPORT_EMOJI)
	sep = random.choice(_SEPARATORS) * 18
	title = get_settings().banner_title
	return f"{icon} {title} {icon}\n{sep}"


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
	# Попробуем системный шрифт; если нет — базовый
	for name in ["DejaVuSans-Bold.ttf", "Arial.ttf", "LiberationSans-Bold.ttf"]:
		p = Path("/usr/share/fonts").rglob(name)
		for f in p:
			try:
				return ImageFont.truetype(str(f), size=size)
			except Exception:
				continue
	return ImageFont.load_default()


def generate_banner_image() -> Path:
	outfile = _ASSETS / "fitcode_banner.png"
	if outfile.exists():
		return outfile
	w, h = 1200, 400
	img = Image.new("RGB", (w, h), (10, 10, 14))
	draw = ImageDraw.Draw(img)
	# Градиент
	for y in range(h):
		r = int(10 + 20 * y / h)
		g = int(10 + 10 * y / h)
		b = int(30 + 70 * y / h)
		draw.line([(0, y), (w, y)], fill=(r, g, b))
	# Лого круг/гантель
	cx, cy = 120, h // 2
	draw.ellipse((cx - 60, cy - 60, cx + 60, cy + 60), fill=(255, 120, 0))
	draw.rectangle((cx + 70, cy - 10, cx + 170, cy + 10), fill=(240, 240, 240))
	draw.rectangle((cx + 60, cy - 30, cx + 80, cy + 30), fill=(240, 240, 240))
	draw.rectangle((cx + 160, cy - 30, cx + 180, cy + 30), fill=(240, 240, 240))
	# Текст
	font_big = _load_font(80)
	font_small = _load_font(28)
	title = get_settings().banner_title
	sub = "Fitness • Workouts • Nutrition"
	draw.text((260, cy - 40), title, font=font_big, fill=(255, 255, 255))
	draw.text((260, cy + 40), sub, font=font_small, fill=(230, 230, 230))
	img = img.filter(ImageFilter.SMOOTH)
	img.save(outfile, format="PNG")
	return outfile


def get_welcome_banner() -> str:
	# Оставляем текстовый баннер как fallback
	lines = [
		"███████╗██╗████████╗ ██████╗ ██████╗ ██████╗ ███████╗",
		"██╔════╝██║╚══██╔══╝██╔════╝██╔═══██╗██╔══██╗██╔════╝",
		"█████╗  ██║   ██║   ██║     ██║   ██║██████╔╝█████╗  ",
		"██╔══╝  ██║   ██║   ██║     ██║   ██║██╔══██╗██╔══╝  ",
		"██║     ██║   ██║   ╚██████╗╚██████╔╝██║  ██║███████╗",
		"╚═╝     ╚═╝   ╚═╝    ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝",
	]
	banner = "\n".join(lines)
	return f"{banner}\n{get_settings().banner_title}"