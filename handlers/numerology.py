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

def escape_markdown_v2(text: str) -> str:
    """Экранирует все зарезервированные символы для MarkdownV2."""
    reserved_chars = r'([_*[\]()~`>#+-=|{}.!])'
    return re.sub(reserved_chars, r'\\\1', text)

def validate_date(birth_date: str) -> bool:
    """Проверяет, что дата в формате ДД.ММ.ГГГГ."""
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

        # Формируем текст без предварительного экранирования
        numerology_text_raw = (
            f"🔢 *Ваше число судьбы: {life_path_number}*\n\n"
            f"✨ *Интерпретация:* {interpretation}\n\n"
            f"🔮 Число судьбы определяет вашу главную жизненную энергию и предназначение!\n"
            f"(Дата рождения: {birth_date})"
        )
        
        # Экранируем весь текст целиком
        numerology_text = escape_markdown_v2(numerology_text_raw)
        logger.debug(f"Отправляемый текст: {numerology_text}")

        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await replace_processing_message(context, processing_message, numerology_text, reply_markup, parse_mode="MarkdownV2")

    except Exception as e:
        logger.error(f"Ошибка при нумерологическом расчете: {e}")
        error_message = escape_markdown_v2("⚠️ Произошла ошибка при расчете. Попробуйте позже.")
        await replace_processing_message(context, processing_message, error_message, parse_mode="MarkdownV2")