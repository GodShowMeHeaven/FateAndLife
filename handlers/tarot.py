import logging
import asyncio
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.tarot_service import get_tarot_interpretation, generate_tarot_image
from services.database import save_tarot_reading
from utils.loading_messages import send_processing_message, replace_processing_message

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)

def escape_markdown_v2(text: str) -> str:
    """Экранирует все зарезервированные символы для MarkdownV2."""
    reserved_chars = r'([_*[\]()~`>#+-=|{}.!])'
    return re.sub(reserved_chars, r'\\\1', text)

async def tarot(update: Update, context: CallbackContext) -> None:
    """Вытягивает случайную карту Таро и отправляет интерпретацию."""
    chat_id = update.effective_chat.id
    logger.info(f"🔮 tarot() запущен для пользователя {chat_id}")
    logger.debug(f"Текущее состояние processing: {context.user_data.get('processing')}")

    # Проверка на активный процесс
    if context.user_data.get("processing", False):
        logger.warning(f"⚠️ Обнаружен активный процесс для {chat_id}, ждём завершения...")
        await update.message.reply_text("⏳ Подождите, предыдущий запрос завершается...")
        await asyncio.sleep(2)  # Даём время завершиться предыдущему вызову
        if context.user_data.get("processing", False):  # Если всё ещё активен
            logger.warning(f"⚠️ Предыдущий процесс завис, сбрасываем флаг для {chat_id}")
            context.user_data["processing"] = False

    context.user_data["processing"] = True
    logger.debug(f"Флаг processing установлен в True для {chat_id}")
    processing_message = None

    try:
        async with asyncio.timeout(40):  # Общий таймаут 40 секунд
            # Отправляем сообщение о подготовке
            processing_message = await send_processing_message(update, escape_markdown_v2("🎴 Подготавливаем вашу карту Таро..."), context)
            logger.debug(f"Сообщение о подготовке отправлено для {chat_id}")

            # Получение карты Таро
            card = None
            interpretation = None
            logger.debug(f"Перед вызовом get_tarot_interpretation для {chat_id}")
            for attempt in range(2):
                try:
                    logger.info(f"🎴 Генерация карты Таро... (Попытка {attempt+1})")
                    card, interpretation = await asyncio.wait_for(
                        get_tarot_interpretation(), timeout=15
                    )
                    logger.info(f"🎴 Вытянута карта: {card}")
                    break
                except asyncio.TimeoutError:
                    logger.warning(f"⏳ Время ожидания get_tarot_interpretation() истекло (Попытка {attempt+1})")
                    if attempt == 1:
                        error_message = escape_markdown_v2("⚠️ Ошибка: не удалось получить карту в течение 30 секунд.")
                        await replace_processing_message(context, processing_message, error_message, parse_mode="MarkdownV2")
                        return
                except Exception as e:
                    logger.error(f"Ошибка в get_tarot_interpretation (Попытка {attempt+1}): {e}", exc_info=True)
                    if attempt == 1:
                        raise

            # Проверяем тип interpretation
            if not isinstance(interpretation, str):
                logger.error(f"interpretation не строка: {type(interpretation)}")
                raise ValueError("Interpretation должна быть строкой")

            # Генерация изображения
            image_url = None
            logger.debug(f"Перед вызовом generate_tarot_image для {chat_id}")
            try:
                logger.info("📸 Генерация изображения...")
                image_url = await asyncio.wait_for(
                    asyncio.to_thread(generate_tarot_image, card), timeout=20
                )
                logger.info("📸 Изображение успешно сгенерировано" if image_url else "📸 Изображение не сгенерировано")
            except asyncio.TimeoutError:
                logger.warning("⏳ Время ожидания generate_tarot_image() истекло")
            except Exception as e:
                logger.error(f"Ошибка в generate_tarot_image: {e}", exc_info=True)

            # Сохранение результата
            logger.debug(f"Перед сохранением результата для {chat_id}")
            save_tarot_reading(chat_id, card, interpretation)
            logger.info("💾 Результат сохранён в базе данных")

            # Формирование текста
            card_escaped = escape_markdown_v2(card)
            interpretation_escaped = escape_markdown_v2(interpretation)
            formatted_text = f"🎴 *Ваша карта Таро: {card_escaped}*\n\n{interpretation_escaped}"
            logger.debug(f"Отправляемый текст: {formatted_text[:500]}...")

            # Формируем inline-кнопки
            keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Отправка изображения
            if image_url:
                logger.info("📤 Отправка изображения...")
                await context.bot.send_photo(chat_id=chat_id, photo=image_url)

            # Отправка текста
            logger.info("📤 Отправка сообщения с картой...")
            await replace_processing_message(context, processing_message, formatted_text, reply_markup, parse_mode="MarkdownV2")

    except asyncio.TimeoutError:
        logger.error(f"❌ Общий таймаут выполнения tarot() для {chat_id}")
        error_message = escape_markdown_v2("⚠️ Ошибка: процесс занял слишком много времени.")
        if processing_message:
            await replace_processing_message(context, processing_message, error_message, parse_mode="MarkdownV2")
        else:
            await update.message.reply_text(error_message, parse_mode="MarkdownV2")
    except Exception as e:
        logger.error(f"❌ Ошибка в tarot(): {e}", exc_info=True)
        error_message = escape_markdown_v2("⚠️ Ошибка, попробуйте снова.")
        if processing_message:
            await replace_processing_message(context, processing_message, error_message, parse_mode="MarkdownV2")
        else:
            await update.message.reply_text(error_message, parse_mode="MarkdownV2")
    finally:
        context.user_data["processing"] = False
        logger.info(f"✅ tarot() завершен для пользователя {chat_id} с флагом processing={context.user_data.get('processing')}")
        logger.debug(f"Флаг processing сброшен для {chat_id}")
        await asyncio.sleep(1)
