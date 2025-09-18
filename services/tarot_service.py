import random
import re
from openai import OpenAI
from services.openai_service import ask_openai
import config
import logging
import asyncio

logger = logging.getLogger(__name__)

client = OpenAI(api_key=config.OPENAI_API_KEY)

tarot_cards = [
    "Шут", "Маг", "Верховная Жрица", "Императрица", "Император",
    "Иерофант", "Влюбленные", "Колесница", "Справедливость", "Отшельник",
    "Колесо Фортуны", "Сила", "Повешенный", "Смерть", "Умеренность",
    "Дьявол", "Башня", "Звезда", "Луна", "Солнце", "Суд", "Мир"
]

async def get_tarot_interpretation():
    card = random.choice(tarot_cards)
    prompt = (
        f"Ты — древний мистик карт Таро. В свете свечей твои руки касаются колоды, и силы указывают на карту: {card}. "
        f"Раскрой глубинный смысл в четырёх сферах: "
        f"🌟 Судьба — какие нити Мойр сплетаются? Какие знаки и кармические уроки несёт карта? "
        f"Добавь пророческое видение будущего. "
        f"🌟 Любовь — как энергии влияют на сердечную чакру и связи? Какие желания пробуждаются? "
        f"🌟 Власть и Успех — какие врата открываются для роста? Какие таланты дремлют в подсознании? "
        f"🌟 Дух — какие энергоцентры активируются? Какие практики усилят связь с высшими силами? "
        f"Для каждой сферы дай мистический совет как древнее пророчество. "
        f"🔮 В завершение раскрой эзотерические тайны карты — связь с планетами, стихиями, "
        f"кристаллами, маслами, лунными фазами. Упомяни священные символы и руны. "
        f"Используй эмодзи: 🌟 перед сферами, 💡 перед советами, 🔮 перед эзотерикой. "
        f"Пиши поэтично, образно, как древние пророчества. "
        f"Не используй Markdown-форматирование (например, ###, **, *, # и т.д.)."
        f"ОБЯЗАТЕЛЬНО УЛОЖИ СВОЙ ОТВЕТ В 960 символов!"
    )
    interpretation = await ask_openai(prompt)
    return card, interpretation

async def generate_tarot_image(card: str) -> str:
    """Генерирует изображение карты Таро с помощью DALL-E."""
    prompt = f"Мистическое изображение карты Таро '{card}' в стиле древних эзотерических традиций, с богатой символикой, глубокими цветами и магической аурой."
    try:
        response = await asyncio.to_thread(
            client.images.generate,
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        if not response.data or not response.data[0].url:
            raise Exception("DALL-E не вернул изображение")
        image_url = response.data[0].url
        logger.debug(f"Сгенерирован URL изображения: {image_url}")
        return image_url
    except Exception as e:
        logger.error(f"Ошибка генерации изображения: {e}")
        return ""