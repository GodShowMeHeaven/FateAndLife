import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.tarot_service import get_tarot_interpretation, generate_tarot_image
from services.database import save_tarot_reading
from utils.button_guard import button_guard  # ✅ Защита от спама

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@button_guard
async def tarot(update: Update, context: CallbackContext) -> None:
    """Вытягивает случайную карту Таро и отправляет интерпретацию."""
    chat_id = update.effective_chat.id
    logger.info(f"🔮 tarot() запущен для пользователя {chat_id}")

    try:
        # Таймаут на получение карты
        try:
            logger.info("🎴 Генерация карты Таро...")
            card, interpretation = await asyncio.wait_for(
                asyncio.to_thread(get_tarot_interpretation), timeout=15  # Увеличили время ожидания
            )
            logger.info(f"🎴 Вытянута карта: {card}")
        except asyncio.TimeoutError:
            logger.error("⏳ Время ожидания get_tarot_interpretation() истекло")
            await update.message.reply_text("⚠️ Ошибка: не удалось получить карту.")
            return

        # Таймаут на генерацию изображения
        try:
            logger.info("📸 Генерация изображения...")
            image_url = await asyncio.wait_for(
                asyncio.to_thread(generate_tarot_image, card), timeout=20  # Увеличили время ожидания
            )
            if image_url:
                logger.info("📸 Изображение успешно сгенерировано")
        except asyncio.TimeoutError:
            logger.warning("⏳ Время ожидания generate_tarot_image() истекло")
            image_url = None  # Продолжаем без изображения

        # Сохраняем результат гадания
        logger.info("💾 Сохранение результата в базе данных...")
        save_tarot_reading(chat_id, card, interpretation)

        # Формируем inline-кнопки
        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Отправляем фото, если оно есть
        if image_url:
            logger.info("📤 Отправка изображения...")
            await context.bot.send_photo(chat_id=chat_id, photo=image_url)

        # Отправляем текстовое объяснение карты
        logger.info("📤 Отправка сообщения с картой...")
        await update.message.reply_text(
            f"🎴 *Ваша карта Таро: {card}*\n\n{interpretation}",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"❌ Ошибка в tarot(): {e}")
        await update.message.reply_text("⚠️ Ошибка, попробуйте снова.")

    finally:
        context.user_data["processing"] = False  # ✅ Гарантированный сброс
        logger.info(f"✅ tarot() завершен для пользователя {chat_id}")

        await asyncio.sleep(2)