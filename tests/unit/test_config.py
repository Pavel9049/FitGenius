import os

from app.core.config import get_settings


def test_settings_loads_from_env(monkeypatch):
	monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "TEST_TOKEN")
	settings = get_settings()
	assert settings.telegram_bot_token == "TEST_TOKEN"