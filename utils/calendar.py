from telegram import Update
from telegram.ext import CallbackContext
from telegram_bot_calendar import WMonthTelegramCalendar
import logging
from datetime import date

logger = logging.getLogger(__name__)

async def start_calendar(update: Update, context: CallbackContext) -> None:
    """Отправляет inline-календарь для выбора даты."""
    try:
        chat_id = update.effective_chat.id
        
        min_date = date(1900, 1, 1)
        max_date = date.today()
        
        calendar = WMonthTelegramCalendar(min_date=min_date, max_date=max_date, locale="ru")
        calendar_data = calendar.build()
        
        logger.info(f"📅 Отправляем календарь для чата {chat_id}")
        logger.debug(f"Данные календаря: {calendar_data}")
        
        await context.bot.send_message(
            chat_id=chat_id,
            text="📅 Выберите дату:",
            reply_markup=calendar_data[0]
        )
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
        logger.error("❌ Получен пустой callback query")
        return
        
    logger.info(f"📥 Получен callback данные: {query.data}")
    await query.answer()  # Сразу отвечаем на callback

    try:
        # Создаем календарь с теми же параметрами
        calendar = WMonthTelegramCalendar(
            min_date=date(1900, 1, 1),
            max_date=date.today(),
            locale="ru"
        )
        
        # Обрабатываем callback данные
        logger.debug(f"Обрабатываем callback данные: {query.data}")
        result, keyboard = calendar.process(query.data)
        
        if not result and keyboard:
            logger.info("📅 Обновляем отображение календаря")
            await query.edit_message_text(
                text="📅 Выберите дату:",
                reply_markup=keyboard
            )
        elif result:
            formatted_date = result.strftime("%d.%m.%Y")
            logger.info(f"✅ Пользователь выбрал дату: {formatted_date}")
            
            await query.edit_message_text(f"✅ Вы выбрали: {formatted_date}")
            context.user_data["selected_date"] = formatted_date
            
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="⏰ Введите время рождения в формате ЧЧ:ММ:"
            )
    except Exception as e:
        logger.error(f"❌ Ошибка при обработке календаря: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при выборе даты. Попробуйте еще раз."
        )