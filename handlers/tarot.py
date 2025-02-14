from telegram import Update, CallbackQuery
from telegram.ext import CallbackContext
from services.tarot_service import get_tarot_interpretation
from keyboards.inline_buttons import tarot_keyboard, tarot_carousel_keyboard
from services.database import save_tarot_reading, get_tarot_history

async def tarot(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "🎴 *Выберите карту Таро или пролистайте карусель:*",
        reply_markup=tarot_carousel_keyboard,  # ✅ Передаем объект, а не вызываем функцию
        parse_mode="Markdown"
    )

async def tarot_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "draw_tarot":
        tarot_text = get_tarot_interpretation()
        save_tarot_reading(query.message.chat_id, "Случайная карта", tarot_text)
        await query.message.reply_text(f"🎴 *Ваша карта Таро:*\n\n{tarot_text}", reply_markup=tarot_keyboard)

async def tarot_history(update: Update, context: CallbackContext) -> None:
    history = get_tarot_history(update.message.chat_id)
    if not history:
        await update.message.reply_text("📜 История гаданий пуста!")
        return

    text = "📜 *История ваших гаданий:*\n"
    for card, interpretation, timestamp in history:
        text += f"🎴 {card} ({timestamp}):\n_{interpretation}_\n\n"

    await update.message.reply_text(text, parse_mode="Markdown")
