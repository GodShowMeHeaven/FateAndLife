from services.openai_service import ask_openai

def get_fortune(category: str) -> str:
    """Запрашивает эзотерическое предсказание у OpenAI."""
    prompt = (
        f"Сделай мистическое предсказание по теме {category}. "
        "Добавь эзотерические советы, символику и важные знаки судьбы."
        f"Не используй Markdown-форматирование (например, ###, **, *, # и т.д.). "
    )
    response = ask_openai(prompt)

    formatted_fortune = (
        f"🔮 *Предсказание: {category.capitalize()}*\n"
        "__________________________\n"
        f"{response}\n"
        "__________________________\n"
        "💡 *Совет:* Примите знаки судьбы и следуйте интуиции!"       
    )

    return formatted_fortune
