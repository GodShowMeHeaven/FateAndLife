import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup  # ✅ Добавлены недостающие импорты
from telegram.ext import CallbackContext
from services.openai_service import ask_openai  # Используем OpenAI API для генерации предсказаний

# Определяем доступные категории предсказаний
CATEGORIES = {
    "деньги": "финансовое предсказание",
    "удача": "предсказание удачи",
    "отношения": "любовное предсказание",
    "здоровье": "предсказание здоровья"
}

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fortune(update: Update, context: CallbackContext) -> None:
    """Генерирует предсказание на основе выбранной категории с помощью OpenAI API"""
    query = update.callback_query
    chat_id = query.message.chat_id if query else update.message.chat_id

    # Определяем категорию
    if query:
        category = query.data.replace("fortune_", "")  # Убираем "fortune_" из callback_data
    elif context.args:
        category = context.args[0].lower()
    else:
        await update.message.reply_text(
            "🔮 *Введите категорию предсказания:*\n"
            "`/fortune деньги`  `/fortune удача`  `/fortune отношения`  `/fortune здоровье`",
            parse_mode="Markdown"
        )
        return

    # Проверяем, является ли введенная категория допустимой
    if category not in CATEGORIES:
        await update.message.reply_text(
            "⚠️ Неверная категория! Выберите одну из:\n"
            "`деньги`, `удача`, `отношения`, `здоровье`",
            parse_mode="Markdown"
        )
        return

    # Формируем запрос к OpenAI API
    prompt = (
        f"Создай предсказание на тему {CATEGORIES[category]}. "
        "Используй эзотерические образы, предсказательную стилистику и мистические метафоры."
    )

    try:
        # Запрашиваем предсказание у OpenAI API
        fortune_text = ask_openai(prompt)

        # Формируем клавиатуру с возвратом в меню
        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Отправляем предсказание пользователю
        if query:
            await query.answer()
            await query.message.reply_text(f"🔮 *Ваше предсказание:*\n\n{fortune_text}",
                                           parse_mode="Markdown", reply_markup=reply_markup)
        else:
            await update.message.reply_text(f"🔮 *Ваше предсказание:*\n\n{fortune_text}",
                                            parse_mode="Markdown", reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Ошибка при получении предсказания: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка при получении предсказания. Попробуйте позже.")
