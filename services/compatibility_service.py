from services.openai_service import ask_openai

def get_zodiac_compatibility(sign1: str, sign2: str) -> str:
    """Запрашивает совместимость по знакам зодиака у OpenAI."""
    prompt = (
        f"Проанализируй совместимость между знаками зодиака {sign1} и {sign2}. "
        "Опиши сильные стороны, возможные конфликты и советы для гармоничных отношений."
    )
    return ask_openai(prompt)

def get_natal_compatibility(name1: str, birth1: str, time1: str, place1: str,
                             name2: str, birth2: str, time2: str, place2: str) -> str:
    """Запрашивает совместимость по натальной карте у OpenAI."""
    prompt = (
        f"Составь астрологический анализ совместимости для {name1} ({birth1}, {time1}, {place1}) "
        f"и {name2} ({birth2}, {time2}, {place2}). "
        "Опиши совпадения в натальных картах, судьбоносные аспекты и советы для гармонии."
        f"Не используй Markdown-форматирование (например, ###, **, *, # и т.д.). "
    )
    return ask_openai(prompt)
