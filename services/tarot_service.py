import random
from services.openai_service import ask_openai

# Список карт Таро
tarot_cards = [
    "Шут", "Маг", "Верховная Жрица", "Императрица", "Император",
    "Иерофант", "Влюбленные", "Колесница", "Справедливость", "Отшельник",
    "Колесо Фортуны", "Сила", "Повешенный", "Смерть", "Умеренность",
    "Дьявол", "Башня", "Звезда", "Луна", "Солнце", "Суд", "Мир"
]

def get_tarot_interpretation():
    """Запрашивает у OpenAI детальную интерпретацию карты Таро и возвращает её название и текст."""
    card = random.choice(tarot_cards)
    prompt = (
        f"Вытащи карту Таро: {card}. Опиши её значение в четырех сферах:\n"
        "1) Судьба\n2) Любовь\n3) Карьера\n4) Духовное развитие.\n"
        "Добавь эзотерические детали и совет."
    )
    interpretation = ask_openai(prompt)
    return card, interpretation

def generate_tarot_image(card: str) -> str:
    """Генерирует изображение карты Таро через OpenAI API."""
    prompt = f"Create a mystical Tarot card illustration of {card} in a detailed fantasy style."
    return ask_openai(prompt, image=True)  # Передаем флаг `image=True` для генерации изображения
