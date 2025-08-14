# MyFitnessBot

Минимальный каркас Telegram-бота на aiogram v3 + FastAPI для /health.

## Быстрый старт

1. Создайте виртуальное окружение и установите зависимости:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip setuptools wheel
pip install -e .[dev]
```

2. Установите переменные окружения (минимум):

```bash
export TELEGRAM_BOT_TOKEN="<your_token>"
```

3. Запуск бота:

```bash
python -m app.bot.main
```

4. Запуск FastAPI (health):

```bash
python -m uvicorn app.infra.web.fastapi_app:app --reload --port 8080
```

5. Тесты:

```bash
pytest
```