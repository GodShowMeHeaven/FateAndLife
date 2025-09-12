import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Токен Telegram бота
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "default_token")
if TELEGRAM_TOKEN == "default_token":
    raise ValueError("TELEGRAM_TOKEN не указан в .env файле")

# API ключ для OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY не указан в .env файле")

# Путь к базе данных
DB_PATH = os.getenv("DB_PATH", "bot_data.db")
if not os.path.exists(os.path.dirname(DB_PATH)) and DB_PATH != "bot_data.db":
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Дополнительные настройки
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")