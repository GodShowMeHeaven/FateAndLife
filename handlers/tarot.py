from telegram import Update, CallbackQuery
from telegram.ext import CallbackContext
from services.tarot_service import get_tarot_interpretation
from keyboards.inline_buttons import tarot_keyboard, tarot_carousel_keyboard
from services.database import save_tarot_reading, get_tarot_history

tarot_index = 0  # Индекс карты в карусели

async def tarot(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "🎴 *Выберите карту Таро или пролистайте карусель:*",
        reply_markup=tarot_carousel_keyboard(),
        parse_mode="Markdown"
    )

async def tarot_callback(update: Update, context: CallbackContext) -> None:
    global tarot_index
    query = update.callback_query
    await query.answer()

    if query.data == "draw_tarot":
        tarot_text = get_tarot_interpretation()
        save_tarot_reading(query.message.chat_id, "Случайная карта", tarot_text)  # Сохраняем гадание
        await query.edit_message_text(f"🎴 *Ваша карта Таро:*\n{tarot_text}", parse_mode="Markdown")
        
    elif query.data == "prev_tarot":
        tarot_index = (tarot_index - 1) % len(context.user_data.get("tarot_deck", []))
    elif query.data == "next_tarot":
        tarot_index = (tarot_index + 1) % len(context.user_data.get("tarot_deck", []))

    tarot_card = context.user_data.get("tarot_deck", [])[tarot_index]
    await query.edit_message_text(f"🎴 *Карта Таро:* {tarot_card}", reply_markup=tarot_carousel_keyboard(), parse_mode="Markdown")

    # После работы с картой Таро возвращаем пользователя в главное меню
    await query.message.reply_text("Выберите раздел:", reply_markup=tarot_keyboard)  # Возвращаем главное меню

async def tarot_history(update: Update, context: CallbackContext) -> None:
    history = get_tarot_history(update.message.chat_id)
    if not history:
        await update.message.reply_text("📜 История гаданий пуста!")
        return

    text = "📜 *История ваших гаданий:*\n"
    for card, interpretation, timestamp in history:
        text += f"🎴 {card} ({timestamp}):\n_{interpretation}_\n\n"

    await update.message.reply_text(text, parse_mode="Markdown")
