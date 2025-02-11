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
    prompt = f"Гороскоп на сегодня для знака зодиака {sign}."
    
    try:
        # Новый метод для работы с ChatCompletion
        response = await openai.completions.create(  # Новый интерфейс API
            model="gpt-3.5-turbo",  # Указываем модель
            prompt=prompt,  # Передаем prompt
            max_tokens=200,
            temperature=0.7,
        )
        
        # Возвращаем текст гороскопа
        horoscope_text = response['choices'][0]['text'].strip()
        
        logger.info("Гороскоп успешно получен.")
        return horoscope_text
    
    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenAI API: {e}")
        return "⚠️ Не удалось получить гороскоп. Попробуйте позже."
