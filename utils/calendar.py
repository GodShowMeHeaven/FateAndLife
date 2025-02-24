import logging
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram_bot_calendar import WMonthTelegramCalendar
import json
from datetime import date

logger = logging.getLogger(__name__)

async def start_calendar(update: Update, context: CallbackContext) -> None:
    """Отправляет inline-календарь для выбора даты."""
    try:
        chat_id = update.effective_chat.id
        calendar = WMonthTelegramCalendar(locale="ru")
        await context.bot.send_message(
            chat_id=chat_id,
            text="📅 Выберите дату:",
            reply_markup=calendar.build()[0]
        )
        logger.info(f"📅 Календарь отправлен для чата {chat_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка при создании календаря: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ Произошла ошибка при создании календаря. Попробуйте позже."
        )

async def handle_calendar(update: Update, context: CallbackContext) -> None:
    """Обрабатывает выбор даты в inline-календаре и передает её в соответствующий обработчик."""
    query = update.callback_query
    if not query:
        return

    logger.info(f"📥 Получен callback данные: {query.data}")
    await query.answer()

    try:
        calendar = WMonthTelegramCalendar(locale="ru")
        data = calendar.process(query.data)
        logger.debug(f"Результат обработки календаря: {data}")

        # Распаковываем три значения
        selected, keyboard_json, step = data

        if selected:
            # Дата выбрана
            formatted_date = selected.strftime("%d.%m.%Y")
            context.user_data["selected_date"] = formatted_date

            # Проверяем, есть ли `query.message`
            chat_id = update.effective_chat.id
            if query.message and query.message.text:
                await query.edit_message_text(text=f"✅ Вы выбрали дату: {formatted_date}")
            else:
                await context.bot.send_message(chat_id, text=f"✅ Вы выбрали дату: {formatted_date}")

            # Передача даты в нужный обработчик в зависимости от контекста
            if context.user_data.get("awaiting_numerology"):
                from handlers.numerology import process_numerology
                await process_numerology(update, context, formatted_date)
            elif context.user_data.get("awaiting_natal_chart"):
                from handlers.natal_chart import natal_chart
                await natal_chart(update, context, formatted_date)
            elif context.user_data.get("awaiting_compatibility"):
                from handlers.compatibility import compatibility_natal
                await compatibility_natal(update, context, formatted_date)

            # Очищаем флаги после обработки
            context.user_data.pop("awaiting_numerology", None)
            context.user_data.pop("awaiting_natal_chart", None)
            context.user_data.pop("awaiting_compatibility", None)
        else:
            # Дата не выбрана, показываем календарь
            keyboard = InlineKeyboardMarkup.from_dict(json.loads(keyboard_json)) if isinstance(keyboard_json, str) else keyboard_json
            if query.message and query.message.text:
                await query.edit_message_text(text="📅 Выберите дату:", reply_markup=keyboard)
            else:
                await context.bot.send_message(chat_id, text="📅 Выберите дату:", reply_markup=keyboard)

    except Exception as e:
        logger.error(f"❌ Ошибка при обработке календаря: {str(e)}")
        chat_id = update.effective_chat.id
        try:
            if query.message and query.message.text:
                await query.edit_message_text(
                    text="❌ Произошла ошибка. Попробуйте выбрать дату заново.",
                    reply_markup=calendar.build()[0]
                )
            else:
                await context.bot.send_message(chat_id, text="❌ Произошла ошибка. Попробуйте выбрать дату заново.", reply_markup=calendar.build()[0])
        except Exception as e2:
            logger.error(f"❌ Ошибка при попытке восстановления календаря: {str(e2)}")
            await context.bot.send_message(chat_id, text="❌ Произошла ошибка. Используйте /start для начала заново.")
