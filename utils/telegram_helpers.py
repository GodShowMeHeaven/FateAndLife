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
    """Отправляет фото с подписью, обрезая подпись до лимита Telegram."""
    try:
        # Лимит подписи в Telegram - 1024 символа
        max_caption_length = 1024
        
        # Обрезаем подпись до лимита
        if len(caption) > max_caption_length:
            # Обрезаем с запасом для безопасности
            safe_length = max_caption_length - 20
            caption = caption[:safe_length] + "..."
            logger.info(f"Подпись обрезана до {len(caption)} символов")
        
        # Убираем parse_mode для подписи, чтобы избежать ошибок с экранированием
        logger.debug(f"Отправка фото с подписью длиной {len(caption)} символов")
        await bot.send_photo(
            chat_id=chat_id,
            photo=photo_url,
            caption=caption,
            parse_mode=None  # Убираем parse_mode для избежания ошибок
        )
        
        logger.info("Фото с подписью успешно отправлено")
        
    except Exception as e:
        logger.error(f"Ошибка отправки фото: {e}")
        # Если не удалось отправить фото с подписью, отправляем отдельно
        try:
            await bot.send_photo(chat_id=chat_id, photo=photo_url)
            await bot.send_message(chat_id=chat_id, text=caption, parse_mode=None)
            logger.info("Фото и текст отправлены отдельно")
        except Exception as e2:
            logger.error(f"Ошибка отправки фото и текста отдельно: {e2}")
            raise