import openai
import config
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Подключаем OpenAI API-ключ
openai.api_key = config.OPENAI_API_KEY

def get_horoscope(sign: str) -> str:
    """
    Получает гороскоп через OpenAI API (с использованием правильного endpoint).
    """
    prompt = f"Гороскоп на сегодня для знака зодиака {sign}."
    
    try:
        # Используем новый endpoint v1/chat/completions
        response = openai.chat.completions.create(  # Новый метод для работы с чатами
            model="gpt-3.5-turbo",  # Указываем модель
            messages=[  # Формируем сообщение
                {"role": "system", "content": "Ты астролог и эксперт по знакам зодиака."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7,
        )
        
        # Проверяем, что ответ содержит корректные данные
        if "choices" in response and len(response["choices"]) > 0:
            horoscope_text = response["choices"][0]["message"]["content"].strip()
            logger.info(f"Гороскоп успешно получен: {horoscope_text[:50]}...")  # Логируем начало гороскопа
            return horoscope_text
        else:
            logger.error("Ошибка: ответ OpenAI не содержит корректных данных.")
            return "⚠️ Не удалось получить гороскоп. Попробуйте позже."

    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenAI API: {e}")
        return "⚠️ Не удалось получить гороскоп. Попробуйте позже."
