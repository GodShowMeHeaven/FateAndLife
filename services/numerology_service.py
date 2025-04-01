from services.openai_service import ask_openai
from datetime import datetime

def calculate_life_path_number(birth_date: str) -> int:
    """
    Вычисляет число судьбы (нумерологический код личности) по дате рождения.
    Формат: 'ДД.ММ.ГГГГ'
    """
    digits = [int(d) for d in birth_date if d.isdigit()]  # Берем все цифры даты
    life_path_number = sum(digits)  # Складываем все цифры

    # Считаем до одной цифры (1-9)
    while life_path_number >= 10:
        life_path_number = sum(map(int, str(life_path_number)))

    return life_path_number


def get_numerology_interpretation(life_path_number: int) -> str:
    """
    Запрашивает у OpenAI интерпретацию нумерологического числа.
    """
    prompt = f"""
    Напиши эзотерическое толкование числа судьбы {life_path_number}.
    Опиши ключевые качества личности, предназначение и кармический смысл этого числа.
    Добавь мистическую символику и советы по гармонизации энергии.
    Не используй Markdown-форматирование (например, ###, **, *, # и т.д.).
    """
    return ask_openai(prompt)
