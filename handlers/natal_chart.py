from telegram import Update
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown  # Правильный импорт
from services.natal_chart_service import get_natal_chart
from utils.validation import validate_date, validate_time, validate_place
from utils.calendar import start_calendar
from keyboards.main_menu import main_menu_keyboard
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

async def natal_chart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat:
        logger.error("Отсутствует effective_chat в update")
        return
    await update.message.reply_text("🌌 Введите ваше имя:")
    context.user_data["natal_step"] = "name"
    context.user_data["last_interaction"] = datetime.now()

async def handle_natal_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text or not update.effective_chat:
        logger.error("Отсутствует сообщение или effective_chat в update")
        return
    if "last_interaction" in context.user_data and (datetime.now() - context.user_data["last_interaction"]) > timedelta(minutes=10):
        context.user_data.clear()
        await update.message.reply_text(
            escape_markdown("⚠️ Время ожидания ввода истекло. Начните заново.", version=2),
            parse_mode="MarkdownV2",
            reply_markup=main_menu_keyboard
        )
        return

    step = context.user_data.get("natal_step")
    text = update.message.text
    logger.debug(f"Обрабатываем ввод для шага {step}: {text}")

    if step == "name":
        context.user_data["name"] = text
        context.user_data["natal_step"] = "birth_date"
        context.user_data["last_interaction"] = datetime.now()
        await update.message.reply_text("📅 Выберите дату рождения:")
        await start_calendar(update, context)
    elif step == "birth_date":
        if not validate_date(text):
            await update.message.reply_text(
                escape_markdown("⚠️ Неверный формат даты (ДД.ММ.ГГГГ).", version=2),
                parse_mode="MarkdownV2"
            )
            return
        context.user_data["birth_date"] = text
        context.user_data["natal_step"] = "birth_time"
        context.user_data["last_interaction"] = datetime.now()
        await update.message.reply_text("⏰ Введите время рождения (ЧЧ:ММ):")
    elif step == "birth_time":
        if not validate_time(text):
            await update.message.reply_text(
                escape_markdown("⚠️ Неверный формат времени (ЧЧ:ММ).", version=2),
                parse_mode="MarkdownV2"
            )
            return
        context.user_data["birth_time"] = text
        context.user_data["natal_step"] = "birth_place"
        context.user_data["last_interaction"] = datetime.now()
        await update.message.reply_text("📍 Введите место рождения:")
    elif step == "birth_place":
        if not validate_place(text):
            await update.message.reply_text(
                escape_markdown("⚠️ Неверный формат места (только буквы и пробелы).", version=2),
                parse_mode="MarkdownV2"
            )
            return
        context.user_data["birth_place"] = text
        context.user_data["last_interaction"] = datetime.now()

        try:
            result = await get_natal_chart(
                context.user_data["name"],
                context.user_data["birth_date"],
                context.user_data["birth_time"],
                context.user_data["birth_place"]
            )
            await update.message.reply_text(escape_markdown(result, version=2), parse_mode="MarkdownV2")
            context.user_data.clear()
            await update.message.reply_text("⏬ Главное меню:", reply_markup=main_menu_keyboard)
        except Exception as e:
            logger.error(f"Ошибка расчета натальной карты: {e}")
            await update.message.reply_text(
                escape_markdown("⚠️ Ошибка при расчете натальной карты. Попробуйте позже.", version=2),
                parse_mode="MarkdownV2",
                reply_markup=main_menu_keyboard
            )
            context.user_data.clear()