from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models.user import User
from app.domain.models.workout_log import WorkoutLog


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
		# Простой расчёт XP/звёзд: 50 XP и 10 звёзд, с бонусом за стрик
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