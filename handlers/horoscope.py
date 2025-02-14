import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.horoscope_service import get_horoscope

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def horoscope_callback(update: Update, context: CallbackContext) -> None:
    """Обрабатывает нажатие кнопки знака зодиака и генерирует гороскоп"""
    query = update.callback_query
    sign = query.data.replace('horoscope_', '').capitalize()  # Извлекаем знак зодиака из callback_data

    try:
        logger.info(f"Запрос гороскопа для знака {sign}")

        # Убираем await, так как get_horoscope() теперь синхронная
        horoscope_text = get_horoscope(sign)

        # Создаем inline-кнопки для возврата к меню
        keyboard = [
            [InlineKeyboardButton("🔙 Вернуться в меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.answer()
        await query.edit_message_text(
            f"🔮 Ваш гороскоп для *{sign}*:\n\n{horoscope_text}",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Ошибка при получении гороскопа для {sign}: {e}")
        await query.answer()
        await query.edit_message_text("⚠️ Произошла ошибка при получении гороскопа. Попробуйте позже.")
