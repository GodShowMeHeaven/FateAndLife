import openai
import config
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Подключаем OpenAI API-ключ
openai.api_key = config.OPENAI_API_KEY

async def get_horoscope(sign: str) -> str:
    """
    Получает гороскоп через OpenAI API (с использованием правильного endpoint).
    """
    prompt = f"Гороскоп на сегодня для знака зодиака {sign}."
    
    try:
        # Используем chat/completions вместо completions
        response = openai.chat.completions.create(  # ✅ Новый метод!
            model="gpt-3.5-turbo",  # Указываем чат-модель
            messages=[{"role": "user", "content": prompt}],  # ✅ Новый формат API
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenAI: {e}")
        return f"⚠️ Ошибка при получении данных: {e}"
            


