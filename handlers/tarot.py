from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.tarot_service import get_tarot_interpretation, generate_tarot_image
from services.database import save_tarot_reading
from utils.button_guard import button_guard  # ✅ Защита от спама
import logging
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@button_guard
async def tarot(update: Update, context: CallbackContext) -> None:
    """Вытягивает случайную карту Таро, отправляет изображение и интерпретацию с защитой от спама"""
    query = update.callback_query
    chat_id = update.effective_chat.id if update.effective_chat else update.message.chat_id

    # Проверяем, вызвана ли функция через кнопку или текстовую команду
    if query:
        try:
            await query.answer()  # ✅ Проверяем, что query не None
        except Exception as e:
            logger.warning(f"Ошибка при обработке query.answer(): {e}")
    else:
        logger.info(f"Пользователь {update.effective_user.id} вызвал Таро через команду")

    # Блокируем повторные запросы
    if context.user_data.get("processing", False):
        await context.bot.send_message(chat_id=chat_id, text="⏳ Подождите, выполняется предыдущее гадание...")
        return

    context.user_data["processing"] = True  # ✅ Устанавливаем флаг выполнения

    try:
        logger.info("Вытягиваем случайную карту Таро...")
        card, interpretation = get_tarot_interpretation()  # Получаем карту и её интерпретацию
        image_url = generate_tarot_image(card)  # Генерируем изображение карты

        # Сохраняем гадание в базе данных
        save_tarot_reading(chat_id, card, interpretation)

        # Формируем клавиатуру с кнопками
        keyboard = [
            [InlineKeyboardButton("🔄 Вытянуть новую карту", callback_data="draw_tarot")],
            [InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Если генерация изображения удалась, отправляем картинку
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
        await asyncio.sleep(2)  # ✅ Задержка для защиты от спама
        context.user_data["processing"] = False  # ✅ Сбрасываем флаг выполнения

@button_guard
async def tarot_callback(update: Update, context: CallbackContext) -> None:
    """Обрабатывает кнопку 'Вытянуть новую карту'"""
    query = update.callback_query

    if query:
        try:
            await query.answer()
        except Exception as e:
            logger.warning(f"Ошибка при query.answer(): {e}")

        if query.data == "draw_tarot":
            logger.info(f"Пользователь {query.from_user.id} нажал '🔄 Вытянуть новую карту'.")
            await tarot(update, context)
    else:
        logger.error("Ошибка: tarot_callback вызван без callback_query.")
