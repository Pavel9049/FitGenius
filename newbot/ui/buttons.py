from __future__ import annotations


def big_label(text: str) -> str:
	PAD = "\u2002"
	core = f"  {text}  "
	target = max(24, min(52, 10 * len(text)))
	pad = max(0, target - len(core))
	left = PAD * (pad // 2)
	right = PAD * (pad - len(left))
	return (f"🟩{left}{core}{right}🟩")[:60]