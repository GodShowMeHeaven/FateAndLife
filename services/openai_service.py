import openai
import config
import random
import os

# Подключаем OpenAI API-ключ
openai.api_key = config.OPENAI_API_KEY

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
        # Новый способ работы с OpenAI API (версия 1.0+)
        response = await openai.completions.create(  # Используем асинхронный вызов
            model="gpt-3.5-turbo",  # Используем модель GPT-3.5 или GPT-4
            prompt=prompt,
            max_tokens=150,
            temperature=0.7,
        )
        return response['choices'][0]['text'].strip()  # Получаем текст из ответа
    except Exception as e:
        return f"⚠️ Ошибка при получении данных: {e}"

async def get_natal_chart(name: str, birth_date: str, birth_time: str, birth_place: str) -> str:
    """Запрос к OpenAI для анализа натальной карты."""
    prompt = (
        f"Создай эзотерический анализ натальной карты для {name}. "
        f"Дата рождения: {birth_date}, Время рождения: {birth_time}, Место: {birth_place}. "
        "Опиши характер, предназначение, скрытые таланты и ключевые события судьбы."
    )
    return await ask_openai(prompt)  # Используем await
