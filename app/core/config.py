from __future__ import annotations

from functools import lru_cache
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

	environment: Literal["local", "staging", "prod"] = Field(default="local", alias="ENVIRONMENT")
	telegram_bot_token: str = Field(alias="TELEGRAM_BOT_TOKEN")
	redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
	database_url: str = Field(
		default="sqlite:///./myfitnessbot.db",
		alias="DATABASE_URL",
	)
	sentry_dsn: Optional[str] = Field(default=None, alias="SENTRY_DSN")
	log_level: str = Field(default="INFO", alias="LOG_LEVEL")


@lru_cache
def get_settings() -> Settings:
	return Settings()  # type: ignore[call-arg]