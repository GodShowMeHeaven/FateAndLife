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
    Получает гороскоп через OpenAI API.
    """
    try:
        # Используем асинхронный запрос для генерации гороскопа
        response = await openai.ChatCompletion.acreate(  # Используем асинхронную версию
            model="gpt-3.5-turbo",  # Указываем модель
            messages=[  # Формируем сообщение
                {"role": "system", "content": "Ты астролог и эксперт по знакам зодиака."},
                {"role": "user", "content": f"Напиши гороскоп для знака {sign} на сегодня."}
            ],
            temperature=0.7,
        )
        
        # Возвращаем текст гороскопа
        return response['choices'][0]['message']['content'].strip()
    
    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenAI API: {e}")
        return "⚠️ Не удалось получить гороскоп. Попробуйте позже."
