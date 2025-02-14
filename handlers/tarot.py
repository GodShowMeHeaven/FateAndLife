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
    """
    chat_id = update.effective_chat.id

    try:
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
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🎴 *Ваша карта Таро: {card}*\n\n{interpretation}",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Ошибка при вытягивании карты Таро: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="⚠️ Произошла ошибка, попробуйте снова."
        )

    finally:
        await asyncio.sleep(2)  # Задержка для защиты от спама
