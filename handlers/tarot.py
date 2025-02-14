from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.tarot_service import get_tarot_interpretation, generate_tarot_image
from services.database import save_tarot_reading

async def tarot(update: Update, context: CallbackContext) -> None:
    """Вытягивает случайную карту Таро, отправляет изображение и интерпретацию"""
    query = update.callback_query
    if query:
        await query.answer()

    card, interpretation = get_tarot_interpretation()  # Получаем карту и её интерпретацию
    image_url = generate_tarot_image(card)  # Генерируем изображение карты

    # Сохраняем гадание в базе данных
    save_tarot_reading(update.effective_user.id, card, interpretation)

    # Формируем клавиатуру с кнопками
    keyboard = [
        [InlineKeyboardButton("🔄 Вытянуть новую карту", callback_data="draw_tarot")],
        [InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем изображение карты
    await update.message.reply_photo(photo=image_url)

    # Отправляем текстовое объяснение
    await update.message.reply_text(
        f"🎴 *Ваша карта Таро: {card}*\n\n{interpretation}",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# Обработчик кнопки "🔄 Вытянуть новую карту"
async def tarot_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if query and query.data == "draw_tarot":
        await tarot(update, context)
