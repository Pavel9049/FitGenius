from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models.user import User
from app.domain.models.subscription import Subscription


class TrialService:
	def __init__(self, session: Session) -> None:
		self.session = session

	def has_used_trial(self, user: User) -> bool:
		trial = self.session.scalar(
			select(Subscription).where(Subscription.user_id == user.id, Subscription.plan == "trial")
		)
		return trial is not None

	def grant_trial(self, user: User) -> Subscription:
		if self.has_used_trial(user):
			raise ValueError("trial_already_used")
		sub = Subscription(
			user_id=user.id,
			plan="trial",
			price_rub=0,
			expires_at=datetime.utcnow() + timedelta(days=1),
			status="active",
		)
		self.session.add(sub)
		self.session.commit()
		self.session.refresh(sub)
		return sub