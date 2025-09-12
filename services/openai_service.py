from openai import OpenAI, OpenAIError
import config
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация клиента OpenAI
client = OpenAI(api_key=config.OPENAI_API_KEY)

@retry(
    stop=stop_after_attempt(3),  # Максимум 3 попытки
    wait=wait_exponential(multiplier=1, min=4, max=10),  # Экспоненциальная задержка: 4-10 секунд
    retry=retry_if_exception_type(OpenAIError),  # Повтор только для ошибок OpenAI
    before_sleep=lambda retry_state: logger.info(
        f"Попытка {retry_state.attempt_number} из 3, ожидание {retry_state.next_action.sleep} секунд..."
    )
)
async def ask_openai(prompt: str) -> str:
    """
    Асинхронный запрос к OpenAI API с повторными попытками при сбоях.

    Args:
        prompt (str): Текст запроса к OpenAI.

    Returns:
        str: Ответ от OpenAI или сообщение об ошибке после всех попыток.
    """
    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-5",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7  # Увеличено для креативных ответов
        )
        return response.choices[0].message.content.strip()
    except OpenAIError as e:
        logger.error(f"Ошибка OpenAI API: {e}")
        raise
    except Exception as e:
        logger.error(f"Неизвестная ошибка при запросе к OpenAI: {e}")
        return f"⚠️ Неизвестная ошибка при получении данных: {e}"

async def main():
    """Пример использования для тестирования."""
    try:
        result = await ask_openai("Привет, расскажи мне что-то интересное!")
        logger.info(f"Ответ от OpenAI: {result}")
    except Exception as e:
        logger.error(f"Не удалось выполнить запрос: {e}")

if __name__ == "__main__":
    asyncio.run(main())