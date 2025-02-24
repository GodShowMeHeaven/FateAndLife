from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram_bot_calendar import DetailedTelegramCalendar
import logging
from datetime import date
import json

logger = logging.getLogger(__name__)

# Настраиваем календарь
class CustomCalendar(DetailedTelegramCalendar):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Русские названия месяцев
        self.months = {
            1: 'Янв', 2: 'Фев', 3: 'Март', 4: 'Апр',
            5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Авг',
            9: 'Сен', 10: 'Окт', 11: 'Ноя', 12: 'Дек'
        }
        
        # Русские названия дней недели
        self.days_of_week = {
            0: 'Пн', 1: 'Вт', 2: 'Ср',
            3: 'Чт', 4: 'Пт', 5: 'Сб', 6: 'Вс'
        }
        
        # Настройка порядка выбора
        self.LSTEP = {
            'y': 'год',
            'm': 'месяц',
            'd': 'день'
        }

async def start_calendar(update: Update, context: CallbackContext) -> None:
    """Отправляет пошаговый календарь для выбора даты."""
    try:
        chat_id = update.effective_chat.id
        
        calendar = CustomCalendar(
            min_date=date(1900, 1, 1),
            max_date=date.today(),
            locale="ru"
        )
        await context.bot.send_message(
            chat_id=chat_id,
            text="📅 Выберите год:",
            reply_markup=calendar.build()
        )
        logger.info(f"📅 Календарь отправлен для чата {chat_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при создании календаря: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ Произошла ошибка при создании календаря. Попробуйте позже."
        )

async def handle_calendar(update: Update, context: CallbackContext) -> None:
    """Обрабатывает пошаговый выбор даты."""
    query = update.callback_query
    if not query:
        return
    
    logger.info(f"📥 Получен callback данные: {query.data}")
    await query.answer()

    try:
        calendar = CustomCalendar(
            min_date=date(1900, 1, 1),
            max_date=date.today(),
            locale="ru"
        )
        result, keyboard, step = calendar.process(query.data)
        
        if not result and keyboard:
            # Показываем соответствующий текст в зависимости от шага
            if step == 'y':
                text = "📅 Выберите год:"
            elif step == 'm':
                text = "📅 Выберите месяц:"
            else:
                text = "📅 Выберите день:"
                
            await query.edit_message_text(
                text=text,
                reply_markup=keyboard
            )
        elif result:
            # Дата полностью выбрана
            formatted_date = result.strftime("%d.%m.%Y")
            context.user_data["selected_date"] = formatted_date
            await query.edit_message_text(
                text=f"✅ Вы выбрали дату: {formatted_date}"
            )
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="⏰ Введите время рождения в формате ЧЧ:ММ:"
            )
            
    except Exception as e:
        logger.error(f"❌ Ошибка при обработке календаря: {str(e)}")
        try:
            await query.edit_message_text(
                text="❌ Произошла ошибка. Попробуйте выбрать дату заново.",
                reply_markup=calendar.build()
            )
        except Exception as e2:
            logger.error(f"❌ Ошибка при попытке восстановления календаря: {str(e2)}")
            await query.edit_message_text(
                text="❌ Произошла ошибка. Используйте /start для начала заново."
            )