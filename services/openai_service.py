from openai import OpenAI, OpenAIError
import config
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import asyncio
import json
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
    Асинхронный запрос к OpenAI API через client.responses.create с отладкой и fallback'ом.
    Возвращает строку с результатом или читаемое сообщение об ошибке.
    """
    try:
        # Основной вызов: client.responses.create
        response = await asyncio.to_thread(
            client.responses.create,
            model="gpt-5-mini",
            input=prompt,
            max_output_tokens=1024
        )

        # DEBUG: логируем сырую структуру ответа в дебаг-логи (без раскрытия секретов).
        try:
            # Попробуем сериализовать объект ответа для логов
            resp_serialized = None
            if hasattr(response, "to_dict"):
                resp_serialized = response.to_dict()
            else:
                # fallback: попытаться через __dict__ или str()
                resp_serialized = getattr(response, "__dict__", str(response))
            # Обрезаем очень длинные логи, чтобы не засорять файлы (например, 5000 символов)
            logger.debug("Raw OpenAI responses.create response: %s", json.dumps(resp_serialized, default=str)[:5000])
        except Exception as e:
            logger.debug("Не удалось сериализовать response для логирования: %s", e)

        # Попытка извлечь текст из response.output — поддерживаем несколько форматов
        output = getattr(response, "output", None)
        if output:
            texts = []
            # output обычно — список блоков, внутри content — список частей
            for block in output:
                content = block.get("content") if isinstance(block, dict) else getattr(block, "content", None)
                if not content:
                    continue
                # content может быть списком объектов, где каждый объект имеет поле 'text' или 'type'/'text'
                if isinstance(content, list):
                    for item in content:
                        # item может быть dict или объект
                        text = item.get("text") if isinstance(item, dict) else getattr(item, "text", None)
                        if text:
                            texts.append(text)
                        else:
                            # иногда item == {"type":"message","text":"..."} или схожее
                            # попробуем собрать все строчные значения
                            if isinstance(item, dict):
                                for v in item.values():
                                    if isinstance(v, str) and len(v.strip()) > 0:
                                        texts.append(v)
                elif isinstance(content, str):
                    texts.append(content)
                else:
                    # попытка общего извлечения
                    try:
                        texts.append(str(content))
                    except Exception:
                        pass

            if texts:
                result = "\n\n".join(t.strip() for t in texts if t and t.strip())
                if result:
                    return result.strip()

        # Если до сюда дошли — output пустой или не удалось извлечь полезный текст
        logger.warning("Пустой или непарсируемый response.output от responses.create — попробуем fallback на chat.completions.create")

    except OpenAIError as e:
        # Явная ошибка от OpenAI — логируем и пробрасываем (retry-логика с tenacity выше должна поймать)
        logger.error("OpenAIError при responses.create: %s", e)
        raise
    except Exception as e:
        # Не-фатальная неизвестная ошибка — логируем и попробуем fallback
        logger.exception("Неожиданная ошибка при responses.create: %s", e)

    # ----------------- FALLBACK: попробовать старый чат-эндпоинт -----------------
    try:
        logger.info("Пробуем fallback: client.chat.completions.create (если доступно в SDK)")
        response2 = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-5-mini",
            messages=[{"role": "user", "content": prompt}],
            max_output_tokens=1024  # на новых SDK это имя может быть другим; если ошибка — поправь на max_tokens
        )

        # Попытка извлечь текст из вариантов старого формата
        if getattr(response2, "choices", None):
            try:
                text = response2.choices[0].message.content
                if text:
                    return text.strip()
            except Exception:
                # ещё попытки: если response2.choices[0].message может быть dict
                try:
                    text = response2.choices[0]["message"]["content"]
                    if text:
                        return text.strip()
                except Exception:
                    pass

        logger.warning("Fallback тоже вернул пустой ответ или неожиданный формат: %s", str(response2)[:1000])

    except OpenAIError as e:
        logger.error("OpenAIError при fallback chat.completions.create: %s", e)
        raise
    except Exception as e:
        logger.exception("Неожиданная ошибка при fallback chat.completions.create: %s", e)

    # Если ничего не получилось — вернуть понятное сообщение пользователю и логировать
    logger.error("Оба вызова (responses.create и chat.completions.create) не вернули текста.")
    return "⚠️ Не удалось получить ответ от модели. Проверьте ключ OpenAI, квоту и доступность модели."
