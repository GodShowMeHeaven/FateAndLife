import random
from openai import OpenAI
from services.openai_service import ask_openai

# Инициализация OpenAI клиента
client = OpenAI()

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
        f"Вытащи карту Таро: {card}. Опиши её значение в четырех сферах:\n"
        "1) Судьба\n2) Любовь\n3) Карьера\n4) Духовное развитие.\n"
        "Добавь эзотерические детали и совет."
    )
    interpretation = await ask_openai(prompt)  # Добавлен await для получения строки
    return card, interpretation

def generate_tarot_image(card: str) -> str:
    """Генерирует изображение карты Таро через OpenAI DALL·E 3."""
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"A mystical Tarot card illustration of {card} in a detailed fantasy style.",
            size="1024x1024",
            quality="standard",
            n=1
        )
        return response.data[0].url
    except Exception as e:
        print(f"Ошибка при генерации изображения: {e}")
        return None