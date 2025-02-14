import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.openai_service import ask_openai

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def message_of_the_day_callback(update: Update, context: CallbackContext) -> None:
    """Генерирует мотивирующее послание с помощью OpenAI API"""
    query = update.callback_query if update.callback_query else None
    chat_id = query.message.chat_id if query else update.message.chat_id

    prompt = (
        "Сгенерируй вдохновляющее послание на день/неделю. "
        "Добавь позитивные аффирмации, эзотерические образы и советы для достижения гармонии."
    )

    try:
        message_text = ask_openai(prompt)

        # Кнопка возврата в меню
        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if query:
            await query.answer()
            await query.message.reply_text(f"✨ *Послание на день* ✨\n\n{message_text}", 
                                           parse_mode="Markdown", 
                                           reply_markup=reply_markup)
        else:
            await update.message.reply_text(f"✨ *Послание на день* ✨\n\n{message_text}", 
                                            parse_mode="Markdown", 
                                            reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Ошибка при получении послания: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка. Попробуйте позже.")
