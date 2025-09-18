import logging
from telegram import Update, Message
from telegram.ext import ContextTypes
from utils.validation import sanitize_input, truncate_text

logger = logging.getLogger(__name__)

async def send_processing_message(update: Update, text: str, parse_mode: str = None) -> Message:
    """Отправляет временное сообщение о процессе обработки."""
    query = update.callback_query
    if query:
        return await query.message.reply_text(text, parse_mode=parse_mode)
    return await update.message.reply_text(text, parse_mode=parse_mode)

async def replace_processing_message(context: ContextTypes.DEFAULT_TYPE, message: Message, text: str, parse_mode: str = None) -> None:
    """Заменяет временное сообщение новым текстом."""
    try:
        logger.debug(f"Замена сообщения с текстом: {text[:100]}...")
        await message.edit_text(text, parse_mode=parse_mode)
    except Exception as e:
        logger.error(f"Ошибка замены сообщения: {e}")
        raise

async def send_photo_with_caption(bot, chat_id: int, photo_url: str, caption: str, parse_mode: str = None) -> None:
    """Отправляет фото с подписью."""
    try:
        caption = truncate_text(caption, max_length=1024)
        # Дополнительное экранирование для MarkdownV2
        if parse_mode == "MarkdownV2":
            caption = sanitize_input(caption)  # Повторное экранирование
        logger.debug(f"Отправка фото с подписью: {caption[:100]}...")
        await bot.send_photo(
            chat_id=chat_id,
            photo=photo_url,
            caption=caption,
            parse_mode=None
        )
    except Exception as e:
        logger.error(f"Ошибка отправки фото: {e}")
        raise