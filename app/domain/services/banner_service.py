from __future__ import annotations

import random

_SPORT_EMOJI = ["🏋️‍♂️", "🏃‍♀️", "🥇", "🔥", "💪", "🏆", "🚴", "🥊", "🧘", "⛹️"]
_SEPARATORS = ["═", "─", "━", "·", "•", "—"]


def get_header() -> str:
	icon = random.choice(_SPORT_EMOJI)
	sep = random.choice(_SEPARATORS) * 18
	title = "FitCode"
	return f"{icon} {title} {icon}\n{sep}"


def get_welcome_banner() -> str:
	# Компактный ASCII-баннер с названием
	lines = [
		"███████╗██╗████████╗ ██████╗ ██████╗ ██████╗ ███████╗",
		"██╔════╝██║╚══██╔══╝██╔════╝██╔═══██╗██╔══██╗██╔════╝",
		"█████╗  ██║   ██║   ██║     ██║   ██║██████╔╝█████╗  ",
		"██╔══╝  ██║   ██║   ██║     ██║   ██║██╔══██╗██╔══╝  ",
		"██║     ██║   ██║   ╚██████╗╚██████╔╝██║  ██║███████╗",
		"╚═╝     ╚═╝   ╚═╝    ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝",
	]
	banner = "\n".join(lines)
	return f"{banner}\nFitCode"