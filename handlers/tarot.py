import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.tarot_service import get_tarot_interpretation, generate_tarot_image
from services.database import save_tarot_reading
from utils.button_guard import button_guard  # ✅ Защита от спама

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@button_guard
async def tarot(update: Update, context: CallbackContext) -> None:
    """
    Вытягивает случайную карту Таро, отправляет изображение и интерпретацию.
    Доступно ТОЛЬКО через команду /tarot или текстовую кнопку "🎴 Карты Таро".
    """
    chat_id = update.effective_chat.id  # ✅ Универсальный способ получения chat_id
    query = update.callback_query  # Проверяем, был ли вызов через callback_query

    try:
        if query:  # Если вызов был через inline-кнопку, игнорируем
            logger.warning("Ошибка: tarot() вызван через callback_query, а должен только через команду /tarot")
            return

        logger.info(f"Пользователь {chat_id} выбрал Таро. Вытягиваем карту...")
        card, interpretation = get_tarot_interpretation()
        image_url = generate_tarot_image(card)

        # Сохраняем гадание в базе данных
        save_tarot_reading(chat_id, card, interpretation)

        # Формируем inline-кнопки
        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Если есть изображение карты, отправляем его
        if image_url:
            await context.bot.send_photo(chat_id=chat_id, photo=image_url)

        # Отправляем текстовое объяснение карты
        await update.message.reply_text(
            f"🎴 *Ваша карта Таро: {card}*\n\n{interpretation}",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Ошибка при вытягивании карты Таро: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка, попробуйте снова.")

    finally:
        await asyncio.sleep(2)  # ✅ Задержка для защиты от спама
        context.user_data["processing"] = False  # ✅ Сбрасываем флаг выполнения