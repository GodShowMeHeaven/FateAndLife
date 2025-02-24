from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.compatibility_service import get_zodiac_compatibility, get_natal_compatibility
from utils.loading_messages import send_processing_message, replace_processing_message
from utils.calendar import start_calendar, handle_calendar
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def compatibility(update: Update, context: CallbackContext) -> None:
    """Обрабатывает запрос совместимости по знакам зодиака."""
    if not update.message or len(context.args) < 2:
        await update.message.reply_text(
            "💑 *Введите знаки зодиака для проверки совместимости:*\n"
            "`/compatibility Овен Телец`",
            parse_mode="Markdown"
        )
        return

    sign1, sign2 = context.args[0].capitalize(), context.args[1].capitalize()
    processing_message = await send_processing_message(update, f"💞 Подготавливаем совместимость {sign1} и {sign2}...")

    try:
        compatibility_text = get_zodiac_compatibility(sign1, sign2)

        formatted_text = (
            f"💞 *Совместимость {sign1} и {sign2}*\n"
            "__________________________\n"
            f"{compatibility_text}\n"
            "__________________________\n"
            "💡 *Совет:* Используйте знание зодиака для гармонии!"
        )

        # Добавляем кнопку возврата
        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await replace_processing_message(context, processing_message, formatted_text, reply_markup)
    except Exception as e:
        logger.error(f"Ошибка при расчете совместимости: {e}")
        await replace_processing_message(context, processing_message, "⚠️ Ошибка при расчете совместимости. Попробуйте позже.")

async def compatibility_natal(update: Update, context: CallbackContext) -> None:
    """Обрабатывает запрос астрологической совместимости: через команду или календарь."""
    chat_id = update.effective_chat.id
    processing_message = None

    # Проверяем источник вызова: команда или календарь
    if update.message and context.args:  # Вызов через команду
        if len(context.args) < 8:
            await update.message.reply_text(
                "🌌 *Введите данные для совместимости по натальной карте:*\n"
                "`/compatibility_natal Имя1 ДД.ММ.ГГГГ ЧЧ:ММ Город1 Имя2 ДД.ММ.ГГГГ ЧЧ:ММ Город2`",
                parse_mode="Markdown"
            )
            return

        name1, birth1, time1, place1 = context.args[:4]
        name2, birth2, time2, place2 = context.args[4:]

    elif context.user_data.get("selected_date"):  # Вызов через календарь
        # Сбор данных для первой персоны
        if not context.user_data.get("compat_name1"):
            await context.bot.send_message(
                chat_id,
                "📜 Укажите имя первой персоны (например, 'Анна'):",
            )
            context.user_data["awaiting_compat_name1"] = True
            return

        if not context.user_data.get("compat_birth1"):
            birth1 = context.user_data["selected_date"]
            context.user_data["compat_birth1"] = birth1
            context.user_data.pop("selected_date")
            await context.bot.send_message(
                chat_id,
                "⏰ Укажите время рождения первой персоны (например, '14:30'):",
            )
            context.user_data["awaiting_compat_time1"] = True
            return

        if not context.user_data.get("compat_place1"):
            await context.bot.send_message(
                chat_id,
                "📍 Укажите место рождения первой персоны (например, 'Москва'):",
            )
            context.user_data["awaiting_compat_place1"] = True
            return

        # Сбор данных для второй персоны
        if not context.user_data.get("compat_name2"):
            await context.bot.send_message(
                chat_id,
                "📜 Укажите имя второй персоны (например, 'Иван'):",
            )
            context.user_data["awaiting_compat_name2"] = True
            context.user_data["awaiting_compatibility"] = True  # Запускаем второй календарь
            await start_calendar(update, context)
            return

        if not context.user_data.get("compat_birth2"):
            birth2 = context.user_data["selected_date"]
            context.user_data["compat_birth2"] = birth2
            context.user_data.pop("selected_date")
            await context.bot.send_message(
                chat_id,
                "⏰ Укажите время рождения второй персоны (например, '09:15'):",
            )
            context.user_data["awaiting_compat_time2"] = True
            return

        if not context.user_data.get("compat_place2"):
            await context.bot.send_message(
                chat_id,
                "📍 Укажите место рождения второй персоны (например, 'Санкт-Петербург'):",
            )
            context.user_data["awaiting_compat_place2"] = True
            return

        # Все данные собраны
        name1 = context.user_data["compat_name1"]
        birth1 = context.user_data["compat_birth1"]
        time1 = context.user_data["compat_time1"]
        place1 = context.user_data["compat_place1"]
        name2 = context.user_data["compat_name2"]
        birth2 = context.user_data["compat_birth2"]
        time2 = context.user_data["compat_time2"]
        place2 = context.user_data["compat_place2"]

    else:
        logger.warning("⚠️ compatibility_natal вызван без команды или данных календаря")
        await context.bot.send_message(
            chat_id,
            "⚠️ Используйте команду `/compatibility_natal Имя1 ДД.ММ.ГГГГ ЧЧ:ММ Город1 Имя2 ДД.ММ.ГГГГ ЧЧ:ММ Город2` или выберите дату через меню.",
            parse_mode="Markdown"
        )
        return

    try:
        # Отправляем сообщение о подготовке
        if update.message:
            processing_message = await send_processing_message(update, f"🔮 Подготавливаем астрологическую совместимость {name1} и {name2}...")
        else:
            processing_message = await context.bot.send_message(chat_id, f"🔮 Подготавливаем астрологическую совместимость {name1} и {name2}...")

        # Получаем совместимость
        compatibility_text = get_natal_compatibility(name1, birth1, time1, place1, name2, birth2, time2, place2)

        formatted_text = (
            f"🔮 *Астрологическая совместимость {name1} и {name2}*\n"
            "__________________________\n"
            f"{compatibility_text}\n"
            "__________________________\n"
            "✨ *Совет:* Используйте астрологию для гармонии в паре!"
        )

        # Добавляем кнопку возврата
        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Заменяем сообщение на результат
        await replace_processing_message(context, processing_message, formatted_text, reply_markup)

        # Очищаем временные данные
        context.user_data.pop("compat_name1", None)
        context.user_data.pop("compat_birth1", None)
        context.user_data.pop("compat_time1", None)
        context.user_data.pop("compat_place1", None)
        context.user_data.pop("compat_name2", None)
        context.user_data.pop("compat_birth2", None)
        context.user_data.pop("compat_time2", None)
        context.user_data.pop("compat_place2", None)
        context.user_data.pop("selected_date", None)

    except Exception as e:
        logger.error(f"Ошибка при расчете астрологической совместимости: {e}")
        error_message = "⚠️ Ошибка при расчете совместимости. Попробуйте позже."
        if processing_message:
            await replace_processing_message(context, processing_message, error_message)
        else:
            await context.bot.send_message(chat_id, error_message)

async def handle_compatibility_input(update: Update, context: CallbackContext) -> None:
    """Обрабатывает ввод пользователя для данных совместимости."""
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    # Проверяем, ожидается ли ввод для совместимости
    awaiting_keys = ["awaiting_compat_name1", "awaiting_compat_time1", "awaiting_compat_place1",
                     "awaiting_compat_name2", "awaiting_compat_time2", "awaiting_compat_place2"]
    if not any(key in context.user_data for key in awaiting_keys):
        logger.debug(f"Игнорируем текст '{text}' - нет активных флагов ожидания для совместимости")
        return

    try:
        if context.user_data.get("awaiting_compat_name1"):
            context.user_data["compat_name1"] = text
            context.user_data.pop("awaiting_compat_name1")
            await context.bot.send_message(chat_id, "⏰ Укажите время рождения первой персоны (например, '14:30'):")
            context.user_data["awaiting_compat_time1"] = True

        elif context.user_data.get("awaiting_compat_time1"):
            if not any(char.isdigit() for char in text) or ":" not in text:
                await update.message.reply_text("⏰ Формат времени неверный. Используйте 'ЧЧ:ММ' (например, '14:30').")
                return
            context.user_data["compat_time1"] = text
            context.user_data.pop("awaiting_compat_time1")
            await context.bot.send_message(chat_id, "📍 Укажите место рождения первой персоны (например, 'Москва'):")
            context.user_data["awaiting_compat_place1"] = True

        elif context.user_data.get("awaiting_compat_place1"):
            context.user_data["compat_place1"] = text
            context.user_data.pop("awaiting_compat_place1")
            await context.bot.send_message(chat_id, "📜 Укажите имя второй персоны (например, 'Иван'):")
            context.user_data["awaiting_compat_name2"] = True
            context.user_data["awaiting_compatibility"] = True
            await start_calendar(update, context)

        elif context.user_data.get("awaiting_compat_name2"):
            context.user_data["compat_name2"] = text
            context.user_data.pop("awaiting_compat_name2")
            await context.bot.send_message(chat_id, "⏰ Укажите время рождения второй персоны (например, '09:15'):")
            context.user_data["awaiting_compat_time2"] = True

        elif context.user_data.get("awaiting_compat_time2"):
            if not any(char.isdigit() for char in text) or ":" not in text:
                await update.message.reply_text("⏰ Формат времени неверный. Используйте 'ЧЧ:ММ' (например, '09:15').")
                return
            context.user_data["compat_time2"] = text
            context.user_data.pop("awaiting_compat_time2")
            await context.bot.send_message(chat_id, "📍 Укажите место рождения второй персоны (например, 'Санкт-Петербург'):")
            context.user_data["awaiting_compat_place2"] = True

        elif context.user_data.get("awaiting_compat_place2"):
            context.user_data["compat_place2"] = text
            context.user_data.pop("awaiting_compat_place2")
            await compatibility_natal(update, context)

    except Exception as e:
        logger.error(f"Ошибка при обработке ввода для совместимости: {e}")
        await context.bot.send_message(
            chat_id,
            "⚠️ Произошла ошибка при вводе данных. Начните заново с команды /compatibility_natal или выбора даты.",
            parse_mode="Markdown"
        )
        # Предполагается, что функция clear_compatibility_data определена в compatibility.py
        clear_compatibility_data(context)
        
def clear_compatibility_data(context: CallbackContext) -> None:
    """Очищает все данные, связанные с совместимостью, из context.user_data."""
    compat_keys = ["selected_date", "compat_name1", "compat_birth1", "compat_time1", "compat_place1",
                   "compat_name2", "compat_birth2", "compat_time2", "compat_place2",
                   "awaiting_compat_name1", "awaiting_compat_time1", "awaiting_compat_place1",
                   "awaiting_compat_name2", "awaiting_compat_time2", "awaiting_compat_place2",
                   "awaiting_compatibility"]
    for key in compat_keys:
        context.user_data.pop(key, None)
    logger.info("Очищены данные совместимости из context.user_data")