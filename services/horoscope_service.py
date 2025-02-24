from services.openai_service import ask_openai
from telegram.ext import CallbackContext
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_horoscope(sign: str, context: CallbackContext = None) -> str:
    """
    Асинхронно получает гороскоп через OpenAI API для указанного знака зодиака и даты.
    Если дата не указана, использует текущую дату.
    """
    # Определяем дату: берем из context.user_data, если есть, иначе текущую
    if context and context.user_data.get("selected_date"):
        horoscope_date = context.user_data.get("selected_date")
    else:
        horoscope_date = datetime.now().strftime("%d.%m.%Y")

    prompt = f"Гороскоп на {horoscope_date} для знака зодиака {sign}."
    response = await ask_openai(prompt)

    logger.info(f"Гороскоп для {sign} на {horoscope_date}: {response[:50]}...")
    return response