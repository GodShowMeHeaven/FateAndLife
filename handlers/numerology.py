import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.numerology_service import calculate_life_path_number
from services.openai_service import ask_openai
from utils.button_guard import button_guard
from utils.loading_messages import send_processing_message, replace_processing_message
from utils.calendar import start_calendar

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def validate_date(birth_date: str) -> bool:
    """Проверяет, что дата в формате ДД.ММ.ГГГГ"""
    return bool(re.match(r"^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.\d{4}$", birth_date))

@button_guard
async def numerology(update: Update, context: CallbackContext) -> None:
    """Обрабатывает команду /numerology и предлагает выбрать дату рождения."""
    await start_calendar(update, context)

async def process_numerology(update: Update, context: CallbackContext, birth_date: str) -> None:
    """Выполняет расчет нумерологии и отправляет результат пользователю."""
    processing_message = await send_processing_message(update, "🔢 Подготавливаем ваш нумерологический расчет...", context)

    try:
        life_path_number = calculate_life_path_number(birth_date)
        interpretation = await ask_openai(
            f"""
            Напиши эзотерическое толкование числа судьбы {life_path_number}.
            Опиши ключевые качества личности, предназначение и кармический смысл этого числа.
            Добавь мистическую символику и советы по гармонизации энергии.
            """
        )

        numerology_text = (
            f"🔢 **Ваше число судьбы: {life_path_number}**\n\n"
            f"✨ *Интерпретация:* {interpretation}\n\n"
            "🔮 Число судьбы определяет вашу главную жизненную энергию и предназначение!"
        )

        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await replace_processing_message(context, processing_message, numerology_text, reply_markup)
    except Exception as e:
        logger.error(f"Ошибка при нумерологическом расчете: {e}")
        await replace_processing_message(context, processing_message, "⚠️ Произошла ошибка при расчете. Попробуйте позже.")