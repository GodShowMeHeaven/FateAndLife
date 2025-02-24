from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.natal_chart_service import get_natal_chart
from utils.loading_messages import send_processing_message, replace_processing_message
import logging
import re

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_date(date_str: str) -> bool:
    """Проверяет, что дата в формате ДД.ММ.ГГГГ."""
    return bool(re.match(r"^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.\d{4}$", date_str))

def validate_time(time_str: str) -> bool:
    """Проверяет, что время в формате ЧЧ:ММ (00:00 - 23:59)."""
    return bool(re.match(r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", time_str))

def clear_natal_data(context: CallbackContext) -> None:
    """Очищает все данные, связанные с натальной картой, из context.user_data."""
    natal_keys = ["selected_date", "natal_name", "natal_time", "natal_place",
                  "awaiting_natal_name", "awaiting_natal_time", "awaiting_natal_place"]
    for key in natal_keys:
        context.user_data.pop(key, None)
    logger.info("Очищены данные натальной карты из context.user_data")

async def natal_chart(update: Update, context: CallbackContext) -> None:
    """Обрабатывает запрос натальной карты: через команду или календарь."""
    chat_id = update.effective_chat.id
    processing_message = None

    # Проверяем источник вызова: команда или календарь
    if update.message and context.args:  # Вызов через команду
        if len(context.args) < 4:
            await update.message.reply_text(
                "📜 *Введите данные для натальной карты в формате:*\n"
                "`/natal_chart Имя ДД.ММ.ГГГГ ЧЧ:ММ Город`",
                parse_mode="Markdown"
            )
            return

        name = context.args[0]
        birth_date = context.args[1]
        birth_time = context.args[2]
        birth_place = " ".join(context.args[3:])

        # Валидация даты и времени
        if not validate_date(birth_date):
            await update.message.reply_text(
                "⚠️ Неверный формат даты. Используйте 'ДД.ММ.ГГГГ' (например, '12.05.1990').",
                parse_mode="Markdown"
            )
            return
        if not validate_time(birth_time):
            await update.message.reply_text(
                "⚠️ Неверный формат времени. Используйте 'ЧЧ:ММ' (например, '14:30').",
                parse_mode="Markdown"
            )
            return

    elif context.user_data.get("selected_date"):  # Вызов через календарь
        birth_date = context.user_data["selected_date"]

        # Проверяем, есть ли сохраненные данные в user_data
        if not context.user_data.get("natal_name"):
            await context.bot.send_message(
                chat_id,
                "📜 Пожалуйста, укажите ваше имя для натальной карты (например, 'Анна'):",
            )
            context.user_data["awaiting_natal_name"] = True
            return

        if not context.user_data.get("natal_time"):
            await context.bot.send_message(
                chat_id,
                "⏰ Укажите время рождения (например, '14:30'):",
            )
            context.user_data["awaiting_natal_time"] = True
            return

        if not context.user_data.get("natal_place"):
            await context.bot.send_message(
                chat_id,
                "📍 Укажите место рождения (например, 'Москва'):",
            )
            context.user_data["awaiting_natal_place"] = True
            return

        # Все данные собраны
        name = context.user_data["natal_name"]
        birth_time = context.user_data["natal_time"]
        birth_place = context.user_data["natal_place"]

        # Валидация даты и времени из календаря
        if not validate_date(birth_date):
            logger.error(f"Неверный формат даты от календаря: {birth_date}")
            await context.bot.send_message(
                chat_id,
                "⚠️ Ошибка в формате даты от календаря. Попробуйте снова.",
                parse_mode="Markdown"
            )
            clear_natal_data(context)
            return
        if not validate_time(birth_time):
            await context.bot.send_message(
                chat_id,
                "⚠️ Неверный формат времени. Используйте 'ЧЧ:ММ' (например, '14:30'). Повторите ввод времени:",
            )
            context.user_data.pop("natal_time")  # Удаляем неверное время
            context.user_data["awaiting_natal_time"] = True
            return

    else:
        # Неизвестный вызов: ни команды, ни данных от календаря
        logger.warning("⚠️ natal_chart вызван без команды или данных календаря")
        await context.bot.send_message(
            chat_id,
            "⚠️ Используйте команду `/natal_chart Имя ДД.ММ.ГГГГ ЧЧ:ММ Город` или выберите дату через меню.",
            parse_mode="Markdown"
        )
        clear_natal_data(context)  # Очистка на случай некорректного состояния
        return

    try:
        # Отправляем сообщение о подготовке
        if update.message:
            processing_message = await send_processing_message(update, f"🌌 Подготавливаем вашу натальную карту для {name}...")
        else:
            processing_message = await context.bot.send_message(chat_id, f"🌌 Подготавливаем вашу натальную карту для {name}...")

        # Получаем натальную карту
        natal_chart_text = get_natal_chart(name, birth_date, birth_time, birth_place)

        formatted_chart = (
            f"🌌 *Анализ натальной карты для {name}*\n"
            "__________________________\n"
            f"{natal_chart_text}\n"
            "__________________________\n"
            "✨ *Совет:* Используйте знания натальной карты для развития!"
        )

        # Добавляем кнопку возврата
        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Заменяем сообщение на результат
        await replace_processing_message(context, processing_message, formatted_chart, reply_markup)

    except Exception as e:
        logger.error(f"Ошибка при обработке натальной карты: {e}")
        error_message = "⚠️ Произошла ошибка при обработке запроса. Попробуйте позже."
        if processing_message:
            await replace_processing_message(context, processing_message, error_message)
        else:
            await context.bot.send_message(chat_id, error_message, parse_mode="Markdown")
        raise  # Повторно выбрасываем исключение для обработки в finally

    finally:
        # Очищаем данные в любом случае (успех или ошибка)
        clear_natal_data(context)

async def handle_natal_input(update: Update, context: CallbackContext) -> None:
    """Обрабатывает ввод пользователя для имени, времени и места рождения."""
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    # Проверяем, ожидается ли ввод для натальной карты
    if not any(key in context.user_data for key in ["awaiting_natal_name", "awaiting_natal_time", "awaiting_natal_place"]):
        logger.debug(f"Игнорируем текст '{text}' - нет активных флагов ожидания для натальной карты")
        return

    try:
        if context.user_data.get("awaiting_natal_name"):
            context.user_data["natal_name"] = text
            context.user_data.pop("awaiting_natal_name")
            await context.bot.send_message(chat_id, "⏰ Укажите время рождения (например, '14:30'):")
            context.user_data["awaiting_natal_time"] = True

        elif context.user_data.get("awaiting_natal_time"):
            if not validate_time(text):
                await update.message.reply_text(
                    "⚠️ Неверный формат времени. Используйте 'ЧЧ:ММ' (например, '14:30'). Повторите ввод:"
                )
                return
            context.user_data["natal_time"] = text
            context.user_data.pop("awaiting_natal_time")
            await context.bot.send_message(chat_id, "📍 Укажите место рождения (например, 'Москва'):")
            context.user_data["awaiting_natal_place"] = True

        elif context.user_data.get("awaiting_natal_place"):
            context.user_data["natal_place"] = text
            context.user_data.pop("awaiting_natal_place")
            await natal_chart(update, context)

    except Exception as e:
        logger.error(f"Ошибка при обработке ввода для натальной карты: {e}")
        await context.bot.send_message(
            chat_id,
            "⚠️ Произошла ошибка при вводе данных. Начните заново с команды /natal_chart или выбора даты.",
            parse_mode="Markdown"
        )
        clear_natal_data(context)