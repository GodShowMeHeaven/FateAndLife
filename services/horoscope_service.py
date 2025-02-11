from services.openai_service import ask_openai
import random

def get_horoscope(sign: str, period: str = "сегодня") -> str:
    """Получает гороскоп через OpenAI API и форматирует его красиво."""
    prompt = (
        f"Напиши эзотерический гороскоп для знака {sign} на {period}. "
        "Добавь мистические детали, советы, совместимость и символику."
    )
    response = ask_openai(prompt)

    formatted_horoscope = (
        f"🔮 *Гороскоп для {sign.capitalize()} на {period}*\n\n"
        f"📅 *Дата:* _{period}_\n"
        f"✨ *Предсказание:* _{response}_\n"
        f"💡 *Совет дня:* Доверьтесь интуиции, знаки судьбы вокруг вас.\n"
        f"🔢 *Счастливое число:* {random.randint(1, 99)}\n"
        f"🎨 *Счастливый цвет:* {random.choice(['🔵 Синий', '🔴 Красный', '🟢 Зеленый', '🟡 Желтый'])}\n"
    )

    return formatted_horoscope
