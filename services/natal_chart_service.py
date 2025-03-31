from services.openai_service import ask_openai
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_natal_chart(name: str, birth_date: str, birth_time: str, birth_place: str) -> str:
    """Асинхронно запрашивает у OpenAI детальный разбор натальной карты."""
    prompt = (
        f"Составь детальный анализ натальной карты для {name}. "
        f"Дата рождения: {birth_date}, Время: {birth_time}, Место: {birth_place}. "
        "Опиши 1) Психологический портрет, 2) Жизненное предназначение, "
        "3) Основные планеты (Солнце, Луна, Асцендент), 4) Советы для гармонии в жизни."
    )
    response = await ask_openai(prompt)
    
    # Очищаем текст от потенциально проблемных символов
    response = ''.join(c for c in response if ord(c) < 128 or c in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ\n')
    response = response.replace("\n\n", "\n").replace("  ", " ")  # Упрощаем форматирование
    
    logger.debug(f"Очищенный natal_chart_text: {response[:500]}...")  # Логируем первые 500 символов
    return response