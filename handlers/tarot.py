import logging
from telegram import Update
from telegram.ext import ContextTypes
from services.tarot_service import get_tarot_interpretation, generate_tarot_image
from utils.loading_messages import send_processing_message, replace_processing_message
from utils.telegram_helpers import send_photo_with_caption
from utils.validation import sanitize_input, truncate_text

logger = logging.getLogger(__name__)

async def tarot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает команду /tarot и отправляет расклад карт Таро."""
    chat_id = update.effective_chat.id
    logger.info(f"Пользователь {chat_id} запросил расклад Таро")

    processing_message = None
    try:
        # Отправляем сообщение о генерации
        processing_message = await send_processing_message(
            update,
            sanitize_input("🔮 Вытягиваем карты Таро..."),
            parse_mode="MarkdownV2"
        )

        # Получаем название карты и её интерпретацию
        card, tarot_reading = await get_tarot_interpretation()
        logger.debug(f"Карта: {card}, Интерпретация: {tarot_reading[:50]}...")

        # Формируем подпись
        raw_caption = f"🎴 Карта: {card}\n\n{tarot_reading}"
        logger.debug(f"Исходная подпись: {raw_caption[:100]}...")

        # Экранируем подпись
        caption = sanitize_input(raw_caption)
        logger.debug(f"Экранированная подпись: {caption[:100]}...")

        # Обрезаем подпись до лимита Telegram (1024 символа)
        caption = truncate_text(caption, max_length=1024)
        logger.debug(f"Обрезанная подпись: {caption[:100]}...")

        # Генерируем изображение карты
        image_url = generate_tarot_image(card)
        if not image_url:
            raise Exception("Не удалось сгенерировать изображение карты Таро")

        # Отправляем фото с подписью
        await send_photo_with_caption(
            context.bot,
            chat_id,
            image_url,
            caption,
            parse_mode="MarkdownV2"
        )

        # Удаляем сообщение о генерации
        await replace_processing_message(
            context,
            processing_message,
            sanitize_input("✅ Расклад Таро готов!"),
            parse_mode="MarkdownV2"
        )

    except Exception as e:
        logger.error(f"Ошибка вытягивания карты Таро: {e}")
        error_message = sanitize_input(f"⚠️ Ошибка: {str(e)}")
        logger.debug(f"Сообщение об ошибке: {error_message}")
        if processing_message:
            await replace_processing_message(
                context,
                processing_message,
                error_message,
                parse_mode="MarkdownV2"
            )
        else:
            await context.bot.send_message(
                chat_id,
                error_message,
                parse_mode="MarkdownV2"
            )