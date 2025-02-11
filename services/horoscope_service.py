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
    
def get_horoscope(sign: str) -> str:
    """
    Получает гороскоп через OpenAI API (с использованием правильного endpoint).
    """
    prompt = f"Гороскоп на сегодня для знака зодиака {sign}."
    
    try:
        # Используем новый endpoint v1/chat/completions
        response = openai.ChatCompletion.create(  # Новый метод для работы с чатами
            model="gpt-3.5-turbo",  # Указываем модель
            messages=[  # Формируем сообщение
                {"role": "system", "content": "Ты астролог и эксперт по знакам зодиака."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7,
        )
        
        # Возвращаем текст гороскопа из объекта response
        horoscope_text = response['choices'][0]['message']['content'].strip()  # Используем правильную структуру ответа
        
        logger.info("Гороскоп успешно получен.")
        return horoscope_text
    
    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenAI API: {e}")
        return "⚠️ Не удалось получить гороскоп. Попробуйте позже."
