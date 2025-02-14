import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.openai_service import ask_openai

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CATEGORIES = {
    "fortune_money": "деньги",
    "fortune_luck": "удача",
    "fortune_relationships": "отношения",
    "fortune_health": "здоровье"
}

async def fortune_callback(update: Update, context: CallbackContext) -> None:
    """
    Обрабатывает inline-кнопки предсказаний.
    """
    query = update.callback_query
    if not query:
        logger.error("Ошибка: fortune_callback вызван не через callback_query.")
        return

    await query.answer()
    category = CATEGORIES.get(query.data, "неизвестно")
    logger.info(f"Генерируем предсказание на тему: {category}")

    prediction = ask_openai(f"Сделай эзотерическое предсказание на тему {category}.")
    keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(f"🔮 *Ваше предсказание на тему {category}:*\n\n{prediction}",
                                  parse_mode="Markdown",
                                  reply_markup=reply_markup)
