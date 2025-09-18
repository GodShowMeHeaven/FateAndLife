# utils/telegram_helpers.py
from telegram import Bot

TELEGRAM_CAPTION_LIMIT = 1024

async def send_photo_with_caption(bot: Bot, chat_id: int, photo_url: str, caption: str):
    if not caption:
        await bot.send_photo(chat_id=chat_id, photo=photo_url)
        return

    if len(caption) <= TELEGRAM_CAPTION_LIMIT:
        await bot.send_photo(chat_id=chat_id, photo=photo_url, caption=caption)
    else:
        # обрезаем подпись для подписи, а полный текст отправляем отдельным сообщением
        short_caption = caption[:(TELEGRAM_CAPTION_LIMIT - 3)] + "..."
        await bot.send_photo(chat_id=chat_id, photo=photo_url, caption=short_caption)
        # отправляем полный текст отдельно (можно с форматированием)
        await bot.send_message(chat_id=chat_id, text=caption)
