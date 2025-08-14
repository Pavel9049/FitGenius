from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.domain.models.exercise import Exercise
from app.domain.models.program import WorkoutProgram, ProgramExercise

MUSCLE_GROUPS = ["back", "biceps", "triceps", "shoulders", "legs", "forearms"]
LEVELS = ["beginner", "novice", "advanced", "pro"]
TYPES = ["split", "home", "street", "gym"]

EXERCISE_POOL: dict[str, list[str]] = {
	"back": [
		"Тяга верхнего блока", "Тяга горизонтального блока", "Подтягивания", "Тяга штанги в наклоне",
		"Пуловер", "Тяга Т-грифа", "Тяга гантели в наклоне", "Шраги со штангой",
		"Тяга гантелей к поясу", "Гиперэкстензия на тренажёре", "Пуллдаун узким хватом",
		"Тяга каната к груди", "Подтягивания обратным хватом", "Пуллдаун за голову", "Пуллдаун нейтральным хватом",
	],
	"biceps": [
		"Подъём штанги стоя", "Подъём гантелей сидя", "Молотки", "Концентрированный подъём",
		"Подъём на скамье Скотта", "Подъём EZ-штанги", "Зоттман", "Подъём гантелей на наклонной",
		"Подъём на блоке", "Обратные сгибания", "Подъём штанги сидя", "Молотки на наклонной",
		"Подъём на верёвке", "Кёрл в кроссовере", "Подъём гантелей по очереди",
	],
	"triceps": [
		"Жим узким хватом", "Французский жим", "Разгибания на блоке", "Отжимания на брусьях",
		"Разгибания с гантелью из-за головы", "Кикбэки", "Алмазные отжимания", "Жим гантелей лёжа",
		"Жим в Смите узким хватом", "Разгибания на канате", "Отжимания узким хватом",
		"Разгибания обратным хватом", "Жим Т-грифа узким хватом", "Жим в машине узким хватом", "Жим с паузой узким хватом",
	],
	"shoulders": [
		"Жим штанги стоя", "Жим гантелей сидя", "Махи в стороны", "Тяга к подбородку",
		"Обратные махи", "Махи вперёд", "Арнольд-пресс", "Жим в тренажёре",
		"Подъём гантелей через стороны наклонившись", "Жим гантелей стоя", "Разведение в тренажёре",
		"Жим штанги из-за головы", "Подъём штанги перед собой", "Махи в кроссовере", "ЙТВ-расводки",
	],
	"legs": [
		"Приседания со штангой", "Выпады", "Жим ногами", "Разгибания ног", "Сгибания ног",
		"Румынская тяга", "Гакк-присед", "Болгарские выпады", "Подъём на носки стоя", "Гиперэкстензия",
		"Фронтальные приседания", "Сумо-тяга", "Пистолетик", "Ягодичный мост", "Спринты на дорожке",
	],
	"forearms": [
		"Сгибания запястий со штангой", "Разгибания запястий", "Фермерская прогулка", "Подъём на пальцы",
		"Сгибания с гантелями сидя", "Скручивание полотенца", "Обратный хват штанги", "Вис на турнике",
		"Молотки обратным хватом", "Катание штанги о пальцы", "Роллер для предплечий", "Сжатие эспандера",
		"Сгибания с эспандером", "Вращение гантели", "Пронация/супинация с гантелью",
	],
}

LEVEL_RU = {
	"beginner": "Начинающий",
	"novice": "Новичок",
	"advanced": "Продвинутый",
	"pro": "Профессионал",
}

TYPE_RU = {
	"split": "Сплит",
	"home": "Дом",
	"street": "Улица",
	"gym": "Зал",
}

COUNT_BY_LEVEL = {"beginner": 5, "novice": 7, "advanced": 10, "pro": 15}


@dataclass
class ProgramView:
	program: WorkoutProgram
	exercises: list[Exercise]


class CatalogService:
	def __init__(self, session: Session) -> None:
		self.session = session

	def _ensure_exercises(self) -> None:
		count = self.session.scalar(select(func.count()).select_from(Exercise))
		if count and count > 0:
			return
		for mg, names in EXERCISE_POOL.items():
			for name in names:
				ex = Exercise(muscle_group=mg, name=name, video_url=f"https://www.youtube.com/results?search_query={name}+техника+выполнения")
				self.session.add(ex)
		self.session.commit()

	def _seed_splits_for_level(self, level: str) -> None:
		# 5 сплит-программ, по 3 упражнения на каждую группу; без повторений между сплитами
		mg_used: dict[str, set[int]] = {mg: set() for mg in MUSCLE_GROUPS}
		for idx in range(1, 6):
			program = WorkoutProgram(level=level, type="split", name=f"{TYPE_RU['split']} {idx} — {LEVEL_RU[level]}")
			self.session.add(program)
			self.session.flush()
			for mg in MUSCLE_GROUPS:
				pool = self.session.scalars(select(Exercise).where(Exercise.muscle_group == mg)).all()
				selected = 0
				for ex in pool:
					if ex.id in mg_used[mg]:
						continue
					self.session.add(ProgramExercise(program_id=program.id, exercise_id=ex.id, order_index=selected))
					mg_used[mg].add(ex.id)
					selected += 1
					if selected >= 3:
						break
		self.session.commit()

	def _seed_block_for_level_and_type(self, level: str, t: str) -> None:
		# По COUNT_BY_LEVEL упражнений на каждую группу
		for mg in MUSCLE_GROUPS:
			program = WorkoutProgram(level=level, type=t, name=f"{TYPE_RU[t]}: {LEVEL_RU[level]} — {mg}")
			self.session.add(program)
			self.session.flush()
			pool = self.session.scalars(select(Exercise).where(Exercise.muscle_group == mg)).all()
			limit = COUNT_BY_LEVEL[level]
			for idx, ex in enumerate(pool[:limit]):
				self.session.add(ProgramExercise(program_id=program.id, exercise_id=ex.id, order_index=idx))
		self.session.commit()

	def seed_all(self) -> None:
		self._ensure_exercises()
		# Если уже есть программы — не пересоздаём
		count = self.session.scalar(select(func.count()).select_from(WorkoutProgram))
		if count and count > 0:
			return
		for level in LEVELS:
			self._seed_splits_for_level(level)
			for t in ("home", "street", "gym"):
				self._seed_block_for_level_and_type(level, t)

	def list_programs(self, level: str, type_: str, muscle_group: str | None = None) -> list[ProgramView]:
		q = select(WorkoutProgram).where(WorkoutProgram.level == level, WorkoutProgram.type == type_)
		programs = self.session.scalars(q).all()
		views: list[ProgramView] = []
		for p in programs:
			pe = self.session.scalars(select(ProgramExercise).where(ProgramExercise.program_id == p.id).order_by(ProgramExercise.order_index)).all()
			ex_ids = [x.exercise_id for x in pe]
			exs = self.session.scalars(select(Exercise).where(Exercise.id.in_(ex_ids))).all()
			if muscle_group:
				exs = [e for e in exs if e.muscle_group == muscle_group]
			views.append(ProgramView(program=p, exercises=exs))
		return views