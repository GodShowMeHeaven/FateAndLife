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
    chat_id = query.message.chat_id if query else update.effective_chat.id

    prompt = (
        "Создай вдохновляющее послание на день. "
        "Добавь позитивные аффирмации, эзотерические образы и советы для достижения гармонии."
    )

    try:
        logger.info(f"Запрос к OpenAI для генерации послания на день...")
        message_text = ask_openai(prompt)  # ❌ Убрали `await`, так как `ask_openai` – синхронная функция

        # Кнопка возврата в меню
        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Проверяем, вызов через callback или команду
        if query:
            await query.answer()
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"✨ *Послание на день* ✨\n\n{message_text}",
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"✨ *Послание на день* ✨\n\n{message_text}",
                parse_mode="Markdown",
                reply_markup=reply_markup
            )

    except Exception as e:
        logger.error(f"Ошибка при получении послания: {e}")
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Произошла ошибка. Попробуйте позже.")
