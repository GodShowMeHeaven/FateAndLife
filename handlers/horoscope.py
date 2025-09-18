from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown  # Правильный импорт
from services.horoscope_service import get_horoscope
from keyboards.main_menu import main_menu_keyboard
from utils.calendar import start_calendar
import logging

logger = logging.getLogger(__name__)

async def horoscope_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.callback_query or not update.effective_chat:
        logger.error("Отсутствует callback_query или effective_chat в update")
        return
    query = update.callback_query
    await query.answer()

    sign = query.data.split("_")[1]
    context.user_data["selected_sign"] = sign
    await query.message.edit_text("📅 Выберите дату для гороскопа:")
    context.user_data["awaiting_horoscope_date"] = True
    await start_calendar(update, context)

async def process_horoscope(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_chat:
        logger.error("Отсутствует сообщение или effective_chat в update")
        return
    selected_date = context.user_data.get("selected_date")
    sign = context.user_data.get("selected_sign")
    if not selected_date or not sign:
        await update.message.reply_text(
            escape_markdown("⚠️ Выберите знак зодиака и дату через меню.", version=2),
            parse_mode="MarkdownV2",
            reply_markup=main_menu_keyboard
        )
        return

    try:
        horoscope = await get_horoscope(sign, selected_date)
        await update.message.reply_text(
            escape_markdown(f"🌟 Гороскоп для {sign} на {selected_date}:\n{horoscope}", version=2),
            parse_mode="MarkdownV2",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu"),
                 InlineKeyboardButton("🔄 Другой день", callback_data=f"horoscope_{sign}")]
            ])
        )
        context.user_data.pop("selected_date", None)
        context.user_data.pop("selected_sign", None)
        context.user_data.pop("awaiting_horoscope_date", None)
    except Exception as e:
        logger.error(f"Ошибка получения гороскопа: {e}")
        await update.message.reply_text(
            escape_markdown("⚠️ Ошибка при получении гороскопа. Попробуйте позже.", version=2),
            parse_mode="MarkdownV2",
            reply_markup=main_menu_keyboard
        )