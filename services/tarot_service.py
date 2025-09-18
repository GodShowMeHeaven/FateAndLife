import random
from openai import OpenAI
from services.openai_service import ask_openai
import re
import config
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация OpenAI клиента
client = OpenAI(api_key=config.OPENAI_API_KEY)

# Список карт Таро
tarot_cards = [
    "Шут", "Маг", "Верховная Жрица", "Императрица", "Император",
    "Иерофант", "Влюбленные", "Колесница", "Справедливость", "Отшельник",
    "Колесо Фортуны", "Сила", "Повешенный", "Смерть", "Умеренность",
    "Дьявол", "Башня", "Звезда", "Луна", "Солнце", "Суд", "Мир"
]

async def get_tarot_interpretation():
    """Запрашивает у OpenAI детальную интерпретацию карты Таро и возвращает её название и текст."""
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
        f"Пиши поэтично, образно, как древние пророчества."
        f"Не используй Markdown-форматирование (например, ###, **, *, # и т.д.)."
    )
    interpretation = ''.join(c for c in interpretation if ord(c) < 128 or c in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ\n')
    interpretation = re.sub(r'\s+', ' ', interpretation).strip()  # Нормализация пробелов
    interpretation = interpretation.replace('\n ', '\n')  # Удаление пробелов после переносов строк
    logger.debug(f"Очищенная интерпретация: {interpretation[:100]}...")
    return card, interpretation

def generate_tarot_image(card: str) -> str:
    """Генерирует изображение карты Таро через OpenAI DALL·E 3."""
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"A mystical, ethereal Tarot card illustration of {card} in an ancient, ornate style with magical symbols, cosmic elements, and mystical energies. The image should appear as if from an ancient grimoire, with rich details, gold accents, and a sense of profound mystery. Add esoteric symbols around the edges and magical auras.",
            size="1024x1024",
            quality="standard",
            n=1
        )
        return response.data[0].url
    except Exception as e:
        logger.error(f"Ошибка при генерации изображения: {e}")
        return None