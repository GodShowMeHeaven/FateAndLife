import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.horoscope_service import get_horoscope
from keyboards.main_menu import main_menu_keyboard
from utils.button_guard import button_guard
from utils.loading_messages import send_processing_message, replace_processing_message
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def escape_markdown_v2(text: str) -> str:
    """Экранирует все зарезервированные символы для MarkdownV2."""
    reserved_chars = r'([_*[\]()~`>#+-=|{}.!])'
    return re.sub(reserved_chars, r'\\\1', text)

@button_guard
async def horoscope_callback(update: Update, context: CallbackContext) -> None:
    """Обрабатывает нажатие кнопки знака зодиака и отправляет гороскоп."""
    query = update.callback_query
    sign = query.data.replace('horoscope_', '').capitalize()
    processing_message = None  # Инициализация переменной перед блоком try

    try:
        await query.answer()
        logger.info(f"Запрос гороскопа для {sign}")

        # Определяем, куда отправлять сообщение
        chat_id = query.message.chat_id if query.message else update.effective_chat.id

        # Отправляем техническое сообщение о подготовке (без форматирования для надежности)
        processing_message = await context.bot.send_message(chat_id, f"🔮 Подготавливаем ваш гороскоп для {sign}...")

        # Определяем дату для гороскопа
        if context.user_data.get("selected_date"):
            horoscope_date = context.user_data.get("selected_date")
        else:
            horoscope_date = datetime.now().strftime("%d.%m.%Y")

        # Асинхронно запрашиваем гороскоп
        horoscope_text = await get_horoscope(sign, context)

        # Экранируем текст для MarkdownV2
        horoscope_date_escaped = escape_markdown_v2(horoscope_date)
        horoscope_text_escaped = escape_markdown_v2(horoscope_text)

        # Формируем итоговый текст
        formatted_text = (
            f"🔮 Ваш гороскоп для *{sign}* на {horoscope_date_escaped}:\n\n"
            f"{horoscope_text_escaped}"
        )
        logger.debug(f"Отправляемый текст: {formatted_text}")

        # Формируем клавиатуру с кнопкой возврата
        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Заменяем техническое сообщение на итоговый результат
        await replace_processing_message(
            context,
            processing_message,
            formatted_text,
            reply_markup,
            parse_mode="MarkdownV2"
        )

    except Exception as e:
        logger.error(f"Ошибка при получении гороскопа для {sign}: {e}")
        error_message = "⚠️ Произошла ошибка при получении гороскопа. Попробуйте позже."
        
        if processing_message:
            await replace_processing_message(
                context,
                processing_message,
                escape_markdown_v2(error_message),
                parse_mode="MarkdownV2"
            )
        else:
            await context.bot.send_message(
                chat_id,
                escape_markdown_v2(error_message),
                parse_mode="MarkdownV2"
            )
