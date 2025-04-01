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

    prompt = (
        f"Ты — потомственный астролог, владеющий древними тайнами звёзд и планет. "
        f"Сотвори волшебное предсказание судьбы для знака {sign} на {horoscope_date}. "
        f"Опиши как танец планет и созвездий влияет на энергетические потоки этого знака. "
        f"Раскрой мистическую суть дня через отношения с тремя сферами: любовь, успех и здоровье. "
        f"Какие тонкие вибрации вселенной окружают знак сегодня? Какие символы и знаки судьбы появятся на пути? "
        f"Какие стихии (огонь, вода, земля, воздух) наиболее благоприятны сегодня? "
        f"Заверши гороскоп загадочным пророчеством или мудрой метафорой, которая останется в сердце. "
        f"Говори красивым, поэтичным языком, наполненным мистицизмом и тайной. "
        f"Пиши на русском языке. Не используй Markdown-форматирование (например, ###, **, *, # и т.д.). "
    )
    response = await ask_openai(prompt)

    logger.info(f"Гороскоп для {sign} на {horoscope_date}: {response[:50]}...")
    return response