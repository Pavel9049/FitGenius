from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.domain.models.exercise import Exercise
from app.domain.models.program import WorkoutProgram, ProgramExercise

RU_TO_LEVEL = {
	"Начинающий": "beginner",
	"Новичок": "novice",
	"Продвинутый": "advanced",
	"Профессионал": "pro",
}

RU_TO_MG = {
	"Спина": "back",
	"Бицепс": "biceps",
	"Трицепс": "triceps",
	"Плечи": "shoulders",
	"Ноги": "legs",
	"Предплечья": "forearms",
	"Пресс": "core",
	"Кор": "core",
	"Кор/Пресс": "core",
}

BODYWEIGHT_HINTS = [
	"без веса", "отжим", "подтяг", "резин", "эспандер", "полотен", "бутыл", "турник", "прыжк", "скакал", "изометр",
]


def _is_bodyweight(name: str) -> bool:
	lname = name.lower()
	return any(h in lname for h in BODYWEIGHT_HINTS)


def _equip_by_location(name: str, location: str | None) -> str:
	if location and location.strip().lower() in ("дом", "улица"):
		return "bodyweight"
	return "gym" if not _is_bodyweight(name) else "bodyweight"


def _get_or_create_exercise(session: Session, mg: str, name: str, video: str | None, equipment: str) -> Exercise:
	ex = session.scalar(select(Exercise).where(Exercise.muscle_group == mg, Exercise.name == name))
	if ex:
		if video:
			ex.video_url = video
		ex.equipment = equipment
		return ex
	ex = Exercise(muscle_group=mg, name=name, video_url=video or None, equipment=equipment)
	session.add(ex)
	session.flush()
	return ex


def import_workouts_dataset(session: Session, file_path: str) -> int:
	if not os.path.exists(file_path):
		return 0
	with open(file_path, "r", encoding="utf-8") as f:
		data = json.load(f)
	created_programs = 0
	for ru_level, groups_or_days in data.items():
		level = RU_TO_LEVEL.get(ru_level)
		if not level:
			continue
		if not isinstance(groups_or_days, dict):
			continue
		for ru_group, exercises in groups_or_days.items():
			mg = RU_TO_MG.get(ru_group)
			if not mg or not isinstance(exercises, list):
				continue
			bw_votes = sum(1 for item in exercises if _equip_by_location(item.get("name", ""), item.get("location").strip() if item.get("location") else None) == "bodyweight")
			type_ = "home" if bw_votes >= len(exercises) / 2 else "gym"
			for t in ([type_] if type_ == "gym" else ["home", "street"]):
				program = WorkoutProgram(level=level, type=t, name=f"{ru_level}: {ru_group}")
				session.add(program)
				session.flush()
				for idx, item in enumerate(exercises):
					name = item.get("name", "").strip()
					sets_desc = item.get("sets")
					rest_desc = item.get("rest")
					video = item.get("video")
					location = item.get("location")
					tip = item.get("tip")
					equip = _equip_by_location(name, location)
					ex = _get_or_create_exercise(session, mg=mg, name=name, video=video, equipment=equip)
					session.add(ProgramExercise(program_id=program.id, exercise_id=ex.id, order_index=idx, sets_desc=sets_desc, rest_desc=rest_desc, tip_text=tip))
				created_programs += 1
	session.commit()
	return created_programs


def import_splits_dataset(session: Session, file_path: str) -> int:
	if not os.path.exists(file_path):
		return 0
	with open(file_path, "r", encoding="utf-8") as f:
		data = json.load(f)
	created = 0
	for ru_level, splits in data.items():
		level = RU_TO_LEVEL.get(ru_level)
		if not level:
			continue
		for split_name, split_groups in splits.items():
			program = WorkoutProgram(level=level, type="split", name=f"{split_name} — {ru_level}")
			session.add(program)
			session.flush()
			order = 0
			for ru_group, exercises in split_groups.items():
				mg = RU_TO_MG.get(ru_group)
				if not mg:
					continue
				for item in exercises:
					name = item.get("name", "").strip()
					sets_desc = item.get("sets")
					rest_desc = item.get("rest")
					video = item.get("video")
					location = item.get("location")
					tip = item.get("tip")
					equip = _equip_by_location(name, location)
					ex = _get_or_create_exercise(session, mg=mg, name=name, video=video, equipment=equip)
					session.add(ProgramExercise(program_id=program.id, exercise_id=ex.id, order_index=order, sets_desc=sets_desc, rest_desc=rest_desc, tip_text=tip))
					order += 1
			created += 1
	session.commit()
	return created