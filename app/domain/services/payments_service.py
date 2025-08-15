from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models.user import User
from app.domain.models.subscription import Subscription


PLANS = {
	"beginner": {"price": 1050},
	"novice": {"price": 1750},
	"advanced": {"price": 2750},
	"pro": {"price": 3050},
}


class PaymentsService:
	def __init__(self, session: Session) -> None:
		self.session = session

	def purchase(self, user: User, plan: str) -> Subscription:
		if plan not in PLANS:
			raise ValueError("unknown plan")
		existing = self.session.scalar(
			select(Subscription).where(Subscription.user_id == user.id, Subscription.status == "active")
		)
		if existing:
			return existing
		expires = datetime.utcnow() + timedelta(days=30)
		sub = Subscription(
			user_id=user.id,
			plan=plan,
			price_rub=PLANS[plan]["price"],
			expires_at=expires,
			status="active",
		)
		self.session.add(sub)
		self.session.commit()
		self.session.refresh(sub)
		return sub