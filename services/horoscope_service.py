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
    Получает гороскоп через OpenAI API для чатовой модели.
    """
    prompt = f"Гороскоп на сегодня для знака зодиака {sign}."
    
    try:
        # Используем правильный метод для чатовой модели
        response = await openai.chat.completions.create(  # Используем endpoint v1/chat/completions
            model="gpt-3.5-turbo",  # Указываем модель
            messages=[  # Формируем сообщения для чатовой модели
                {"role": "system", "content": "Ты астролог и эксперт по знакам зодиака."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        
        # Возвращаем текст гороскопа
        horoscope_text = response['choices'][0]['message']['content'].strip()
        
        logger.info("Гороскоп успешно получен.")
        return horoscope_text
    
    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenAI API: {e}")
        return "⚠️ Не удалось получить гороскоп. Попробуйте позже."
