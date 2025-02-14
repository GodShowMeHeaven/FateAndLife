from telegram import Update, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.tarot_service import get_tarot_interpretation
from keyboards.inline_buttons import tarot_keyboard, tarot_carousel_keyboard
from services.database import save_tarot_reading, get_tarot_history

tarot_index = 0  # Индекс карты в карусели

async def tarot(update: Update, context: CallbackContext) -> None:
    """Отображает меню карт Таро"""
    await update.message.reply_text(
        "🎴 *Выберите карту Таро или пролистайте карусель:*",
        reply_markup=tarot_carousel_keyboard,  # ✅ Передаем объект, а не вызываем функцию
        parse_mode="Markdown"
    )

async def tarot_callback(update: Update, context: CallbackContext) -> None:
    """Обрабатывает нажатия inline-кнопок для Таро"""
    global tarot_index
    query = update.callback_query
    await query.answer()

    if query.data == "draw_tarot":
        tarot_text = get_tarot_interpretation()  # ✅ Теперь вызов асинхронной функции
        save_tarot_reading(query.message.chat_id, "Случайная карта", tarot_text)  # ✅ Сохраняем гадание
        
        # Вместо редактирования отправляем новое сообщение с кнопками
        await query.message.reply_text(f"🎴 *Ваша карта Таро:*\n\n{tarot_text}",
                                       parse_mode="Markdown",
                                       reply_markup=tarot_keyboard)  # ✅ Добавляем меню

    elif query.data == "prev_tarot":
        tarot_index = (tarot_index - 1) % len(context.user_data.get("tarot_deck", []))
    elif query.data == "next_tarot":
        tarot_index = (tarot_index + 1) % len(context.user_data.get("tarot_deck", []))

    tarot_card = context.user_data.get("tarot_deck", [])[tarot_index]
    await query.message.reply_text(f"🎴 *Карта Таро:* {tarot_card}",
                                   reply_markup=tarot_carousel_keyboard,  # ✅ Передаем объект, а не вызываем функцию
                                   parse_mode="Markdown")

async def tarot_history(update: Update, context: CallbackContext) -> None:
    """Выводит историю гаданий пользователя"""
    history = get_tarot_history(update.message.chat_id)
    
    if not history:
        await update.message.reply_text("📜 История гаданий пуста!")
        return

    text = "📜 *История ваших гаданий:*\n"
    for card, interpretation, timestamp in history:
        text += f"🎴 {card} ({timestamp}):\n_{interpretation}_\n\n"

    await update.message.reply_text(text, parse_mode="Markdown")
