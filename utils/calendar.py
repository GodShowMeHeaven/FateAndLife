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
        logger.warning("⚠️ Вызван handle_calendar без callback_query")
        return

    logger.info(f"📥 Получен callback данные: {query.data}")
    await query.answer()

    chat_id = update.effective_chat.id
    calendar = WMonthTelegramCalendar(locale="ru")

    try:
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
                    await natal_chart(update, context)
                elif context.user_data.get("awaiting_compatibility"):
                    # Сохраняем дату в зависимости от того, для кого она выбрана
                    if "compat_name1" in context.user_data and "compat_birth1" not in context.user_data:
                        context.user_data["compat_birth1"] = formatted_date
                    elif "compat_name2" in context.user_data and "compat_birth2" not in context.user_data:
                        context.user_data["compat_birth2"] = formatted_date
                    else:
                        logger.warning("⚠️ Не удалось определить, для кого выбрана дата")
                        await context.bot.send_message(
                            chat_id,
                            text="⚠️ Ошибка: начните процесс заново."
                        )
                        return

                    # Очищаем selected_date
                    context.user_data.pop("selected_date", None)

                    # Создаём фейковое сообщение для handle_compatibility_input
                    update.message = query.message
                    update.message.text = ""  # Пустой текст, так как мы уже обработали дату
                    from handlers.compatibility import handle_compatibility_input
                    await handle_compatibility_input(update, context)
            finally:
                # Очищаем флаги после обработки, если нужно
                if not context.user_data.get("awaiting_compatibility"):
                    context.user_data.pop("awaiting_numerology", None)
                    context.user_data.pop("awaiting_natal_chart", None)
                    context.user_data.pop("awaiting_compatibility", None)
        else:
            # Продолжаем показывать календарь
            keyboard = InlineKeyboardMarkup.from_dict(json.loads(keyboard_json)) if isinstance(keyboard_json, str) else keyboard_json
            try:
                if query.message:
                    await query.edit_message_reply_markup(reply_markup=keyboard)
                else:
                    await context.bot.send_message(chat_id, text="📅 Выберите дату:", reply_markup=keyboard)
            except Exception as e:
                logger.warning(f"⚠️ Не удалось обновить клавиатуру: {e}")
                await context.bot.send_message(chat_id, text="📅 Выберите дату:", reply_markup=keyboard)

    except Exception as e:
        logger.error(f"❌ Ошибка при обработке календаря: {str(e)}")
        try:
            if query.message:
                await query.edit_message_text(
                    text="❌ Произошла ошибка. Попробуйте выбрать дату заново.",
                    reply_markup=calendar.build()[0]
                )
            else:
                await context.bot.send_message(
                    chat_id,
                    text="❌ Произошла ошибка. Попробуйте выбрать дату заново.",
                    reply_markup=calendar.build()[0]
                )
        except Exception as e2:
            logger.error(f"❌ Ошибка при восстановлении календаря: {e2}")
            await context.bot.send_message(
                chat_id,
                text="❌ Произошла ошибка. Используйте /start для начала заново."
            )