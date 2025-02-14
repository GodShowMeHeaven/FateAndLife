import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.openai_service import ask_openai  # Используем OpenAI API

# Определяем доступные категории предсказаний
CATEGORIES = {
    "fortune_money": "финансовое предсказание",
    "fortune_luck": "предсказание удачи",
    "fortune_relationships": "любовное предсказание",
    "fortune_health": "предсказание здоровья"
}

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fortune_callback(update: Update, context: CallbackContext) -> None:
    """Генерирует предсказание на основе выбранной категории (через кнопку)"""
    query = update.callback_query
    chat_id = query.message.chat_id

    category_key = query.data  # Берем callback_data из кнопки

    if category_key not in CATEGORIES:
        logger.error(f"Получена неизвестная категория предсказания: {category_key}")
        await query.answer("⚠️ Ошибка! Попробуйте снова.", show_alert=True)
        return

    # Формируем запрос к OpenAI API
    prompt = (
        f"Создай предсказание на тему {CATEGORIES[category_key]}. "
        "Используй эзотерические образы, предсказательную стилистику и мистические метафоры."
    )

    try:
        # Запрашиваем предсказание у OpenAI API
        fortune_text = ask_openai(prompt)

        # Формируем клавиатуру с возвратом в меню
        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Отправляем предсказание пользователю
        await query.answer()
        await query.message.reply_text(f"🔮 *Ваше предсказание:*\n\n{fortune_text}",
                                       parse_mode="Markdown", reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Ошибка при получении предсказания: {e}")
        await query.message.reply_text("⚠️ Произошла ошибка при получении предсказания. Попробуйте позже.")

async def fortune_command(update: Update, context: CallbackContext) -> None:
    """Генерирует предсказание на основе команды /fortune <категория>"""
    if not context.args:
        await update.message.reply_text(
            "🔮 *Выберите тему предсказания:*\n"
            "💰 `/fortune деньги`  🍀 `/fortune удача`  💞 `/fortune отношения`  🏥 `/fortune здоровье`",
            parse_mode="Markdown"
        )
        return

    category_name = context.args[0].lower()
    category_key = f"fortune_{category_name}"

    if category_key not in CATEGORIES:
        await update.message.reply_text(
            "⚠️ Неверная категория! Выберите одну из:\n"
            "`/fortune деньги`, `/fortune удача`, `/fortune отношения`, `/fortune здоровье`",
            parse_mode="Markdown"
        )
        return

    # Формируем запрос к OpenAI API
    prompt = (
        f"Создай предсказание на тему {CATEGORIES[category_key]}. "
        "Используй эзотерические образы, предсказательную стилистику и мистические метафоры."
    )

    try:
        # Запрашиваем предсказание у OpenAI API
        fortune_text = ask_openai(prompt)

        # Формируем клавиатуру с возвратом в меню
        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Отправляем предсказание пользователю
        await update.message.reply_text(f"🔮 *Ваше предсказание:*\n\n{fortune_text}",
                                        parse_mode="Markdown", reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Ошибка при получении предсказания: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка при получении предсказания. Попробуйте позже.")
