from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.domain.models.exercise import Exercise
from app.domain.models.program import WorkoutProgram, ProgramExercise

MUSCLE_GROUPS = ["back", "biceps", "triceps", "shoulders", "legs", "forearms", "core"]
LEVELS = ["beginner", "novice", "advanced", "pro"]
TYPES = ["split", "home", "street", "gym"]

EXERCISE_POOL_GYM: dict[str, list[str]] = {
	"back": [
		"Тяга верхнего блока", "Тяга горизонтального блока", "Тяга штанги в наклоне",
		"Пуловер", "Тяга Т-грифа", "Тяга гантели в наклоне", "Шраги со штангой",
		"Тяга гантелей к поясу", "Гиперэкстензия на тренажёре", "Пуллдаун узким хватом",
		"Тяга каната к груди", "Пуллдаун за голову", "Пуллдаун нейтральным хватом",
	],
	"biceps": [
		"Подъём штанги стоя", "Подъём гантелей сидя", "Молотки", "Концентрированный подъём",
		"Подъём на скамье Скотта", "Подъём EZ-штанги", "Зоттман", "Подъём гантелей на наклонной",
		"Подъём на блоке", "Кёрл в кроссовере",
	],
	"triceps": [
		"Жим узким хватом", "Французский жим", "Разгибания на блоке", "Отжимания на брусьях",
		"Разгибания с гантелью из-за головы", "Кикбэки", "Жим в Смите узким хватом", "Разгибания на канате",
	],
	"shoulders": [
		"Жим штанги стоя", "Жим гантелей сидя", "Махи в стороны", "Тяга к подбородку",
		"Арнольд-пресс", "Жим в тренажёре", "Жим гантелей стоя", "Разведение в тренажёре",
	],
	"legs": [
		"Приседания со штангой", "Жим ногами", "Разгибания ног", "Сгибания ног",
		"Румынская тяга", "Гакк-присед", "Болгарские выпады", "Подъём на носки стоя",
		"Фронтальные приседания", "Сумо-тяга",
	],
	"forearms": [
		"Сгибания запястий со штангой", "Разгибания запястий", "Фермерская прогулка", "Обратный хват штанги",
		"Роллер для предплечий", "Сжатие эспандера", "Вращение гантели", "Пронация/супинация с гантелью",
	],
	"core": [
		"Кранчи на блоке", "Подъём ног в висе", "Колесо для пресса", "Скручивания на скамье",
		"Планка с диском", "Русский твист с гантелью", "Кранчи в тренажёре", "Велосипед с утяжелением",
		"Планка на мяче", "Слайдинги коленей с полотенцем",
	],
}

EXERCISE_POOL_BW: dict[str, list[str]] = {
	"back": [
		"Подтягивания", "Гиперэкстензия", "Планка супермен", "Тяга резинки к поясу",
		"Обратные отжимания на лавке", "Гребля с резинкой", "Пуловер с резинкой", "Тяга полотенца",
		"Подтягивания обратным хватом", "Гиперэкстензия на полу",
	],
	"biceps": [
		"Сгибания с резинкой", "Зоттман с резинкой", "Изометрика сгибаний", "Сгибания молотком с резинкой",
		"Подтягивания узким хватом", "Сгибания с полотенцем", "Кёрл у стены", "Кёрл сидя без отрыва спины",
		"Сгибания с рюкзаком", "Обратные сгибания с резинкой",
	],
	"triceps": [
		"Алмазные отжимания", "Отжимания на скамье", "Разгибания с резинкой над головой", "Жим узким хватом (отжимания)",
		"Отжимания в стойке у стены", "Жим резинки вниз", "Жим с паузой (отжимания)", "Разгибания резинки обратным хватом",
	],
	"shoulders": [
		"Отжимания с подъёмом таза", "Жим резинки над головой", "Махи в стороны с резинкой", "Арнольд-пресс с резинкой",
		"Обратные махи в наклоне", "Махи вперёд с резинкой", "Отжимания у стены", "Жим бутылок водой",
	],
	"legs": [
		"Приседания", "Выпады", "Болгарские выпады", "Ягодичный мост", "Пистолетик на опоре",
		"Сумо-присед", "Скакалка", "Прыжки на месте", "Подъём на носки", "Спринты на месте",
	],
	"forearms": [
		"Сжимание эспандера", "Вис на турнике", "Скручивание полотенца", "Изометрия кисти",
		"Перекидывание бутылки", "Кручение эспандера", "Подъём на пальцы", "Пронация кисти без веса",
	],
	"core": [
		"Планка", "Боковая планка", "Скручивания", "Подъём ног лёжа", "Велосипед",
		"Русский твист", "V-up", "Hollow hold", "Dead bug", "Маунтин-клаймбер",
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
		# Gym
		for mg, names in EXERCISE_POOL_GYM.items():
			for name in names:
				ex = Exercise(muscle_group=mg, name=name, video_url=f"https://www.youtube.com/results?search_query={name}+техника+выполнения", equipment="gym")
				self.session.add(ex)
		# Bodyweight
		for mg, names in EXERCISE_POOL_BW.items():
			for name in names:
				ex = Exercise(muscle_group=mg, name=name, video_url=f"https://www.youtube.com/results?search_query={name}+техника+выполнения", equipment="bodyweight")
				self.session.add(ex)
		self.session.commit()

	def _seed_splits_for_level(self, level: str) -> None:
		# Сплиты доступны только для advanced/pro
		if level not in ("advanced", "pro"):
			return
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
		# По COUNT_BY_LEVEL упражнений на каждую группу; для home/street — только bodyweight, для gym — только gym
		for mg in MUSCLE_GROUPS:
			program = WorkoutProgram(level=level, type=t, name=f"{TYPE_RU[t]}: {LEVEL_RU[level]} — {mg}")
			self.session.add(program)
			self.session.flush()
			if t == "gym":
				pool = self.session.scalars(select(Exercise).where(Exercise.muscle_group == mg, Exercise.equipment == "gym")).all()
			else:
				pool = self.session.scalars(select(Exercise).where(Exercise.muscle_group == mg, Exercise.equipment == "bodyweight")).all()
			limit = COUNT_BY_LEVEL[level]
			for idx, ex in enumerate(pool[:limit]):
				self.session.add(ProgramExercise(program_id=program.id, exercise_id=ex.id, order_index=idx))
		self.session.commit()

	def seed_all(self) -> None:
		self._ensure_exercises()
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