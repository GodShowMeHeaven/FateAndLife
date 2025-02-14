import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.openai_service import ask_openai

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Сопоставление кнопок с категориями предсказаний
CATEGORIES = {
    "💰 На деньги": "деньги",
    "🍀 На удачу": "удача",
    "💞 На отношения": "отношения",
    "🩺 На здоровье": "здоровье"
}

async def fortune_callback(update: Update, context: CallbackContext) -> None:
    """
    Обрабатывает нажатие кнопки предсказания и сразу отправляет предсказание.
    """
    query = update.callback_query
    if not query:
        logger.error("Ошибка: fortune_callback вызван не через callback_query.")
        return

    await query.answer()  # Подтверждаем нажатие кнопки

    category = CATEGORIES.get(query.data, "неизвестно")

    logger.info(f"Генерируем предсказание на тему: {category}")

    # Получаем предсказание от OpenAI
    prediction = ask_openai(f"Сделай эзотерическое предсказание на тему {category}.")

    # Кнопка возврата в меню
    keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Обновляем сообщение, заменяя кнопки на предсказание
    await query.message.edit_text(f"🔮 *Ваше предсказание на тему {category}:*\n\n{prediction}",
                                  parse_mode="Markdown",
                                  reply_markup=reply_markup)
