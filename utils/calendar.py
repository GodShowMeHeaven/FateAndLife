from telegram import Update
from telegram.ext import CallbackContext
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
import logging
from datetime import date

logger = logging.getLogger(__name__)

async def start_calendar(update: Update, context: CallbackContext) -> None:
    """Отправляет inline-календарь для выбора даты."""
    chat_id = update.effective_chat.id

    min_date = date(1900, 1, 1)
    max_date = date.today()

    calendar = DetailedTelegramCalendar(min_date=min_date, max_date=max_date, locale="ru")
    keyboard, step = calendar.build()

    logger.info(f"📅 Отправляем календарь. Шаг: {LSTEP.get(step, 'год')}")

    await context.bot.send_message(chat_id, f"📅 Выберите {LSTEP.get(step, 'год')}:", reply_markup=keyboard)

async def handle_calendar(update: Update, context: CallbackContext) -> None:
    """Обрабатывает выбор даты в inline-календаре."""
    query = update.callback_query
    chat_id = query.message.chat_id

    logger.info(f"📥 `handle_calendar()` ВЫЗВАН!")  # ✅ Проверяем, вызывается ли обработчик
    logger.info(f"🔄 Получен callback: {query.data}")  
    await query.answer()  # ✅ Подтверждаем нажатие кнопки!

    if not query.data or "calendar_" not in query.data:  # ✅ Исправленный фильтр
        logger.warning(f"⚠️ Игнорируем callback: {query.data}")
        return

    calendar = DetailedTelegramCalendar(min_date=date(1900, 1, 1), max_date=date.today(), locale="ru")

    result, key, step = calendar.process(query.data)

    if not result and key:
        step_text = LSTEP.get(step, "год")
        logger.info(f"📅 Обновляем календарь. Новый шаг: {step_text}")

        await query.message.edit_text(f"📅 Выберите {step_text}:", reply_markup=key)
    elif result:
        formatted_date = result.strftime("%d.%m.%Y")
        logger.info(f"✅ Дата выбрана: {formatted_date}")

        await query.message.edit_text(f"✅ Вы выбрали: {formatted_date}")
        context.user_data["selected_date"] = formatted_date

        await context.bot.send_message(chat_id, "⏰ Введите время рождения в формате ЧЧ:ММ:")
