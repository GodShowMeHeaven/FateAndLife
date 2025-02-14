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
    Обрабатывает inline-кнопки предсказаний или текстовые команды.
    """
    query = update.callback_query
    chat_id = update.effective_chat.id

    if query:
        await query.answer()
        category = CATEGORIES.get(query.data, "неизвестно")
    else:  # Если пришло текстовое сообщение
        text = update.message.text
        category = CATEGORIES.get(text, "неизвестно")

    logger.info(f"Генерируем предсказание на тему: {category}")

    prediction = ask_openai(f"Сделай эзотерическое предсказание на тему {category}.")

    keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"🔮 *Ваше предсказание на тему {category}:*\n\n{prediction}",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

