from telegram import Bot
from utils.validation import sanitize_input

TELEGRAM_CAPTION_LIMIT = 1024

async def send_photo_with_caption(bot: Bot, chat_id: int, photo_url: str, caption: str, parse_mode: str = None):
    """
    Отправляет фото с подписью, обрезая длинные подписи и отправляя остаток отдельным сообщением.
    
    Args:
        bot: Объект Telegram Bot
        chat_id: ID чата
        photo_url: URL изображения
        caption: Подпись к фото
        parse_mode: Формат текста (например, 'MarkdownV2')
    """
    if not caption:
        await bot.send_photo(chat_id=chat_id, photo=photo_url)
        return

    # Экранируем подпись для MarkdownV2
    caption = sanitize_input(caption)

    if len(caption) <= TELEGRAM_CAPTION_LIMIT:
        await bot.send_photo(
            chat_id=chat_id,
            photo=photo_url,
            caption=caption,
            parse_mode=parse_mode
        )
    else:
        # Обрезаем подпись для фото, остаток отправляем отдельно
        short_caption = caption[:(TELEGRAM_CAPTION_LIMIT - 3)] + "..."
        await bot.send_photo(
            chat_id=chat_id,
            photo=photo_url,
            caption=short_caption,
            parse_mode=parse_mode
        )
        # Отправляем полный текст отдельным сообщением
        await bot.send_message(
            chat_id=chat_id,
            text=caption,
            parse_mode=parse_mode
        )