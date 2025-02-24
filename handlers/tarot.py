import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.tarot_service import get_tarot_interpretation, generate_tarot_image
from services.database import save_tarot_reading
from utils.button_guard import button_guard  # ✅ Защита от спама
from utils.loading_messages import send_processing_message, replace_processing_message  # ✅ Импорт функций загрузки

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@button_guard
async def tarot(update: Update, context: CallbackContext) -> None:
    """Вытягивает случайную карту Таро и отправляет интерпретацию."""
    chat_id = update.effective_chat.id
    logger.info(f"🔮 tarot() запущен для пользователя {chat_id}")
    processing_message = None  # Инициализация переменной

    try:
        # Отправляем техническое сообщение о подготовке
        processing_message = await send_processing_message(update, "🎴 Подготавливаем вашу карту Таро...")
        
        # Таймаут на получение карты
        for attempt in range(2):  # ✅ Делаем 2 попытки
            try:
                logger.info(f"🎴 Генерация карты Таро... (Попытка {attempt+1})")
                card, interpretation = await asyncio.wait_for(
                    asyncio.to_thread(get_tarot_interpretation), timeout=30  # ✅ Увеличили таймаут
                )
                logger.info(f"🎴 Вытянута карта: {card}")
                break  # ✅ Если удалось, выходим из цикла
            except asyncio.TimeoutError:
                logger.warning(f"⏳ Время ожидания get_tarot_interpretation() истекло (Попытка {attempt+1})")
                if attempt == 1:  # Если вторая попытка тоже не удалась
                    await replace_processing_message(context, processing_message, "⚠️ Ошибка: не удалось получить карту.")
                    return

        # Таймаут на генерацию изображения
        try:
            logger.info("📸 Генерация изображения...")
            image_url = await asyncio.wait_for(
                asyncio.to_thread(generate_tarot_image, card), timeout=25  # ✅ Увеличили таймаут
            )
            if image_url:
                logger.info("📸 Изображение успешно сгенерировано")
        except asyncio.TimeoutError:
            logger.warning("⏳ Время ожидания generate_tarot_image() истекло")
            image_url = None  # Продолжаем без изображения

        # Сохраняем результат гадания
        logger.info("💾 Сохранение результата в базе данных...")
        save_tarot_reading(chat_id, card, interpretation)

        # Формируем inline-кнопки
        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Отправляем фото, если оно есть
        if image_url:
            logger.info("📤 Отправка изображения...")
            await context.bot.send_photo(chat_id=chat_id, photo=image_url)

        # Отправляем текстовое объяснение карты
        logger.info("📤 Отправка сообщения с картой...")
        await replace_processing_message(context, processing_message, f"🎴 *Ваша карта Таро: {card}*\n\n{interpretation}", reply_markup)

    except Exception as e:
        logger.error(f"❌ Ошибка в tarot(): {e}")
        
        if processing_message:
            await replace_processing_message(context, processing_message, "⚠️ Ошибка, попробуйте снова.")
        else:
            await update.message.reply_text("⚠️ Ошибка, попробуйте снова.")

    finally:
        context.user_data["processing"] = False  # ✅ Гарантированный сброс
        logger.info(f"✅ tarot() завершен для пользователя {chat_id}")
        await asyncio.sleep(2)