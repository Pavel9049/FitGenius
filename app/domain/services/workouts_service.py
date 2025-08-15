from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models.user import User
from app.domain.models.workout_log import WorkoutLog
from app.domain.models.user_exercise import UserExerciseProfile


_GOAL_MOD = {
	"Похудеть": 0.85,
	"Сушка": 0.9,
	"Поддерживать форму": 1.0,
	"Набор массы": 1.05,
}

_DIFF_MOD = {
	"Лёгкая": 0.85,
	"Средняя": 1.0,
	"Сложная": 1.1,
}


class WorkoutsService:
	def __init__(self, session: Session) -> None:
		self.session = session

	def ensure_user(self, tg_id: int, language: str) -> User:
		user = self.session.scalar(select(User).where(User.tg_id == tg_id))
		if not user:
			user = User(tg_id=tg_id, language=language)
			self.session.add(user)
			self.session.commit()
			self.session.refresh(user)
		return user

	def complete_workout(self, user: User) -> WorkoutLog:
		now = datetime.utcnow()
		bonus = 0
		if user.last_workout_at and (now.date() - user.last_workout_at.date()) == timedelta(days=1):
			user.streak += 1
			bonus = min(user.streak, 10)
		else:
			user.streak = 1
		xp = 50 + 5 * bonus
		stars = 10 + bonus

		user.xp += xp
		user.stars += stars
		user.last_workout_at = now

		log = WorkoutLog(user_id=user.id, xp_earned=xp, stars_earned=stars)
		self.session.add(log)
		self.session.commit()
		self.session.refresh(log)
		return log

	def suggest_weight(self, user: User, exercise_id: int, difficulty: str, goal: str) -> float | None:
		profile = self.session.scalar(
			select(UserExerciseProfile).where(UserExerciseProfile.user_id == user.id, UserExerciseProfile.exercise_id == exercise_id)
		)
		base = None
		if profile and profile.estimated_1rm:
			base = 0.7 * profile.estimated_1rm
		elif profile and profile.last_work_weight:
			base = profile.last_work_weight
		else:
			# нет данных — вернём None (в UI покажем ориентиры РПЕ)
			return None
		g = _GOAL_MOD.get(goal, 1.0)
		d = _DIFF_MOD.get(difficulty, 1.0)
		weight = max(0.0, round(base * g * d, 1))
		return weight

	def update_user_exercise(self, user: User, exercise_id: int, last_weight: float, last_reps: int, estimated_1rm: float | None = None) -> None:
		profile = self.session.scalar(
			select(UserExerciseProfile).where(UserExerciseProfile.user_id == user.id, UserExerciseProfile.exercise_id == exercise_id)
		)
		if not profile:
			profile = UserExerciseProfile(user_id=user.id, exercise_id=exercise_id)
			self.session.add(profile)
		profile.last_work_weight = last_weight
		profile.last_reps = last_reps
		if estimated_1rm:
			profile.estimated_1rm = estimated_1rm
		profile.updated_at = datetime.utcnow()
		self.session.commit()