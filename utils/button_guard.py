import asyncio
import logging
from telegram import Update
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)

def button_guard(func):
    """Декоратор для защиты кнопок от многократных нажатий."""
    async def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        query = update.callback_query
        user_id = update.effective_user.id

        # Проверяем, идет ли уже процесс обработки кнопки
        if context.user_data.get("processing", False):
            await query.answer("⏳ Подождите, запрос обрабатывается...", show_alert=True)
            return

        context.user_data["processing"] = True  # ✅ Устанавливаем флаг выполнения

        try:
            await func(update, context, *args, **kwargs)  # Выполняем основную функцию
        except Exception as e:
            logger.error(f"Ошибка при обработке кнопки: {e}")
            await update.effective_message.reply_text("⚠️ Произошла ошибка, попробуйте снова.")
        finally:
            await asyncio.sleep(2)  # ✅ Небольшая задержка, чтобы избежать спама
            context.user_data["processing"] = False  # ✅ Сбрасываем флаг выполнения

    return wrapper
