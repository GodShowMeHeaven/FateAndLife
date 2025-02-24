from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.natal_chart_service import get_natal_chart
from utils.loading_messages import send_processing_message, replace_processing_message  # ✅ Импорт функций загрузки
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def natal_chart(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 4:
        await update.message.reply_text(
            "📜 *Введите данные для натальной карты в формате:*\n"
            "`/natal_chart Имя ДД.ММ.ГГГГ ЧЧ:ММ Город`",
            parse_mode="Markdown"
        )
        return

    name = context.args[0]
    birth_date = context.args[1]
    birth_time = context.args[2]
    birth_place = " ".join(context.args[3:])  # Поддержка названий с пробелами
    processing_message = None  # Инициализация переменной

    try:
        # Отправляем техническое сообщение о подготовке
        processing_message = await send_processing_message(update, f"🌌 Подготавливаем вашу натальную карту для {name}...")

        natal_chart_text = get_natal_chart(name, birth_date, birth_time, birth_place)

        formatted_chart = (
            f"🌌 *Анализ натальной карты для {name}*\n"
            "__________________________\n"
            f"{natal_chart_text}\n"
            "__________________________\n"
            "✨ *Совет:* Используйте знания натальной карты для развития!"
        )

        # Добавляем кнопку "🔙 Вернуться в меню"
        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Заменяем техническое сообщение на итоговый результат
        await replace_processing_message(context, processing_message, formatted_chart, reply_markup)

    except Exception as e:
        logger.error(f"Ошибка при обработке натальной карты: {e}")
        
        if processing_message:
            await replace_processing_message(context, processing_message, "⚠️ Произошла ошибка при обработке запроса. Попробуйте позже.")
        else:
            await update.message.reply_text(
                "⚠️ Произошла ошибка при обработке запроса. Попробуйте позже.",
                parse_mode="Markdown"
            )