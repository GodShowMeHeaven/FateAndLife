from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.tarot_service import get_tarot_interpretation, generate_tarot_image
from services.database import save_tarot_reading
from utils.button_guard import button_guard  # ✅ Импорт защиты кнопок
import logging
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def tarot(update: Update, context: CallbackContext) -> None:
    """Вытягивает случайную карту Таро, отправляет изображение и интерпретацию с защитой от спама"""
    query = update.callback_query

    # Разрешаем обработку кнопки "Вытянуть новую карту" даже при активном процессе
    if context.user_data.get("processing", False) and query.data != "draw_tarot":
        await query.answer("⏳ Подождите, идет генерация карты...", show_alert=True)
        return

    context.user_data["processing"] = True  # ✅ Устанавливаем флаг выполнения
    try:
        if query:
            await query.answer()

        logger.info("Вытягиваем случайную карту Таро...")
        card, interpretation = get_tarot_interpretation()  # Получаем карту и её интерпретацию
        image_url = generate_tarot_image(card)  # Генерируем изображение карты

        # Сохраняем гадание в базе данных
        save_tarot_reading(update.effective_user.id, card, interpretation)

        # Формируем клавиатуру с кнопками
        keyboard = [
            [InlineKeyboardButton("🔄 Вытянуть новую карту", callback_data="draw_tarot")],
            [InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        chat_id = update.effective_chat.id  # ✅ Явно передаем chat_id

        # Если генерация изображения удалась, отправляем картинку
        if image_url:
            await context.bot.send_photo(chat_id=chat_id, photo=image_url)

        # Отправляем текстовое объяснение карты
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🎴 *Ваша карта Таро: {card}*\n\n{interpretation}",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Ошибка при вытягивании карты Таро: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Произошла ошибка, попробуйте снова."
        )

    finally:
        await asyncio.sleep(2)  # ✅ Небольшая задержка, чтобы избежать спама
        context.user_data["processing"] = False  # ✅ Сбрасываем флаг выполнения

@button_guard
async def tarot_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if query:
        await query.answer()  # ✅ Подтверждаем нажатие кнопки
        if query.data == "draw_tarot":
            logger.info("Кнопка '🔄 Вытянуть новую карту' нажата.")
            await tarot(update, context)
