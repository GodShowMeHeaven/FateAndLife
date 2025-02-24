from telegram import Update
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

    # Создаем календарь с `calendar_id`
    calendar, step = DetailedTelegramCalendar(calendar_id=1, min_date=min_date, max_date=max_date, locale="ru").build()

    logger.info(f"📅 Отправляем календарь. Шаг: {LSTEP.get(step, 'год')}")  # ✅ Логируем отправку

    await context.bot.send_message(chat_id, f"📅 Выберите {LSTEP.get(step, 'год')}:", reply_markup=calendar)

async def handle_calendar(update: Update, context: CallbackContext) -> None:
    """Обрабатывает выбор даты в inline-календаре."""
    query = update.callback_query
    chat_id = query.message.chat_id

    logger.info(f"🔄 Получен callback: {query.data}")  # ✅ Логируем callback_data

    # Проверяем, что callback относится к календарю
    if not DetailedTelegramCalendar.func(calendar_id=1)(query):
        logger.warning(f"⚠️ Игнорируем callback: {query.data}")
        return

    # Инициализируем календарь с `calendar_id`
    calendar = DetailedTelegramCalendar(calendar_id=1, min_date=date(1900, 1, 1), max_date=date.today(), locale="ru")

    result, key, step = calendar.process(query.data)

    if not result and key:
        step_text = LSTEP.get(step, "дату")  # ✅ Проверка наличия ключа
        logger.info(f"📅 Обновляем календарь. Новый шаг: {step_text}")  # ✅ Логируем обновление

        await query.message.edit_text(f"📅 Выберите {step_text}:", reply_markup=key)
    elif result:
        formatted_date = result.strftime("%d.%m.%Y")  # Приводим к нужному формату
        logger.info(f"✅ Дата выбрана: {formatted_date}")  # ✅ Логируем выбор даты

        await query.message.edit_text(f"✅ Вы выбрали: {formatted_date}")
        context.user_data["selected_date"] = formatted_date  # Сохраняем дату в user_data

        # Запрашиваем следующую информацию (например, время)
        await context.bot.send_message(chat_id, "⏰ Введите время рождения в формате ЧЧ:ММ:")
