import logging
import asyncio
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.tarot_service import get_tarot_interpretation, generate_tarot_image
from services.database import save_tarot_reading
from utils.loading_messages import send_processing_message, replace_processing_message

logging.basicConfig(level=logging.DEBUG)  # Включаем DEBUG для детализации
logger = logging.getLogger(__name__)

def escape_markdown_v2(text: str) -> str:
    """Экранирует все зарезервированные символы для MarkdownV2."""
    reserved_chars = r'([_*[\]()~`>#+-=|{}.!])'
    return re.sub(reserved_chars, r'\\\1', text)

async def tarot(update: Update, context: CallbackContext) -> None:
    """Вытягивает случайную карту Таро и отправляет интерпретацию."""
    chat_id = update.effective_chat.id
    logger.info(f"🔮 tarot() запущен для пользователя {chat_id}")
    processing_message = None

    # Проверка на активный процесс
    if context.user_data.get("processing", False):
        logger.warning(f"⚠️ Блокировка повторного вызова tarot для пользователя {chat_id}")
        await update.message.reply_text("⏳ Подождите, запрос обрабатывается...")
        return

    context.user_data["processing"] = True
    logger.debug(f"Флаг processing установлен в True для {chat_id}")

    try:
        # Отправляем техническое сообщение о подготовке
        processing_message = await send_processing_message(update, escape_markdown_v2("🎴 Подготавливаем вашу карту Таро..."), context)
        logger.debug(f"Сообщение о подготовке отправлено для {chat_id}")

        # Получение карты Таро
        card = None
        interpretation = None
        for attempt in range(2):
            try:
                logger.info(f"🎴 Генерация карты Таро... (Попытка {attempt+1})")
                card, interpretation = await asyncio.wait_for(
                    asyncio.to_thread(get_tarot_interpretation), timeout=15
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
                logger.error(f"Ошибка в get_tarot_interpretation (Попытка {attempt+1}): {e}")
                if attempt == 1:
                    raise  # Повторяем ошибку после второй попытки

        # Генерация изображения
        image_url = None
        try:
            logger.info("📸 Генерация изображения...")
            image_url = await asyncio.wait_for(
                asyncio.to_thread(generate_tarot_image, card), timeout=10
            )
            logger.info("📸 Изображение успешно сгенерировано" if image_url else "📸 Изображение не сгенерировано")
        except asyncio.TimeoutError:
            logger.warning("⏳ Время ожидания generate_tarot_image() истекло")
        except Exception as e:
            logger.error(f"Ошибка в generate_tarot_image: {e}")

        # Сохранение результата
        logger.info("💾 Сохранение результата в базе данных...")
        save_tarot_reading(chat_id, card, interpretation)
        logger.debug(f"Результат сохранён: карта={card}")

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

    except Exception as e:
        logger.error(f"❌ Ошибка в tarot(): {e}")
        error_message = escape_markdown_v2("⚠️ Ошибка, попробуйте снова.")
        if processing_message:
            await replace_processing_message(context, processing_message, error_message, parse_mode="MarkdownV2")
        else:
            await update.message.reply_text(error_message, parse_mode="MarkdownV2")

    finally:
        context.user_data["processing"] = False
        logger.info(f"✅ tarot() завершен для пользователя {chat_id} с флагом processing={context.user_data.get('processing')}")
        await asyncio.sleep(1)
