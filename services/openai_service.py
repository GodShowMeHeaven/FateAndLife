import openai
import config
import logging

openai.api_key = config.OPENAI_API_KEY
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ask_openai(prompt: str) -> str:
    """
    Запрос к OpenAI API.
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenAI: {e}")
        return f"⚠️ Ошибка при получении данных: {e}"
