from services.openai_service import ask_openai
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_horoscope(sign: str) -> str:
    """
    Получает гороскоп через OpenAI API.
    """
    prompt = f"Гороскоп на сегодня для знака зодиака {sign}."
    response = ask_openai(prompt)

    logger.info(f"Гороскоп для {sign}: {response[:50]}...")
    return response
