import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.tarot_service import get_tarot_interpretation, generate_tarot_image
from services.database import save_tarot_reading
from utils.button_guard import button_guard  # ✅ Защита от спама

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@button_guard
async def tarot(update: Update, context: CallbackContext) -> None:
    """
    Вытягивает случайную карту Таро, отправляет изображение и интерпретацию.
    Доступно ТОЛЬКО через команду /tarot или текстовую кнопку "🎴 Карты Таро".
    """
    chat_id = update.effective_chat.id  # ✅ Универсальный способ получения chat_id
    logger.info(f"🔮 Начало гадания Таро для пользователя {chat_id}...")

    try:
        # Получаем карту и её интерпретацию
        card, interpretation = await asyncio.to_thread(get_tarot_interpretation)  # ✅ Выполняем в отдельном потоке
        logger.info(f"🔮 Вытянута карта: {card}")

        # Генерируем изображение карты
        image_url = await asyncio.to_thread(generate_tarot_image, card)
        if image_url:
            logger.info(f"🔮 Изображение карты {card} сгенерировано успешно.")

        # Сохраняем результат гадания в базе данных
        save_tarot_reading(chat_id, card, interpretation)

        # Формируем inline-кнопки
        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Если есть изображение карты, отправляем его
        if image_url:
            await context.bot.send_photo(chat_id=chat_id, photo=image_url)

        # Отправляем текстовое объяснение карты
        await update.message.reply_text(
            f"🎴 *Ваша карта Таро: {card}*\n\n{interpretation}",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"❌ Ошибка при вытягивании карты Таро: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка, попробуйте снова.")

    finally:
        context.user_data["processing"] = False  # ✅ Гарантированно сбрасываем флаг
        logger.info(f"🔮 Завершение гадания Таро для пользователя {chat_id}")

        await asyncio.sleep(2)  # ✅ Задержка для защиты от спама
