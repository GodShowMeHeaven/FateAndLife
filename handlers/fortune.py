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

async def fortune(update: Update, context: CallbackContext) -> None:
    """
    Обрабатывает команду /fortune или выбор категории через callback-кнопки.
    Если вызвано через команду, отправляет клавиатуру выбора категории.
    Если вызвано через callback, сразу отправляет предсказание.
    """
    query = update.callback_query  # Проверяем, вызвано ли через callback

    if query:
        await query.answer()
        category_key = query.data  # Например, "fortune_money"
    else:
        message = update.message
        if not context.args:
            # Отправляем кнопки выбора категории, если не указаны аргументы
            keyboard = [
                [InlineKeyboardButton("💰 На деньги", callback_data="fortune_money")],
                [InlineKeyboardButton("🍀 На удачу", callback_data="fortune_luck")],
                [InlineKeyboardButton("💞 На отношения", callback_data="fortune_relationships")],
                [InlineKeyboardButton("🩺 На здоровье", callback_data="fortune_health")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await message.reply_text("🔮 Выберите категорию предсказания:", reply_markup=reply_markup)
            return

        # Если команда введена с аргументом, используем его
        category_name = context.args[0].lower()
        category_key = next((key for key, value in CATEGORIES.items() if value == category_name), None)

        if not category_key:
            await message.reply_text(
                "⚠️ Неверная категория! Выберите одну из:\n"
                "`деньги`, `удача`, `отношения`, `здоровье`",
                parse_mode="Markdown"
            )
            return

    category = CATEGORIES[category_key]
    logger.info(f"Генерируем предсказание на тему: {category}")

    # Получаем предсказание от OpenAI
    prediction = ask_openai(f"Сделай эзотерическое предсказание на тему {category}.")

    # Кнопка возврата в меню
    keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query:
        await query.message.edit_text(f"🔮 *Ваше предсказание на тему {category}:*\n\n{prediction}",
                                      parse_mode="Markdown",
                                      reply_markup=reply_markup)
    else:
        await message.reply_text(f"🔮 *Ваше предсказание на тему {category}:*\n\n{prediction}",
                                 parse_mode="Markdown",
                                 reply_markup=reply_markup)

async def fortune_callback(update: Update, context: CallbackContext) -> None:
    """Обрабатывает inline-кнопки предсказаний."""
    query = update.callback_query
    if not query:
        logger.error("Ошибка: fortune_callback вызван не через callback_query.")
        return

    await fortune(update, context)
