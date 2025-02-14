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

async def fortune_command(update: Update, context: CallbackContext) -> None:
    """Обрабатывает команду /fortune с указанием категории"""
    if not context.args:
        await update.message.reply_text(
            "🔮 *Выберите категорию предсказания:*\n"
            "`/fortune деньги`, `/fortune удача`, `/fortune отношения`, `/fortune здоровье`",
            parse_mode="Markdown"
        )
        return

    category = context.args[0].lower()
    if category not in CATEGORIES.values():
        await update.message.reply_text(
            "⚠️ Неверная категория! Выберите одну из:\n"
            "`деньги`, `удача`, `отношения`, `здоровье`",
            parse_mode="Markdown"
        )
        return

    # Получаем предсказание от OpenAI
    prediction = ask_openai(f"Сделай эзотерическое предсказание на тему {category}.")
    
    await update.message.reply_text(f"🔮 *Ваше предсказание на тему {category}:*\n\n{prediction}", parse_mode="Markdown")

async def fortune_callback(update: Update, context: CallbackContext) -> None:
    """Обрабатывает кнопки предсказаний (callback_query)"""
    query = update.callback_query

    if query is None:  # ✅ Проверяем, что update вызван через callback
        logger.error("Ошибка: fortune_callback вызван не через callback_query.")
        return

    await query.answer()  # ✅ Теперь `.answer()` вызывается только если query не None

    category_key = query.data  # Например, "fortune_money"
    
    if category_key not in CATEGORIES:
        await query.message.reply_text("⚠️ Ошибка! Выбрана неверная категория предсказания.")
        return

    category = CATEGORIES[category_key]

    logger.info(f"Генерируем предсказание на тему: {category}")

    # Получаем предсказание от OpenAI
    prediction = ask_openai(f"Сделай эзотерическое предсказание на тему {category}.")

    # Формируем кнопку возврата в меню
    keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text(f"🔮 *Ваше предсказание на тему {category}:*\n\n{prediction}", 
                                   parse_mode="Markdown",
                                   reply_markup=reply_markup)
