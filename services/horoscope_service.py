import openai
import config
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Подключаем OpenAI API-ключ
client = openai.OpenAI(api_key=config.OPENAI_API_KEY)

def get_horoscope(sign: str) -> str:
    """
    Получает гороскоп через OpenAI API (использует v1/chat/completions).
    """
    prompt = f"Гороскоп на сегодня для знака зодиака {sign}."

    try:
        # Отправляем запрос к OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",  # Используем gpt-4o для лучшего качества
            messages=[
                {"role": "system", "content": "Ты астролог и эксперт по знакам зодиака."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,  # Ограничиваем размер ответа
            temperature=0.7
        )

        # Корректно извлекаем ответ API
        horoscope_text = response.choices[0].message.content.strip()
        logger.info(f"Гороскоп для {sign}: {horoscope_text[:50]}...")
        return horoscope_text

    except openai.APIConnectionError:
        logger.error("Ошибка соединения с OpenAI API.")
        return "⚠️ Ошибка соединения с OpenAI. Попробуйте позже."

    except openai.RateLimitError:
        logger.error("Превышен лимит запросов OpenAI.")
        return "⚠️ Превышен лимит запросов. Попробуйте через минуту."

    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenAI API: {e}")
        return "⚠️ Не удалось получить гороскоп. Попробуйте позже."
