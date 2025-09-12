from telegram import Update
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown_v2
from services.numerology_service import calculate_life_path_number
from utils.validation import validate_date
from utils.calendar import start_calendar
from keyboards.main_menu import main_menu_keyboard
import logging

logger = logging.getLogger(__name__)

async def numerology(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Запрашивает дату рождения для нумерологического расчета."""
    if not update.effective_chat:
        logger.error("Отсутствует effective_chat в update")
        return
    await update.message.reply_text("🔢 Выберите дату рождения через календарь:")
    context.user_data["awaiting_numerology"] = True
    await start_calendar(update, context)

async def process_numerology(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает выбранную дату и возвращает число жизненного пути."""
    if not update.message or not update.effective_chat:
        logger.error("Отсутствует сообщение или effective_chat в update")
        return
    birth_date = context.user_data.get("selected_date")
    if not birth_date:
        await update.message.reply_text(
            escape_markdown_v2("⚠️ Дата не выбрана. Используйте календарь."),
            parse_mode="MarkdownV2",
            reply_markup=main_menu_keyboard
        )
        return
    if not validate_date(birth_date):
        await update.message.reply_text(
            escape_markdown_v2("⚠️ Неверный формат даты (ДД.ММ.ГГГГ)."),
            parse_mode="MarkdownV2",
            reply_markup=main_menu_keyboard
        )
        return

    try:
        life_path_number = calculate_life_path_number(birth_date)
        await update.message.reply_text(
            escape_markdown_v2(f"🔢 Ваше число жизненного пути: {life_path_number}"),
            parse_mode="MarkdownV2",
            reply_markup=main_menu_keyboard
        )
        context.user_data.pop("selected_date", None)
        context.user_data.pop("awaiting_numerology", None)
    except Exception as e:
        logger.error(f"Ошибка расчета числа жизненного пути: {e}")
        await update.message.reply_text(
            escape_markdown_v2("⚠️ Ошибка при расчете. Попробуйте позже."),
            parse_mode="MarkdownV2",
            reply_markup=main_menu_keyboard
        )