from telegram import Update
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown  # Правильный импорт
from services.compatibility_service import get_compatibility
from utils.validation import validate_date, validate_time, validate_place
from utils.calendar import start_calendar
from keyboards.main_menu import main_menu_keyboard
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

async def compatibility(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat:
        logger.error("Отсутствует effective_chat в update")
        return
    await update.message.reply_text("💑 Выберите дату рождения первого человека:")
    context.user_data["awaiting_compatibility"] = True
    context.user_data["compatibility_step"] = "birth_date1"
    context.user_data["last_interaction"] = datetime.now()
    await start_calendar(update, context)

async def compatibility_natal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_chat:
        logger.error("Отсутствует сообщение или effective_chat в update")
        return
    if not context.args or len(context.args) < 8:
        await update.message.reply_text(
            escape_markdown("⚠️ Укажите данные в формате: имя1 дата1 время1 место1 имя2 дата2 время2 место2", version=2),
            parse_mode="MarkdownV2"
        )
        return

    name1, birth1, time1, place1, name2, birth2, time2, place2 = context.args[:8]
    if not validate_date(birth1) or not validate_time(time1) or not validate_date(birth2) or not validate_time(time2):
        await update.message.reply_text(
            escape_markdown("⚠️ Неверный формат даты (ДД.ММ.ГГГГ) или времени (ЧЧ:ММ).", version=2),
            parse_mode="MarkdownV2"
        )
        return

    try:
        result = await get_compatibility(name1, birth1, time1, place1, name2, birth2, time2, place2)
        await update.message.reply_text(escape_markdown(result, version=2), parse_mode="MarkdownV2")
    except Exception as e:
        logger.error(f"Ошибка расчета совместимости: {e}")
        await update.message.reply_text(
            escape_markdown("⚠️ Ошибка при расчете совместимости. Попробуйте позже.", version=2),
            parse_mode="MarkdownV2"
        )

async def handle_compatibility_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

    step = context.user_data.get("compatibility_step")
    text = update.message.text
    logger.debug(f"Обрабатываем ввод для шага {step}: {text}")

    if step == "birth_date1":
        if not validate_date(text):
            await update.message.reply_text(
                escape_markdown("⚠️ Неверный формат даты (ДД.ММ.ГГГГ).", version=2),
                parse_mode="MarkdownV2"
            )
            return
        context.user_data["birth_date1"] = text
        context.user_data["compatibility_step"] = "birth_time1"
        context.user_data["last_interaction"] = datetime.now()
        await update.message.reply_text("⏰ Введите время рождения первого человека (ЧЧ:ММ):")
    elif step == "birth_time1":
        if not validate_time(text):
            await update.message.reply_text(
                escape_markdown("⚠️ Неверный формат времени (ЧЧ:ММ).", version=2),
                parse_mode="MarkdownV2"
            )
            return
        context.user_data["birth_time1"] = text
        context.user_data["compatibility_step"] = "birth_place1"
        context.user_data["last_interaction"] = datetime.now()
        await update.message.reply_text("📍 Введите место рождения первого человека:")
    elif step == "birth_place1":
        if not validate_place(text):
            await update.message.reply_text(
                escape_markdown("⚠️ Неверный формат места (только буквы и пробелы).", version=2),
                parse_mode="MarkdownV2"
            )
            return
        context.user_data["birth_place1"] = text
        context.user_data["name1"] = context.user_data.get("name1", "Первый человек")
        context.user_data["compatibility_step"] = "birth_date2"
        context.user_data["last_interaction"] = datetime.now()
        await update.message.reply_text("💑 Выберите дату рождения второго человека:")
        await start_calendar(update, context)
    elif step == "birth_date2":
        if not validate_date(text):
            await update.message.reply_text(
                escape_markdown("⚠️ Неверный формат даты (ДД.ММ.ГГГГ).", version=2),
                parse_mode="MarkdownV2"
            )
            return
        context.user_data["birth_date2"] = text
        context.user_data["compatibility_step"] = "birth_time2"
        context.user_data["last_interaction"] = datetime.now()
        await update.message.reply_text("⏰ Введите время рождения второго человека (ЧЧ:ММ):")
    elif step == "birth_time2":
        if not validate_time(text):
            await update.message.reply_text(
                escape_markdown("⚠️ Неверный формат времени (ЧЧ:ММ).", version=2),
                parse_mode="MarkdownV2"
            )
            return
        context.user_data["birth_time2"] = text
        context.user_data["compatibility_step"] = "birth_place2"
        context.user_data["last_interaction"] = datetime.now()
        await update.message.reply_text("📍 Введите место рождения второго человека:")
    elif step == "birth_place2":
        if not validate_place(text):
            await update.message.reply_text(
                escape_markdown("⚠️ Неверный формат места (только буквы и пробелы).", version=2),
                parse_mode="MarkdownV2"
            )
            return
        context.user_data["birth_place2"] = text
        context.user_data["name2"] = context.user_data.get("name2", "Второй человек")
        context.user_data["last_interaction"] = datetime.now()

        try:
            result = await get_compatibility(
                context.user_data["name1"],
                context.user_data["birth_date1"],
                context.user_data["birth_time1"],
                context.user_data["birth_place1"],
                context.user_data["name2"],
                context.user_data["birth_date2"],
                context.user_data["birth_time2"],
                context.user_data["birth_place2"]
            )
            await update.message.reply_text(escape_markdown(result, version=2), parse_mode="MarkdownV2")
            context.user_data.clear()
            await update.message.reply_text("⏬ Главное меню:", reply_markup=main_menu_keyboard)
        except Exception as e:
            logger.error(f"Ошибка расчета совместимости: {e}")
            await update.message.reply_text(
                escape_markdown("⚠️ Ошибка при расчете совместимости. Попробуйте позже.", version=2),
                parse_mode="MarkdownV2",
                reply_markup=main_menu_keyboard
            )
            context.user_data.clear()