import openai
import config
import random
import os
import logging
# Подключаем OpenAI API-ключ
openai.api_key = config.OPENAI_API_KEY
# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)  # Инициализация логгера
# Список карт Таро
tarot_cards = [
    "Шут", "Маг", "Верховная Жрица", "Императрица", "Император",
    "Иерофант", "Влюбленные", "Колесница", "Справедливость", "Отшельник",
    "Колесо Фортуны", "Сила", "Повешенный", "Смерть", "Умеренность",
    "Дьявол", "Башня", "Звезда", "Луна", "Солнце", "Суд", "Мир"
]

async def get_tarot_interpretation() -> str:
    """Запрашивает у OpenAI интерпретацию случайной карты Таро."""
    card = random.choice(tarot_cards)
    prompt = (
        f"Вытащи карту Таро: {card}. Объясни ее значение с точки зрения судьбы, любви, карьеры и духовного пути."
    )
    interpretation = await ask_openai(prompt)  # Используем await
    return f"🎴 **Ваша карта Таро: {card}**\n\n{interpretation}"

async def ask_openai(prompt: str) -> str:
    """
    Отправляет запрос к OpenAI API для получения интерпретации.
    """
    try:
        # Используем chat/completions вместо completions
        response = await openai.chat.completions.create(  # ✅ Новый метод!
            model="gpt-3.5-turbo",  # Указываем чат-модель
            messages=[{"role": "user", "content": prompt}],  # ✅ Новый формат API
            max_tokens=150,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenAI: {e}")
        return f"⚠️ Ошибка при получении данных: {e}"
async def get_natal_chart(name: str, birth_date: str, birth_time: str, birth_place: str) -> str:
    """Запрос к OpenAI для анализа натальной карты."""
    prompt = (
        f"Создай эзотерический анализ натальной карты для {name}. "
        f"Дата рождения: {birth_date}, Время рождения: {birth_time}, Место: {birth_place}. "
        "Опиши характер, предназначение, скрытые таланты и ключевые события судьбы."
    )
    return await ask_openai(prompt)  # Используем await
