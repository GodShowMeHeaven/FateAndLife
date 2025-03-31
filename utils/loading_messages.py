import logging
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_processing_message(update: Update, text: str, context: CallbackContext = None):
    """Отправляет сообщение о том, что идет генерация, поддерживая как сообщения, так и callback-запросы."""
    if update.message:
        return await update.message.reply_text(text)
    elif update.callback_query and context:
        chat_id = update.effective_chat.id
        return await context.bot.send_message(chat_id, text)
    else:
        logger.error("Не удалось определить источник для отправки сообщения")
        raise ValueError("Невозможно отправить сообщение: отсутствует message или callback_query")

async def replace_processing_message(context: CallbackContext, message, new_text, reply_markup=None, parse_mode="MarkdownV2"):
    """Заменяет сообщение о генерации на финальный ответ."""
    logger.debug(f"Текст для редактирования: {new_text}")
    try:
        await message.edit_text(new_text, parse_mode=parse_mode, reply_markup=reply_markup)
        logger.info("Сообщение успешно отредактировано")
    except telegram.error.BadRequest as e:
        logger.warning(f"Ошибка при редактировании сообщения: {e}")
        # Пытаемся отправить новое сообщение вместо редактирования
        chat_id = message.chat_id
        logger.debug(f"Попытка отправить новое сообщение с текстом: {new_text}")
        try:
            await context.bot.send_message(chat_id, new_text, parse_mode=parse_mode, reply_markup=reply_markup)
            logger.info("Новое сообщение успешно отправлено")
        except telegram.error.BadRequest as e:
            logger.error(f"Ошибка при отправке нового сообщения: {e}")
            # Отправляем сообщение об ошибке без сложного форматирования
            await context.bot.send_message(chat_id, "⚠️ Произошла ошибка при обновлении сообщения. Попробуйте позже.", parse_mode="MarkdownV2")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при редактировании сообщения: {e}")
        chat_id = message.chat_id
        await context.bot.send_message(chat_id, "⚠️ Произошла ошибка при обновлении сообщения. Попробуйте позже.", parse_mode="MarkdownV2")