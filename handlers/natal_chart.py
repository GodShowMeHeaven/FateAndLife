from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown_v2
from services.openai_service import ask_openai
from keyboards.main_menu import main_menu_keyboard
import logging

logger = logging.getLogger(__name__)

async def message_of_the_day_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет пользователю послание на день."""
    if not update.effective_chat:
        logger.error("Отсутствует effective_chat в update")
        return
    query = update.callback_query
    try:
        prompt = "Дайте краткое вдохновляющее послание на день в стиле эзотерики, не длиннее 100 слов."
        message_text = await ask_openai(prompt)
        message_text = message_text[:4000]  # Ограничение длины Telegram
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu"),
             InlineKeyboardButton("🔄 Новое послание", callback_data="message_of_the_day")]
        ])
        if query:
            await query.answer()
            await query.message.edit_text(
                escape_markdown_v2(f"📜 Послание на день:\n{message_text}"),
                parse_mode="MarkdownV2",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                escape_markdown_v2(f"📜 Послание на день:\n{message_text}"),
                parse_mode="MarkdownV2",
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Ошибка получения послания: {e}")
        text = escape_markdown_v2("⚠️ Ошибка при получении послания. Попробуйте позже.")
        if query:
            await query.answer()
            await query.message.edit_text(text, parse_mode="MarkdownV2", reply_markup=main_menu_keyboard)
        else:
            await update.message.reply_text(text, parse_mode="MarkdownV2", reply_markup=main_menu_keyboard)