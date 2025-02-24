from telegram import Update
from telegram.ext import CallbackContext
from telegram_bot_calendar import WMonthTelegramCalendar  # ✅ Используем WMonthTelegramCalendar
import logging
from datetime import date

logger = logging.getLogger(__name__)

async def start_calendar(update: Update, context: CallbackContext) -> None:
    """Отправляет inline-календарь для выбора даты."""
    chat_id = update.effective_chat.id

    min_date = date(1900, 1, 1)
    max_date = date.today()

    calendar = WMonthTelegramCalendar(min_date=min_date, max_date=max_date, locale="ru")
    keyboard = calendar.create()

    logger.info("📅 Отправляем календарь.")

    await context.bot.send_message(chat_id, "📅 Выберите дату:", reply_markup=keyboard)

async def handle_calendar(update: Update, context: CallbackContext) -> None:
    """Обрабатывает выбор даты в inline-календаре."""
    query = update.callback_query
    chat_id = query.message.chat_id

    logger.info(f"📥 `handle_calendar()` ВЫЗВАН! Callback: {query.data}")
    await query.answer()  # ✅ Подтверждаем нажатие кнопки!

    calendar = WMonthTelegramCalendar(locale="ru")

    result, key = calendar.process(query.data)

    if not result and key:
        logger.info("📅 Обновляем календарь.")
        await query.message.edit_text("📅 Выберите дату:", reply_markup=key)
    elif result:
        formatted_date = result.strftime("%d.%m.%Y")
        logger.info(f"✅ Дата выбрана: {formatted_date}")

        await query.message.edit_text(f"✅ Вы выбрали: {formatted_date}")
        context.user_data["selected_date"] = formatted_date

        await context.bot.send_message(chat_id, "⏰ Введите время рождения в формате ЧЧ:ММ:")
