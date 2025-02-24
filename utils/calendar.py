import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, ConversationHandler
from telegram_bot_calendar import WMonthTelegramCalendar
import json
from datetime import date, datetime
import calendar
import re

logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
CHOOSING_INPUT_METHOD, WAITING_FOR_MANUAL_DATE, WAITING_FOR_YEAR, WAITING_FOR_MONTH, WAITING_FOR_DAY = range(5)

async def start_calendar(update: Update, context: CallbackContext) -> int:
    """Отправляет выбор способа ввода даты: календарь или ручной ввод."""
    try:
        chat_id = update.effective_chat.id
        
        # Создаем клавиатуру с выбором способа ввода
        keyboard = [
            [InlineKeyboardButton("📅 Выбрать в календаре", callback_data="calendar_select")],
            [InlineKeyboardButton("⌨️ Ввести дату вручную", callback_data="manual_input")],
            [InlineKeyboardButton("📆 Быстрый выбор года", callback_data="year_select")]
        ]
        
        await context.bot.send_message(
            chat_id=chat_id,
            text="Как вы хотите указать дату?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        logger.info(f"📱 Меню выбора способа ввода даты отправлено для чата {chat_id}")
        
        return CHOOSING_INPUT_METHOD
        
    except Exception as e:
        logger.error(f"❌ Ошибка при создании меню выбора даты: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Произошла ошибка. Попробуйте позже."
        )
        return ConversationHandler.END

async def choose_input_method(update: Update, context: CallbackContext) -> int:
    """Обрабатывает выбор способа ввода даты."""
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_chat.id
    
    choice = query.data
    
    if choice == "calendar_select":
        # Используем стандартный календарь
        calendar_obj = WMonthTelegramCalendar(locale="ru")
        await query.edit_message_text(
            text="📅 Выберите дату:",
            reply_markup=calendar_obj.build()[0]
        )
        return ConversationHandler.END  # Продолжим через handle_calendar
    
    elif choice == "manual_input":
        # Запрашиваем ручной ввод даты
        await query.edit_message_text(
            text="✏️ Введите дату в формате ДД.ММ.ГГГГ (например, 04.04.1990):"
        )
        return WAITING_FOR_MANUAL_DATE
    
    elif choice == "year_select":
        # Отправляем меню для выбора года
        years = generate_year_buttons()
        await query.edit_message_text(
            text="📆 Выберите год:",
            reply_markup=InlineKeyboardMarkup(years)
        )
        return WAITING_FOR_YEAR

async def handle_manual_date_input(update: Update, context: CallbackContext) -> int:
    """Обрабатывает ручной ввод даты."""
    text = update.message.text
    chat_id = update.effective_chat.id
    
    # Проверяем формат даты (ДД.ММ.ГГГГ)
    date_pattern = re.compile(r'^(\d{1,2})\.(\d{1,2})\.(\d{4})$')
    match = date_pattern.match(text)
    
    if match:
        day, month, year = map(int, match.groups())
        try:
            selected_date = date(year, month, day)
            formatted_date = selected_date.strftime("%d.%m.%Y")
            context.user_data["selected_date"] = formatted_date
            
            await update.message.reply_text(f"✅ Вы выбрали дату: {formatted_date}")
            
            # Передаем дату в нужный обработчик
            await process_selected_date(update, context, formatted_date)
            return ConversationHandler.END
            
        except ValueError:
            await update.message.reply_text(
                "❌ Неверная дата. Пожалуйста, введите корректную дату в формате ДД.ММ.ГГГГ:"
            )
            return WAITING_FOR_MANUAL_DATE
    else:
        await update.message.reply_text(
            "❌ Неверный формат. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ (например, 04.04.1990):"
        )
        return WAITING_FOR_MANUAL_DATE

def generate_year_buttons():
    """Генерирует кнопки для выбора года."""
    current_year = datetime.now().year
    years = []
    
    # Создаем кнопки для текущего года и предыдущих 4 лет
    recent_years = [[
        InlineKeyboardButton(f"{year}", callback_data=f"year_{year}")
        for year in range(current_year-4, current_year+1)
    ]]
    
    # Создаем кнопки для десятилетий
    decades = []
    for decade in range(1920, current_year, 10):
        if len(decades) == 3:  # Максимум 3 кнопки в ряду
            years.append(decades)
            decades = []
        decades.append(InlineKeyboardButton(f"{decade}-е", callback_data=f"decade_{decade}"))
    
    if decades:  # Добавляем неполный ряд, если есть
        years.append(decades)
    
    # Добавляем строку с недавними годами в начало
    return recent_years + years

async def handle_year_selection(update: Update, context: CallbackContext) -> int:
    """Обрабатывает выбор года."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("year_"):
        # Если выбран конкретный год
        year = int(data.split("_")[1])
        context.user_data["selected_year"] = year
        
        # Показываем месяцы
        months = generate_month_buttons()
        await query.edit_message_text(
            text=f"📆 Выбран год: {year}. Теперь выберите месяц:",
            reply_markup=InlineKeyboardMarkup(months)
        )
        return WAITING_FOR_MONTH
        
    elif data.startswith("decade_"):
        # Если выбрано десятилетие, показываем годы этого десятилетия
        decade = int(data.split("_")[1])
        years = []
        for i in range(0, 10, 2):
            row = []
            for j in range(2):
                if i + j < 10:  # Проверка, чтобы не выйти за пределы десятилетия
                    year = decade + i + j
                    row.append(InlineKeyboardButton(f"{year}", callback_data=f"year_{year}"))
            years.append(row)
        
        # Добавляем кнопку "Назад"
        years.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_decades")])
        
        await query.edit_message_text(
            text=f"📆 Выберите год из {decade}-х:",
            reply_markup=InlineKeyboardMarkup(years)
        )
        return WAITING_FOR_YEAR

def generate_month_buttons():
    """Генерирует кнопки для выбора месяца."""
    months = []
    # Русские названия месяцев
    month_names = [
        "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
        "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
    ]
    
    # Создаем кнопки по 3 месяца в ряду
    for i in range(0, 12, 3):
        row = []
        for j in range(3):
            if i + j < 12:  # Проверка на выход за пределы
                month_num = i + j + 1  # +1 потому что месяцы начинаются с 1
                row.append(InlineKeyboardButton(month_names[i+j], callback_data=f"month_{month_num}"))
        months.append(row)
    
    # Добавляем кнопку "Назад"
    months.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_years")])
    
    return months

async def handle_month_selection(update: Update, context: CallbackContext) -> int:
    """Обрабатывает выбор месяца."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "back_to_years":
        # Возвращаемся к выбору года
        years = generate_year_buttons()
        await query.edit_message_text(
            text="📆 Выберите год:",
            reply_markup=InlineKeyboardMarkup(years)
        )
        return WAITING_FOR_YEAR
    
    if data.startswith("month_"):
        month = int(data.split("_")[1])
        context.user_data["selected_month"] = month
        year = context.user_data["selected_year"]
        
        # Определяем количество дней в месяце
        days_in_month = calendar.monthrange(year, month)[1]
        
        # Генерируем кнопки для дней
        day_buttons = generate_day_buttons(days_in_month)
        
        # Русские названия месяцев
        month_names = [
            "января", "февраля", "марта", "апреля", "мая", "июня",
            "июля", "августа", "сентября", "октября", "ноября", "декабря"
        ]
        
        await query.edit_message_text(
            text=f"📆 Выберите день {month_names[month-1]} {year} года:",
            reply_markup=InlineKeyboardMarkup(day_buttons)
        )
        return WAITING_FOR_DAY

def generate_day_buttons(days_in_month):
    """Генерирует кнопки для выбора дня."""
    day_buttons = []
    
    # Создаем кнопки по 7 дней в ряду (как в календаре)
    for i in range(0, days_in_month, 7):
        row = []
        for j in range(7):
            if i + j < days_in_month:
                day = i + j + 1
                row.append(InlineKeyboardButton(f"{day}", callback_data=f"day_{day}"))
        day_buttons.append(row)
    
    # Добавляем кнопку "Назад"
    day_buttons.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_months")])
    
    return day_buttons

async def handle_day_selection(update: Update, context: CallbackContext) -> int:
    """Обрабатывает выбор дня."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "back_to_months":
        # Возвращаемся к выбору месяца
        months = generate_month_buttons()
        await query.edit_message_text(
            text=f"📆 Выбран год: {context.user_data['selected_year']}. Теперь выберите месяц:",
            reply_markup=InlineKeyboardMarkup(months)
        )
        return WAITING_FOR_MONTH
    
    if data.startswith("day_"):
        day = int(data.split("_")[1])
        year = context.user_data["selected_year"]
        month = context.user_data["selected_month"]
        
        try:
            selected_date = date(year, month, day)
            formatted_date = selected_date.strftime("%d.%m.%Y")
            context.user_data["selected_date"] = formatted_date
            
            await query.edit_message_text(text=f"✅ Вы выбрали дату: {formatted_date}")
            
            # Передаем дату в нужный обработчик
            await process_selected_date(update, context, formatted_date)
            return ConversationHandler.END
            
        except ValueError as e:
            logger.error(f"❌ Ошибка при создании даты: {e}")
            await query.edit_message_text(
                text="❌ Произошла ошибка при выборе даты. Попробуйте еще раз."
            )
            return ConversationHandler.END

async def process_selected_date(update: Update, context: CallbackContext, formatted_date: str) -> None:
    """Обрабатывает выбранную дату и передает в соответствующий обработчик."""
    try:
        # Передача даты в нужный обработчик
        if context.user_data.get("awaiting_numerology"):
            from handlers.numerology import process_numerology
            await process_numerology(update, context, formatted_date)
        elif context.user_data.get("awaiting_natal_chart"):
            from handlers.natal_chart import natal_chart
            await natal_chart(update, context)
        elif context.user_data.get("awaiting_compatibility"):
            from handlers.compatibility import compatibility_natal
            await compatibility_natal(update, context)
    finally:
        # Очищаем флаги после обработки
        context.user_data.pop("awaiting_numerology", None)
        context.user_data.pop("awaiting_natal_chart", None)
        context.user_data.pop("awaiting_compatibility", None)

async def handle_calendar(update: Update, context: CallbackContext) -> None:
    """Обрабатывает выбор даты в inline-календаре."""
    query = update.callback_query
    if not query:
        logger.warning("⚠️ Вызван handle_calendar без callback_query")
        return

    logger.info(f"📥 Получен callback данные: {query.data}")
    await query.answer()

    # Если это возврат к выбору способа ввода
    if query.data == "back_to_input_method":
        return await start_calendar(update, context)

    chat_id = update.effective_chat.id
    calendar_obj = WMonthTelegramCalendar(locale="ru")

    try:
        selected, keyboard_json, step = calendar_obj.process(query.data)
        logger.debug(f"Результат обработки календаря: {selected}, {step}")

        if selected:
            # Дата выбрана
            formatted_date = selected.strftime("%d.%m.%Y")
            context.user_data["selected_date"] = formatted_date

            # Безопасное обновление сообщения
            try:
                if query.message:
                    await query.edit_message_text(text=f"✅ Вы выбрали дату: {formatted_date}")
                else:
                    await context.bot.send_message(chat_id, text=f"✅ Вы выбрали дату: {formatted_date}")
            except Exception as e:
                logger.warning(f"⚠️ Не удалось отредактировать сообщение: {e}")
                await context.bot.send_message(chat_id, text=f"✅ Вы выбрали дату: {formatted_date}")

            # Передача даты в нужный обработчик
            await process_selected_date(update, context, formatted_date)
        else:
            # Продолжаем показывать календарь
            keyboard = InlineKeyboardMarkup.from_dict(json.loads(keyboard_json)) if isinstance(keyboard_json, str) else keyboard_json
            
            # Добавляем кнопку "Ввести вручную" к стандартному календарю
            keyboard_dict = keyboard.to_dict()
            keyboard_dict["inline_keyboard"].append([{"text": "⌨️ Ввести вручную", "callback_data": "manual_input"}])
            
            try:
                if query.message:
                    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup.from_dict(keyboard_dict))
                else:
                    await context.bot.send_message(chat_id, text="📅 Выберите дату:", reply_markup=InlineKeyboardMarkup.from_dict(keyboard_dict))
            except Exception as e:
                logger.warning(f"⚠️ Не удалось обновить клавиатуру: {e}")
                await context.bot.send_message(chat_id, text="📅 Выберите дату:", reply_markup=InlineKeyboardMarkup.from_dict(keyboard_dict))

    except Exception as e:
        logger.error(f"❌ Ошибка при обработке календаря: {str(e)}")
        try:
            if query.message:
                await query.edit_message_text(
                    text="❌ Произошла ошибка. Попробуйте выбрать дату заново.",
                    reply_markup=calendar_obj.build()[0]
                )
            else:
                await context.bot.send_message(
                    chat_id,
                    text="❌ Произошла ошибка. Попробуйте выбрать дату заново.",
                    reply_markup=calendar_obj.build()[0]
                )
        except Exception as e2:
            logger.error(f"❌ Ошибка при восстановлении календаря: {e2}")
            await context.bot.send_message(
                chat_id,
                text="❌ Произошла ошибка. Используйте /start для начала заново."
            )

# Инициализация ConversationHandler для всего процесса выбора даты
def get_calendar_conversation_handler():
    from telegram.ext import CallbackQueryHandler, MessageHandler, filters
    
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(choose_input_method, pattern=r'^(calendar_select|manual_input|year_select)$')],
        states={
            WAITING_FOR_MANUAL_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_manual_date_input)],
            WAITING_FOR_YEAR: [CallbackQueryHandler(handle_year_selection, pattern=r'^(year_|decade_|back_to_decades).*')],
            WAITING_FOR_MONTH: [CallbackQueryHandler(handle_month_selection, pattern=r'^(month_|back_to_years).*')],
            WAITING_FOR_DAY: [CallbackQueryHandler(handle_day_selection, pattern=r'^(day_|back_to_months).*')],
        },
        fallbacks=[],
        name="calendar_conversation",
        persistent=False
    )