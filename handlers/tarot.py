import logging
from telegram import Update
from telegram.ext import ContextTypes
from services.tarot_service import get_tarot_card  # Изменено с get_tarot_reading
from utils.loading_messages import send_processing_message, replace_processing_message
from utils.telegram_helpers import send_photo_with_caption

logger = logging.getLogger(__name__)

async def tarot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает команду /tarot и отправляет расклад карт Таро."""
    chat_id = update.effective_chat.id
    logger.info(f"Пользователь {chat_id} запросил расклад Таро")

    try:
        # Отправляем сообщение о генерации
        processing_message = await send_processing_message(update, "🔮 Вытягиваем карты Таро...")

        # Получаем расклад Таро (описание и URL изображения)
        tarot_reading, image_url = await get_tarot_card()  # Изменено с get_tarot_reading

        # Отправляем фото с подписью, используя send_photo_with_caption
        await send_photo_with_caption(context.bot, chat_id, image_url, tarot_reading)

        # Удаляем сообщение о генерации
        await replace_processing_message(context, processing_message, "✅ Расклад Таро готов!")

    except Exception as e:
        logger.error(f"Ошибка вытягивания карты Таро: {e}")
        await replace_processing_message(context, processing_message, f"⚠️ Ошибка: {str(e)}")