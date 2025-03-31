import logging
import re  # Добавлен импорт re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.openai_service import ask_openai
from utils.loading_messages import send_processing_message, replace_processing_message

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def escape_markdown_v2(text: str) -> str:
    """Экранирует все зарезервированные символы для MarkdownV2."""
    reserved_chars = r'([_*[\]()~`>#+-=|{}.!])'
    return re.sub(reserved_chars, r'\\\1', text)

async def message_of_the_day_callback(update: Update, context: CallbackContext) -> None:
    """Генерирует мотивирующее послание с помощью OpenAI API."""
    query = update.callback_query if update.callback_query else None
    chat_id = query.message.chat_id if query else update.effective_chat.id
    processing_message = None  # Инициализация переменной

    prompt = (
        "Создай вдохновляющее послание на день, наполненное мистическими и эзотерическими образами. "
        "Используй язык, который вдохновляет и пробуждает интуицию. "
        "Добавь древнюю мудрость, метафоры природы, элементы астрологии или карт Таро. "
        "Предложи совет, который поможет человеку найти гармонию, уверенность и осознанность в этот день. "
        "Послание должно звучать как пророчество или тайное знание, направленное лично к читающему. "
        "Избегай клише и делай каждое послание уникальным и запоминающимся."
    )

    try:
        logger.info(f"Запрос к OpenAI для генерации послания на день...")
        
        # Отправляем техническое сообщение о подготовке
        processing_message = await context.bot.send_message(chat_id, "✨ Подготавливаем ваше послание на день...")
        
        message_text = await ask_openai(prompt)  # Оставляем await, так как функция асинхронная в других файлах

        # Экранируем текст для MarkdownV2
        message_text_escaped = escape_markdown_v2(message_text)
        formatted_text = f"✨ *Послание на день* ✨\n\n{message_text_escaped}"
        logger.debug(f"Отправляемый текст: {formatted_text}")

        # Кнопка возврата в меню
        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Заменяем техническое сообщение на итоговый результат
        await replace_processing_message(context, processing_message, formatted_text, reply_markup, parse_mode="MarkdownV2")
    
    except Exception as e:
        logger.error(f"Ошибка при получении послания: {e}")
        error_message = escape_markdown_v2("⚠️ Произошла ошибка. Попробуйте позже.")
        
        if processing_message:
            await replace_processing_message(context, processing_message, error_message, parse_mode="MarkdownV2")
        else:
            await context.bot.send_message(chat_id, error_message, parse_mode="MarkdownV2")