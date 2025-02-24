from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram_bot_calendar import WMonthTelegramCalendar
import logging
from datetime import date
import json

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
    """Обрабатывает выбор даты в inline-календаре."""
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
            await query.edit_message_text(
                text=f"✅ Вы выбрали дату: {formatted_date}"
            )
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="⏰ Введите время рождения в формате ЧЧ:ММ:"
            )
        else:
            # Дата не выбрана, показываем календарь
            if isinstance(keyboard_json, str):
                # Если клавиатура пришла в виде JSON строки
                keyboard = InlineKeyboardMarkup.from_dict(json.loads(keyboard_json))
            else:
                # Если клавиатура пришла в виде объекта
                keyboard = keyboard_json
                
            await query.edit_message_text(
                text="📅 Выберите дату:",
                reply_markup=keyboard
            )
            
    except Exception as e:
        logger.error(f"❌ Ошибка при обработке календаря: {str(e)}")
        try:
            await query.edit_message_text(
                text="❌ Произошла ошибка. Попробуйте выбрать дату заново.",
                reply_markup=calendar.build()[0]
            )
        except Exception as e2:
            logger.error(f"❌ Ошибка при попытке восстановления календаря: {str(e2)}")
            await query.edit_message_text(
                text="❌ Произошла ошибка. Используйте /start для начала заново."
            )