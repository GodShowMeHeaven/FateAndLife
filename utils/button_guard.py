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

        # Проверяем, идет ли уже процесс обработки
        if context.user_data.get("processing", False):
            message = "⏳ Подождите, запрос обрабатывается..."
            logger.warning(f"⚠️ Блокировка повторного вызова {func.__name__} для пользователя {user_id}")

            # Для inline-кнопок
            if is_callback:
                await update.callback_query.answer(message, show_alert=True)
            # Для текстовых кнопок
            elif update.message:
                await update.message.reply_text(message)
            return

        logger.info(f"✅ Запускаем {func.__name__} для пользователя {user_id}")

        # Устанавливаем флаг перед вызовом функции
        context.user_data["processing"] = True  
        
        try:
            await func(update, context, *args, **kwargs)  # Вызываем основную функцию
        except Exception as e:
            logger.error(f"❌ Ошибка в {func.__name__}: {e}")
            error_message = "⚠️ Ошибка, попробуйте снова."
            
            if is_callback:
                await update.callback_query.message.reply_text(error_message)
            elif update.message:
                await update.message.reply_text(error_message)

        finally:
            await asyncio.sleep(2)  # Защита от спама
            context.user_data["processing"] = False  # Гарантированный сброс флага
            logger.info(f"✅ Завершение {func.__name__} для пользователя {user_id}")

    return wrapper