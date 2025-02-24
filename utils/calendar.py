import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram_bot_calendar import WMonthTelegramCalendar
import json
from datetime import datetime, date

logger = logging.getLogger(__name__)

# Диапазон годов для выбора
MIN_YEAR = 1900
MAX_YEAR = 2100

async def start_calendar(update: Update, context: CallbackContext) -> None:
    """Отправляет inline-календарь с предварительным выбором года и месяца."""
    try:
        chat_id = update.effective_chat.id
        current_year = datetime.now().year

        # Создаем клавиатуру для выбора года
        year_buttons = []
        for year in range(current_year - 20, current_year + 21, 10):  # Показываем 41 год (5 групп по 10 лет)
            if MIN_YEAR <= year <= MAX_YEAR:
                year_buttons.append(
                    InlineKeyboardButton(str(year), callback_data=f"year_{year}")
                )
        year_keyboard = [year_buttons[i:i + 3] for i in range(0, len(year_buttons), 3)]  # 3 кнопки в строке
        year_keyboard.append([
            InlineKeyboardButton("<< Назад 10 лет", callback_data="year_back_10"),
            InlineKeyboardButton("Вперед 10 лет >>", callback_data="year_forward_10")
        ])
        year_keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_calendar")])

        await context.bot.send_message(
            chat_id=chat_id,
            text="📅 Выберите год:",
            reply_markup=InlineKeyboardMarkup(year_keyboard)
        )
        context.user_data["calendar_step"] = "year"
        logger.info(f"📅 Календарь: начат выбор года для чата {chat_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка при создании календаря: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ Произошла ошибка при создании календаря. Попробуйте позже."
        )

async def handle_calendar(update: Update, context: CallbackContext) -> None:
    """Обрабатывает выбор даты, года или месяца в inline-календаре."""
    query = update.callback_query
    if not query:
        logger.warning("⚠️ Вызван handle_calendar без callback_query")
        return

    logger.info(f"📥 Получен callback данные: {query.data}")
    await query.answer()

    chat_id = update.effective_chat.id
    calendar_step = context.user_data.get("calendar_step", "year")

    try:
        if calendar_step == "year":
            if query.data.startswith("year_"):
                year = int(query.data.replace("year_", ""))
                # Создаем клавиатуру для выбора месяца
                month_buttons = []
                for month in range(1, 13):
                    month_name = datetime(2000, month, 1).strftime("%B")  # Название месяца на русском
                    month_buttons.append(
                        InlineKeyboardButton(month_name, callback_data=f"month_{month}_{year}")
                    )
                month_keyboard = [month_buttons[i:i + 3] for i in range(0, len(month_buttons), 3)]  # 3 кнопки в строке
                month_keyboard.append([
                    InlineKeyboardButton("Назад", callback_data="back_to_year"),
                    InlineKeyboardButton("Отмена", callback_data="cancel_calendar")
                ])

                await query.edit_message_text(
                    text="📅 Выберите месяц:",
                    reply_markup=InlineKeyboardMarkup(month_keyboard)
                )
                context.user_data["calendar_step"] = "month"
                logger.info(f"📅 Календарь: начат выбор месяца для года {year} в чате {chat_id}")
            elif query.data == "year_back_10":
                current_year = context.user_data.get("current_year", datetime.now().year)
                new_year = max(MIN_YEAR, current_year - 10)
                context.user_data["current_year"] = new_year
                await show_year_selection(update, context)
            elif query.data == "year_forward_10":
                current_year = context.user_data.get("current_year", datetime.now().year)
                new_year = min(MAX_YEAR, current_year + 10)
                context.user_data["current_year"] = new_year
                await show_year_selection(update, context)
            elif query.data == "cancel_calendar":
                await query.edit_message_text(
                    text="📅 Выбор даты отменен.",
                    reply_markup=None
                )
                context.user_data.pop("calendar_step", None)
                context.user_data.pop("current_year", None)
                logger.info(f"📅 Календарь: выбор даты отменен для чата {chat_id}")
                return
        elif calendar_step == "month":
            if query.data.startswith("month_"):
                month, year = map(int, query.data.replace("month_", "").split("_"))
                calendar = WMonthTelegramCalendar(locale="ru", min_date=date(MIN_YEAR, 1, 1), max_date=date(MAX_YEAR, 12, 31))
                keyboard = calendar.build()[0]
                await query.edit_message_text(
                    text="📅 Выберите день:",
                    reply_markup=keyboard
                )
                context.user_data["calendar_step"] = "day"
                context.user_data["selected_month"] = month
                context.user_data["selected_year"] = year
                logger.info(f"📅 Календарь: начат выбор дня для {month}/{year} в чате {chat_id}")
            elif query.data == "back_to_year":
                await start_calendar(update, context)
                context.user_data.pop("calendar_step", None)
            elif query.data == "cancel_calendar":
                await query.edit_message_text(
                    text="📅 Выбор даты отменен.",
                    reply_markup=None
                )
                context.user_data.pop("calendar_step", None)
                context.user_data.pop("selected_month", None)
                context.user_data.pop("selected_year", None)
                logger.info(f"📅 Календарь: выбор даты отменен для чата {chat_id}")
                return
        elif calendar_step == "day":
            calendar = WMonthTelegramCalendar(locale="ru", min_date=date(MIN_YEAR, 1, 1), max_date=date(MAX_YEAR, 12, 31))
            selected, keyboard_json, step = calendar.process(query.data)
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
                try:
                    if context.user_data.get("awaiting_numerology"):
                        from handlers.numerology import process_numerology
                        await process_numerology(update, context, formatted_date)
                    elif context.user_data.get("awaiting_natal_chart"):
                        from handlers.natal_chart import natal_chart
                        # Передаем весь Update объект для полной совместимости
                        await natal_chart(update, context)
                    elif context.user_data.get("awaiting_compatibility"):
                        from handlers.compatibility import compatibility_natal
                        await compatibility_natal(update, context)
                finally:
                    # Очищаем флаги после обработки
                    context.user_data.pop("awaiting_numerology", None)
                    context.user_data.pop("awaiting_natal_chart", None)
                    context.user_data.pop("awaiting_compatibility", None)
                    context.user_data.pop("calendar_step", None)
                    context.user_data.pop("selected_month", None)
                    context.user_data.pop("selected_year", None)
            else:
                # Продолжаем показывать календарь
                keyboard = InlineKeyboardMarkup.from_dict(json.loads(keyboard_json)) if isinstance(keyboard_json, str) else keyboard_json
                try:
                    if query.message:
                        await query.edit_message_reply_markup(reply_markup=keyboard)
                    else:
                        await context.bot.send_message(chat_id, text="📅 Выберите день:", reply_markup=keyboard)
                except Exception as e:
                    logger.warning(f"⚠️ Не удалось обновить клавиатуру: {e}")
                    await context.bot.send_message(chat_id, text="📅 Выберите день:", reply_markup=keyboard)

    except Exception as e:
        logger.error(f"❌ Ошибка при обработке календаря: {str(e)}")
        try:
            if query.message:
                await query.edit_message_text(
                    text="❌ Произошла ошибка. Попробуйте выбрать дату заново.",
                    reply_markup=WMonthTelegramCalendar(locale="ru", min_date=date(MIN_YEAR, 1, 1), max_date=date(MAX_YEAR, 12, 31)).build()[0]
                )
            else:
                await context.bot.send_message(
                    chat_id,
                    text="❌ Произошла ошибка. Попробуйте выбрать дату заново.",
                    reply_markup=WMonthTelegramCalendar(locale="ru", min_date=date(MIN_YEAR, 1, 1), max_date=date(MAX_YEAR, 12, 31)).build()[0]
                )
        except Exception as e2:
            logger.error(f"❌ Ошибка при восстановлении календаря: {e2}")
            await context.bot.send_message(
                chat_id,
                text="❌ Произошла ошибка. Используйте /start для начала заново."
            )

async def show_year_selection(update: Update, context: CallbackContext) -> None:
    """Показывает клавиатуру для выбора года с учетом текущего диапазона."""
    chat_id = update.effective_chat.id
    current_year = context.user_data.get("current_year", datetime.now().year)

    year_buttons = []
    for year in range(max(MIN_YEAR, current_year - 20), min(MAX_YEAR + 1, current_year + 21), 10):
        year_buttons.append(
            InlineKeyboardButton(str(year), callback_data=f"year_{year}")
        )
    year_keyboard = [year_buttons[i:i + 3] for i in range(0, len(year_buttons), 3)]  # 3 кнопки в строке
    year_keyboard.append([
        InlineKeyboardButton("<< Назад 10 лет", callback_data="year_back_10"),
        InlineKeyboardButton("Вперед 10 лет >>", callback_data="year_forward_10")
    ])
    year_keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_calendar")])

    query = update.callback_query
    await query.edit_message_text(
        text="📅 Выберите год:",
        reply_markup=InlineKeyboardMarkup(year_keyboard)
    )
    context.user_data["calendar_step"] = "year"
    logger.info(f"📅 Календарь: обновлен выбор года для чата {chat_id}")