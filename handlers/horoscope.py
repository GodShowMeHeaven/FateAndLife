import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.horoscope_service import get_horoscope

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def horoscope_callback(update: Update, context: CallbackContext) -> None:
    """Обрабатывает нажатие кнопки знака зодиака и отправляет гороскоп"""
    query = update.callback_query
    sign = query.data.replace('horoscope_', '').capitalize()

    try:
        logger.info(f"Запрос гороскопа для {sign}")
        horoscope_text = get_horoscope(sign)  # ✅ Без await

        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"🔮 Ваш гороскоп для *{sign}*:\n\n{horoscope_text}",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Ошибка при получении гороскопа для {sign}: {e}")
        await query.edit_message_text("⚠️ Произошла ошибка. Попробуйте позже.")
