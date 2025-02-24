import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.openai_service import ask_openai
from utils.loading_messages import send_processing_message, replace_processing_message  # ✅ Импорт функций загрузки

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def message_of_the_day_callback(update: Update, context: CallbackContext) -> None:
    """Генерирует мотивирующее послание с помощью OpenAI API"""
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
        
        message_text = ask_openai(prompt)  # ❌ Убрали `await`, так как `ask_openai` – синхронная функция

        # Кнопка возврата в меню
        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Заменяем техническое сообщение на итоговый результат
        await replace_processing_message(context, processing_message, f"✨ *Послание на день* ✨\n\n{message_text}", reply_markup)
    
    except Exception as e:
        logger.error(f"Ошибка при получении послания: {e}")
        
        if processing_message:
            await replace_processing_message(context, processing_message, "⚠️ Произошла ошибка. Попробуйте позже.")
        else:
            await context.bot.send_message(chat_id, "⚠️ Произошла ошибка. Попробуйте позже.")
