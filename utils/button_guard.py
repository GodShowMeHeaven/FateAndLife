import asyncio
import logging
from telegram import Update
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)

def button_guard(func):
    """Декоратор для защиты кнопок от многократных нажатий."""
    async def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        user_id = update.effective_user.id
        
        # Проверяем, идет ли уже процесс обработки
        if context.user_data.get("processing", False):
            message = "⏳ Подождите, запрос обрабатывается..."
            
            # Для inline кнопок
            if update.callback_query:
                await update.callback_query.answer(message, show_alert=True)
                return
            # Для текстовых кнопок
            else:
                await update.effective_message.reply_text(message)
                return

        context.user_data["processing"] = True

        try:
            await func(update, context, *args, **kwargs)
        except Exception as e:
            logger.error(f"Ошибка при обработке кнопки: {e}")
            await update.effective_message.reply_text("⚠️ Произошла ошибка, попробуйте снова.")
        finally:
            await asyncio.sleep(2)
            context.user_data["processing"] = False

    return wrapper