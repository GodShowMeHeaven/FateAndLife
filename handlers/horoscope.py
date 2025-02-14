import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.horoscope_service import get_horoscope
from keyboards.main_menu import main_menu_keyboard
from utils.button_guard import button_guard  # ✅ Импорт защиты кнопок

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@button_guard
async def horoscope_callback(update: Update, context: CallbackContext) -> None:
    """Обрабатывает нажатие кнопки знака зодиака и отправляет гороскоп"""
    query = update.callback_query
    sign = query.data.replace('horoscope_', '').capitalize()

    try:
        await query.answer()
        logger.info(f"Запрос гороскопа для {sign}")

        horoscope_text = get_horoscope(sign)

        # Формируем клавиатуру с главным меню
        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Отправляем новое сообщение с клавиатурой
        await update.effective_message.reply_text(
            f"🔮 Ваш гороскоп для *{sign}*:\n\n{horoscope_text}",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Ошибка при получении гороскопа для {sign}: {e}")
        await update.effective_message.reply_text("⚠️ Произошла ошибка при получении гороскопа. Попробуйте позже.")
