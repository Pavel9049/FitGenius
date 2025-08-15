from __future__ import annotations

import random

SPORT = ["🏋️‍♂️","🏃‍♀️","🥇","🔥","💪","🏆","🚴","🥊","🧘","⛹️"]
SEP = ["═","─","━","·","•","—"]

def header() -> str:
	return f"{random.choice(SPORT)} Fit‑Pro {random.choice(SPORT)}\n{random.choice(SEP)*18}"