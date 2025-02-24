from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
import logging
from datetime import date

logger = logging.getLogger(__name__)

async def start_calendar(update: Update, context: CallbackContext) -> None:
    """Отправляет пользователю inline-календарь для выбора даты."""
    chat_id = update.effective_chat.id

    # Определяем диапазон дат
    min_date = date(1900, 1, 1)  # Минимальная дата
    max_date = date.today()  # Сегодняшняя дата

    # Создаем календарь
    calendar = DetailedTelegramCalendar(min_date=min_date, max_date=max_date, locale="ru")
    keyboard = InlineKeyboardMarkup(calendar.build())  # ✅ Теперь это объект InlineKeyboardMarkup

    await context.bot.send_message(chat_id, "📅 Выберите год:", reply_markup=keyboard)

async def handle_calendar(update: Update, context: CallbackContext) -> None:
    """Обрабатывает выбор даты в inline-календаре."""
    query = update.callback_query
    chat_id = query.message.chat_id

    # Инициализируем календарь с тем же диапазоном дат
    calendar = DetailedTelegramCalendar(min_date=date(1900, 1, 1), max_date=date.today(), locale="ru")

    result, key, step = calendar.process(query.data)

    if not result and key:
        step_text = LSTEP.get(step, "дату")  # Защита от ошибки
        keyboard = InlineKeyboardMarkup(key)  # ✅ Теперь это объект InlineKeyboardMarkup
        await query.message.edit_text(f"📅 Выберите {step_text}:", reply_markup=keyboard)
    elif result:
        formatted_date = result.strftime("%d.%m.%Y")  # Приводим к нужному формату
        await query.message.edit_text(f"✅ Вы выбрали: {formatted_date}")
        context.user_data["selected_date"] = formatted_date  # Сохраняем дату в user_data

        # Запрашиваем следующую информацию (например, время)
        await context.bot.send_message(chat_id, "⏰ Введите время рождения в формате ЧЧ:ММ:")
