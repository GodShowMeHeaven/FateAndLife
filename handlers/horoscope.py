import logging
from telegram import Update
from telegram.ext import CallbackContext
from services.horoscope_service import get_horoscope
from keyboards.main_menu import main_menu_keyboard  # Импортируем правильную клавиатуру

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def horoscope_callback(update: Update, context: CallbackContext) -> None:
    """Обрабатывает нажатие кнопки знака зодиака и генерирует гороскоп"""
    query = update.callback_query
    sign = query.data.replace('horoscope_', '').capitalize()  # Извлекаем знак зодиака из callback_data

    try:
        # Получаем гороскоп для выбранного знака
        logger.info(f"Запрос гороскопа для знака {sign}")
        horoscope_text = await get_horoscope(sign)
        
        # Обрабатываем успешный результат
        await query.answer()  # Подтверждаем нажатие

        # Отправляем гороскоп в сообщении
        await query.edit_message_text(f"🔮 Ваш гороскоп для *{sign}*:\n\n{horoscope_text}", parse_mode="Markdown")

        # Возвращаем главное меню
        # Важно: убедитесь, что это сообщение отправляется один раз.
        await query.message.reply_text("Выберите раздел:", reply_markup=main_menu_keyboard)

    except Exception as e:
        logger.error(f"Ошибка при получении гороскопа для {sign}: {e}")
        await query.answer()
        await query.edit_message_text("⚠️ Произошла ошибка при получении гороскопа. Попробуйте позже.")
        await query.message.reply_text("Выберите раздел:", reply_markup=main_menu_keyboard)  # Возвращаем главное меню
