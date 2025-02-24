from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.natal_chart_service import get_natal_chart
from utils.loading_messages import send_processing_message, replace_processing_message
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    else:
        # Неизвестный вызов: ни команды, ни данных от календаря
        logger.warning("⚠️ natal_chart вызван без команды или данных календаря")
        await context.bot.send_message(
            chat_id,
            "⚠️ Используйте команду `/natal_chart Имя ДД.ММ.ГГГГ ЧЧ:ММ Город` или выберите дату через меню.",
            parse_mode="Markdown"
        )
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

        # Очищаем временные данные после успешного выполнения
        context.user_data.pop("natal_name", None)
        context.user_data.pop("natal_time", None)
        context.user_data.pop("natal_place", None)
        context.user_data.pop("selected_date", None)

    except Exception as e:
        logger.error(f"Ошибка при обработке натальной карты: {e}")
        error_message = "⚠️ Произошла ошибка при обработке запроса. Попробуйте позже."
        if processing_message:
            await replace_processing_message(context, processing_message, error_message)
        else:
            await context.bot.send_message(chat_id, error_message, parse_mode="Markdown")

async def handle_natal_input(update: Update, context: CallbackContext) -> None:
    """Обрабатывает ввод пользователя для имени, времени и места рождения."""
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    if context.user_data.get("awaiting_natal_name"):
        context.user_data["natal_name"] = text
        context.user_data.pop("awaiting_natal_name")
        await context.bot.send_message(chat_id, "⏰ Укажите время рождения (например, '14:30'):")
        context.user_data["awaiting_natal_time"] = True

    elif context.user_data.get("awaiting_natal_time"):
        # Простая проверка формата времени (ЧЧ:ММ)
        if not any(char.isdigit() for char in text) or ":" not in text:
            await update.message.reply_text("⏰ Формат времени неверный. Используйте 'ЧЧ:ММ' (например, '14:30').")
            return
        context.user_data["natal_time"] = text
        context.user_data.pop("awaiting_natal_time")
        await context.bot.send_message(chat_id, "📍 Укажите место рождения (например, 'Москва'):")
        context.user_data["awaiting_natal_place"] = True

    elif context.user_data.get("awaiting_natal_place"):
        context.user_data["natal_place"] = text
        context.user_data.pop("awaiting_natal_place")
        # Все данные собраны, вызываем natal_chart
        await natal_chart(update, context)