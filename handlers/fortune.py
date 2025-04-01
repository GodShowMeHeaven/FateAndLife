import logging
import re  # Добавляем импорт re для escape_markdown_v2
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.openai_service import ask_openai
from utils.loading_messages import send_processing_message, replace_processing_message

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CATEGORIES = {
    "fortune_money": "деньги",
    "fortune_luck": "удача",
    "fortune_relationships": "отношения",
    "fortune_health": "здоровье",
    "💰 На деньги": "деньги",
    "🍀 На удачу": "удача",
    "💞 На отношения": "отношения",
    "🩺 На здоровье": "здоровье"
}

def escape_markdown_v2(text: str) -> str:
    """Экранирует все зарезервированные символы для MarkdownV2."""
    reserved_chars = r'([_*[\]()~`>#+-=|{}.!])'
    return re.sub(reserved_chars, r'\\\1', text)

async def fortune_callback(update: Update, context: CallbackContext) -> None:
    """
    Обрабатывает inline-кнопки предсказаний и текстовые команды.
    """
    query = update.callback_query
    chat_id = update.effective_chat.id
    processing_message = None

    if query:
        await query.answer()
        category = CATEGORIES.get(query.data, "неизвестно")
    else:
        text = update.message.text
        category = CATEGORIES.get(text, "неизвестно")

    if category == "неизвестно":
        logger.warning(f"Неизвестная категория предсказания: {text if not query else query.data}")
        await update.message.reply_text("⚠️ Ошибка: неизвестная категория предсказания.")
        return

    logger.info(f"Генерируем предсказание на тему: {category}")

    try:
        # Экранируем текст для начального сообщения
        processing_text = escape_markdown_v2(f"🔮 Подготавливаем ваше предсказание на тему {category}...")
        processing_message = await context.bot.send_message(chat_id, processing_text, parse_mode="MarkdownV2")
        
        # Получаем предсказание от OpenAI
        prediction = await ask_openai(f"Сделай эзотерическое предсказание на тему {category}.")
        logger.debug(f"Текст предсказания от OpenAI: {prediction[:500]}...")

        # Экранируем категорию и предсказание
        category_escaped = escape_markdown_v2(category)
        prediction_escaped = escape_markdown_v2(prediction)
        formatted_text = f"🔮 *Ваше предсказание на  {category_escaped}:*\n\n{prediction_escaped}"
        logger.debug(f"Экранированный текст для отправки: {formatted_text[:500]}...")

        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Заменяем сообщение
        await replace_processing_message(context, processing_message, formatted_text, reply_markup, parse_mode="MarkdownV2")

    except Exception as e:
        logger.error(f"Ошибка при генерации предсказания для {category}: {e}")
        error_message = escape_markdown_v2("⚠️ Произошла ошибка при генерации предсказания. Попробуйте позже.")
        if processing_message:
            await replace_processing_message(context, processing_message, error_message, parse_mode="MarkdownV2")
        else:
            await context.bot.send_message(chat_id, error_message, parse_mode="MarkdownV2")