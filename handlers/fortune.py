from telegram import Update
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown  # Правильный импорт
from services.fortune_service import get_fortune
from keyboards.main_menu import main_menu_keyboard
import logging

logger = logging.getLogger(__name__)

CATEGORIES = {
    "fortune_money": "деньги",
    "fortune_luck": "удача",
    "fortune_love": "отношения",
    "fortune_health": "здоровье"
}

def get_category(data: str) -> str:
    return CATEGORIES.get(data, "неизвестно")

async def fortune_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat:
        logger.error("Отсутствует effective_chat в update")
        return

    query = update.callback_query
    text = update.message.text if update.message else None
    category = None

    if query and query.data:
        await query.answer()
        category = get_category(query.data)
    elif text in ["💰 На деньги", "🍀 На удачу", "💞 На отношения", "🩺 На здоровье"]:
        category = {
            "💰 На деньги": "деньги",
            "🍀 На удачу": "удача",
            "💞 На отношения": "отношения",
            "🩺 На здоровье": "здоровье"
        }.get(text)

    if not category:
        logger.warning("Неизвестная категория предсказания")
        await (query.message.edit_text if query else update.message.reply_text)(
            escape_markdown("⚠️ Неизвестная категория. Вернитесь в меню.", version=2),
            parse_mode="MarkdownV2",
            reply_markup=main_menu_keyboard
        )
        return

    try:
        fortune = await get_fortune(category)
        fortune = fortune[:4000]
        await (query.message.edit_text if query else update.message.reply_text)(
            escape_markdown(f"🔮 Предсказание на {category}:\n{fortune}", version=2),
            parse_mode="MarkdownV2",
            reply_markup=main_menu_keyboard
        )
    except Exception as e:
        logger.error(f"Ошибка получения предсказания: {e}")
        await (query.message.edit_text if query else update.message.reply_text)(
            escape_markdown("⚠️ Ошибка при получении предсказания. Попробуйте позже.", version=2),
            parse_mode="MarkdownV2",
            reply_markup=main_menu_keyboard
        )