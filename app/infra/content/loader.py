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
	"Beginner": "beginner",
	"Novice": "novice",
	"Advanced": "advanced",
	"Professional": "pro",
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
	"back": "back",
	"biceps": "biceps",
	"triceps": "triceps",
	"shoulders": "shoulders",
	"legs": "legs",
	"forearms": "forearms",
	"core": "core",
}

BODYWEIGHT_HINTS = [
	"без веса", "отжим", "подтяг", "резин", "эспандер", "полотен", "бутыл", "турник", "прыжк", "скакал", "изометр",
	"home", "outdoor",
]


def _is_bodyweight(name: str) -> bool:
	lname = name.lower()
	return any(h in lname for h in BODYWEIGHT_HINTS)


def _equip_by_location(name: str, location: str | None) -> str:
	if not location:
		return "bodyweight" if _is_bodyweight(name) else "gym"
	l = location.strip().lower()
	if l in ("дом", "home", "улица", "outdoor"):
		return "bodyweight"
	return "gym"


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


def import_levels_dataset(session: Session, file_path: str) -> int:
	if not os.path.exists(file_path):
		return 0
	with open(file_path, "r", encoding="utf-8") as f:
		data = json.load(f)
	levels: Dict[str, Any] = data.get("levels", {})
	created = 0
	for level_name, level_payload in levels.items():
		level_key = RU_TO_LEVEL.get(level_name, None)
		if not level_key:
			continue
		# 1) Основные категории в зале
		cats = level_payload.get("training_categories", {})
		for mg_key, items in cats.items():
			mg = RU_TO_MG.get(mg_key)
			if not mg:
				continue
			program = WorkoutProgram(level=level_key, type="gym", name=f"{level_name}: {mg}")
			session.add(program)
			session.flush()
			for idx, item in enumerate(items):
				name = item.get("name", "").strip()
				video = item.get("video_url")
				equip = _equip_by_location(name, item.get("location"))
				ex = _get_or_create_exercise(session, mg=mg, name=name, video=video, equipment=equip)
				session.add(ProgramExercise(program_id=program.id, exercise_id=ex.id, order_index=idx))
			created += 1
		# 2) Дом без инвентаря
		home = level_payload.get("home_workouts_no_equipment", {})
		for mg_key, items in home.items():
			mg = RU_TO_MG.get(mg_key)
			if not mg:
				continue
			program = WorkoutProgram(level=level_key, type="home", name=f"{level_name}: {mg} (home)")
			session.add(program)
			session.flush()
			for idx, item in enumerate(items):
				name = item.get("name", "").strip()
				video = item.get("video_url")
				ex = _get_or_create_exercise(session, mg=mg, name=name, video=video, equipment="bodyweight")
				session.add(ProgramExercise(program_id=program.id, exercise_id=ex.id, order_index=idx))
			created += 1
		# 3) Улица
		outdoor = level_payload.get("outdoor_workouts", {})
		for mg_key, items in outdoor.items():
			mg = RU_TO_MG.get(mg_key)
			if not mg:
				continue
			program = WorkoutProgram(level=level_key, type="street", name=f"{level_name}: {mg} (outdoor)")
			session.add(program)
			session.flush()
			for idx, item in enumerate(items):
				name = item.get("name", "").strip()
				video = item.get("video_url")
				ex = _get_or_create_exercise(session, mg=mg, name=name, video=video, equipment="bodyweight")
				session.add(ProgramExercise(program_id=program.id, exercise_id=ex.id, order_index=idx))
			created += 1
		# Питание (сохраняем как программы типа nutrition)
		nutrition_menu = level_payload.get("nutrition_menu_pp") or level_payload.get("nutrition_programs")
		if nutrition_menu:
			program = WorkoutProgram(level=level_key, type="nutrition", name=f"{level_name}: Питание")
			session.add(program)
			session.flush()
			# Сохраняем блюда как «упражнения» с описанием
			for idx, dish in enumerate(nutrition_menu):
				name = dish.get("dish_name") or dish.get("program_name") or f"Dish {idx+1}"
				desc = dish.get("description") or "ПП-блюдо"
				ex = _get_or_create_exercise(session, mg="core", name=name, video=None, equipment="bodyweight")
				session.add(ProgramExercise(program_id=program.id, exercise_id=ex.id, order_index=idx, sets_desc=None, rest_desc=None, tip_text=desc))
		session.commit()
	return created


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