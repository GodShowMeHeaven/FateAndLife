import logging
from telegram import Update
from telegram.ext import ContextTypes
from services.tarot_service import get_tarot_interpretation, generate_tarot_image
from utils.loading_messages import send_processing_message, replace_processing_message
from utils.telegram_helpers import send_photo_with_caption
from utils.validation import sanitize_input

logger = logging.getLogger(__name__)

async def tarot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает команду /tarot и отправляет расклад карт Таро."""
    chat_id = update.effective_chat.id
    logger.info(f"Пользователь {chat_id} запросил расклад Таро")

    processing_message = None
    try:
        # Отправляем сообщение о генерации
        processing_message = await send_processing_message(update, "🔮 Вытягиваем карты Таро...")

        # Получаем название карты и её интерпретацию
        card, tarot_reading = await get_tarot_interpretation()

        # Экранируем текст для MarkdownV2
        tarot_reading = sanitize_input(tarot_reading)
        card = sanitize_input(card)  # Экранируем название карты

        # Генерируем изображение карты
        image_url = generate_tarot_image(card)

        if not image_url:
            raise Exception("Не удалось сгенерировать изображение карты Таро")

        # Отправляем фото с подписью
        await send_photo_with_caption(context.bot, chat_id, image_url, tarot_reading, parse_mode="MarkdownV2")

        # Удаляем сообщение о генерации
        await replace_processing_message(context, processing_message, "✅ Расклад Таро готов!")

    except Exception as e:
        logger.error(f"Ошибка вытягивания карты Таро: {e}")
        error_message = sanitize_input(f"⚠️ Ошибка: {str(e)}")
        if processing_message:
            await replace_processing_message(context, processing_message, error_message, parse_mode="MarkdownV2")
        else:
            await context.bot.send_message(chat_id, error_message, parse_mode="MarkdownV2")