import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.horoscope_service import get_horoscope
from keyboards.main_menu import main_menu_keyboard
from utils.button_guard import button_guard  # ✅ Импорт защиты кнопок
from utils.loading_messages import send_processing_message, replace_processing_message  # ✅ Импорт функций загрузки

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

        # Отправляем техническое сообщение о подготовке
        processing_message = await send_processing_message(update, f"🔮 Подготавливаем ваш гороскоп для {sign}...")

        # Запрашиваем гороскоп
        horoscope_text = get_horoscope(sign)

        # Формируем клавиатуру с главным меню
        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Заменяем техническое сообщение на итоговый результат
        await replace_processing_message(context, processing_message, f"🔮 Ваш гороскоп для *{sign}*:\n\n{horoscope_text}", reply_markup)

    except Exception as e:
        logger.error(f"Ошибка при получении гороскопа для {sign}: {e}")
        await replace_processing_message(context, processing_message, "⚠️ Произошла ошибка при получении гороскопа. Попробуйте позже.")
