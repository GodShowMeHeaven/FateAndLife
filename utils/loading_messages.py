import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_processing_message(update: Update, text: str, context: CallbackContext = None) -> None:
    """Отправляет сообщение о процессе, поддерживая как сообщения, так и callback-запросы."""
    if update.message:
        return await update.message.reply_text(text)
    elif update.callback_query and context:
        chat_id = update.effective_chat.id
        return await context.bot.send_message(chat_id, text)
    else:
        logger.error("Не удалось определить источник для отправки сообщения")
        raise ValueError("Невозможно отправить сообщение: отсутствует message или callback_query")

async def replace_processing_message(context: CallbackContext, message, new_text, reply_markup=None) -> None:
    """Заменяет сообщение о процессе на финальный ответ."""
    try:
        await message.edit_text(new_text, parse_mode="Markdown", reply_markup=reply_markup)
    except Exception as e:
        logger.warning(f"Ошибка при редактировании сообщения: {e}")
        await message.reply_text(new_text, parse_mode="Markdown", reply_markup=reply_markup)