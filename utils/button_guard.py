import asyncio
import logging
from telegram import Update
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)

def button_guard(func):
    """Декоратор для защиты от многократных нажатий (работает и с inline, и с текстовыми кнопками)."""
    async def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        user_id = update.effective_user.id
        is_callback = update.callback_query is not None

        if context.user_data.get("processing", False):
            message = "⏳ Подождите, запрос обрабатывается..."
            logger.warning(f"⚠️ Блокировка повторного вызова {func.__name__} для пользователя {user_id}")

            if is_callback:
                await update.callback_query.answer(message, show_alert=True)
            elif update.message:
                await update.message.reply_text(message)
            return

        logger.info(f"✅ Запускаем {func.__name__} для пользователя {user_id}")

        context.user_data["processing"] = True
        
        try:
            await func(update, context, *args, **kwargs)
        except Exception as e:
            logger.error(f"❌ Ошибка в {func.__name__}: {e}")
            if update.message:
                await update.message.reply_text("⚠️ Ошибка, попробуйте снова.")
            elif update.callback_query:
                await update.callback_query.message.reply_text("⚠️ Ошибка, попробуйте снова.")

        finally:
            await asyncio.sleep(1)  # Уменьшено с 2 до 1 секунды
            context.user_data["processing"] = False
            logger.info(f"✅ Завершение {func.__name__} для пользователя {user_id}")

    return wrapper