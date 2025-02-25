from services.openai_service import ask_openai
import re

def get_natal_chart(name: str, birth_date: str, birth_time: str, birth_place: str) -> str:
    """Запрашивает у OpenAI детальный разбор натальной карты."""
    prompt = (
        f"Составь детальный анализ натальной карты для {name}. "
        f"Дата рождения: {birth_date}, Время: {birth_time}, Место: {birth_place}. "
        "Опиши 1) Психологический портрет, 2) Жизненное предназначение, "
        "3) Основные планеты (Солнце, Луна, Асцендент), 4) Советы для гармонии в жизни."
    )
    response = ask_openai(prompt)
    
    # Экранируем специальные символы Markdown
    response = response.replace("*", "\\*").replace("_", "\\_").replace("`", "\\`")
    return response