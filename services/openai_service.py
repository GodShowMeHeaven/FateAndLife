import openai
import config
import random
# Подключаем OpenAI API-ключ
openai.api_key = config.OPENAI_API_KEY


tarot_cards = [
    "Шут", "Маг", "Верховная Жрица", "Императрица", "Император",
    "Иерофант", "Влюбленные", "Колесница", "Справедливость", "Отшельник",
    "Колесо Фортуны", "Сила", "Повешенный", "Смерть", "Умеренность",
    "Дьявол", "Башня", "Звезда", "Луна", "Солнце", "Суд", "Мир"
]

def get_tarot_interpretation() -> str:
    """Запрашивает у OpenAI интерпретацию случайной карты Таро."""
    card = random.choice(tarot_cards)
    prompt = (
        f"Вытащи карту Таро: {card}. Объясни ее значение с точки зрения судьбы, любви, карьеры и духовного пути."
    )
    interpretation = ask_openai(prompt)
    return f"🎴 **Ваша карта Таро: {card}**\n\n{interpretation}"

def ask_openai(prompt: str) -> str:
    """Запрос к OpenAI для генерации ответа."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "Ты эзотерический астрологический помощник."},
                      {"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=300
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"⚠️ Ошибка при получении данных: {str(e)}"
def get_natal_chart(name: str, birth_date: str, birth_time: str, birth_place: str) -> str:
    """Запрос к OpenAI для анализа натальной карты."""
    prompt = (
        f"Создай эзотерический анализ натальной карты для {name}. "
        f"Дата рождения: {birth_date}, Время рождения: {birth_time}, Место: {birth_place}. "
        "Опиши характер, предназначение, скрытые таланты и ключевые события судьбы."
    )
    return ask_openai(prompt)
