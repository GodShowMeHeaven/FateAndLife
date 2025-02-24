import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_processing_message(update: Update, text: str):
    """Отправляет сообщение о том, что идет генерация."""
    return update.message.reply_text(text)

async def replace_processing_message(context: CallbackContext, message, new_text, reply_markup=None):
    """Заменяет сообщение о генерации на финальный ответ."""
    try:
        await message.edit_text(new_text, parse_mode="Markdown", reply_markup=reply_markup)
    except Exception as e:
        logger.warning(f"Ошибка при редактировании сообщения: {e}")
        await message.reply_text(new_text, parse_mode="Markdown", reply_markup=reply_markup)
