from services.openai_service import ask_openai
from telegram.ext import ContextTypes
from datetime import datetime
import logging
from utils.validation import sanitize_input

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_horoscope(sign: str, period: str, context: ContextTypes.DEFAULT_TYPE = None) -> str:
    """
    Асинхронно получает гороскоп через OpenAI API для указанного знака зодиака и периода.
    
    Args:
        sign: Знак зодиака
        period: Период гороскопа ('today', 'week', 'month')
        context: Контекст Telegram (опционально)
    
    Returns:
        str: Текст гороскопа
    """
    # Определяем период для текста запроса
    period_text = {
        "today": datetime.now().strftime("%d.%m.%Y"),
        "week": f"неделю с {datetime.now().strftime('%d.%m.%Y')}",
        "month": f"месяц {datetime.now().strftime('%B %Y')}"
    }.get(period, datetime.now().strftime("%d.%m.%Y"))

    prompt = (
        f"Ты — потомственный астролог, владеющий древними тайнами звёзд и планет. "
        f"Сотвори волшебное предсказание судьбы для знака {sign} на {period_text}. "
        f"Опиши, как танец планет и созвездий влияет на энергетические потоки этого знака. "
        f"Раскрой мистическую суть {period_text} через отношения с тремя сферами: любовь, успех и здоровье. "
        f"Какие тонкие вибрации вселенной окружают знак в этот период? Какие символы и знаки судьбы появятся на пути? "
        f"Какие стихии (огонь, вода, земля, воздух) наиболее благоприятны в этот период? "
        f"Заверши гороскоп загадочным пророчеством или мудрой метафорой, которая останется в сердце. "
        f"Говори красивым, поэтичным языком, наполненным мистицизмом и тайной. "
        f"Пиши на русском языке. Не используй Markdown-форматирование (например, ###, **, *, # и т.д.). "
    )
    response = await ask_openai(prompt)

    logger.info(f"Гороскоп для {sign} на {period_text}: {response[:50]}...")
    return response