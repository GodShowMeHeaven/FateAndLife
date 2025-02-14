import asyncio
import logging
from telegram import Update
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)

def button_guard(func):
    """Декоратор для защиты кнопок (как inline, так и текстовых) от многократных нажатий."""
    async def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        user_id = update.effective_user.id
        is_callback = update.callback_query is not None

        # Проверяем, идет ли уже процесс обработки
        if context.user_data.get("processing", False):
            message = "⏳ Подождите, запрос обрабатывается..."
            logger.warning(f"⚠️ Блокировка повторного вызова для {user_id}")
            
            if is_callback:
                await update.callback_query.answer(message, show_alert=True)
            else:
                await update.message.reply_text(message)
            return

        logger.info(f"✅ Запускаем {func.__name__} для пользователя {user_id}")

        context.user_data["processing"] = True

        try:
            await func(update, context, *args, **kwargs)
        except Exception as e:
            logger.error(f"❌ Ошибка в {func.__name__}: {e}")
            if is_callback:
                await update.callback_query.message.reply_text("⚠️ Произошла ошибка, попробуйте снова.")
            else:
                await update.message.reply_text("⚠️ Произошла ошибка, попробуйте снова.")
        finally:
            context.user_data["processing"] = False  # ✅ Гарантированный сброс
            logger.info(f"✅ Завершение {func.__name__} для пользователя {user_id}")

            await asyncio.sleep(2)

    return wrapper
