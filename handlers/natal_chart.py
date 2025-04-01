from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.natal_chart_service import get_natal_chart
from utils.loading_messages import send_processing_message, replace_processing_message
import logging
import re

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG  # Устанавливаем DEBUG для большей детализации
)
logger = logging.getLogger(__name__)

def escape_markdown_v2(text: str) -> str:
    """Экранирует все зарезервированные символы для MarkdownV2."""
    reserved_chars = r'([_*[\]()~`>#+-=|{}.!])'
    result = re.sub(reserved_chars, r'\\\1', text)
    logger.debug(f"Экранированный текст в escape_markdown_v2: {result[:500]}...")  # Ограничим до 500 символов
    return result

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

    logger.debug(f"Текущее состояние context.user_data: {context.user_data}")

    if update.message and context.args:
        if len(context.args) < 4:
            await update.message.reply_text(
                escape_markdown_v2("📜 *Введите данные для натальной карты в формате:*\n"
                                   "`/natal_chart Имя ДД.ММ.ГГГГ ЧЧ:ММ Город`"),
                parse_mode="MarkdownV2"
            )
            return

        name, birth_date, birth_time, birth_place = context.args[0], context.args[1], context.args[2], " ".join(context.args[3:])
        if not validate_date(birth_date) or not validate_time(birth_time):
            await update.message.reply_text(
                escape_markdown_v2("⚠️ Неверный формат даты или времени. Используйте 'ДД.ММ.ГГГГ ЧЧ:ММ' (например, '12.05.1990 14:30')."),
                parse_mode="MarkdownV2"
            )
            return

    elif context.user_data.get("selected_date"):
        birth_date = context.user_data["selected_date"]
        if not context.user_data.get("natal_name"):
            await context.bot.send_message(chat_id, escape_markdown_v2("📜 Пожалуйста, укажите ваше имя для натальной карты (например, 'Анна'):"), parse_mode="MarkdownV2")
            context.user_data["awaiting_natal_name"] = True
            return
        if not context.user_data.get("natal_time"):
            await context.bot.send_message(chat_id, escape_markdown_v2("⏰ Укажите время рождения (например, '14:30'):"), parse_mode="MarkdownV2")
            context.user_data["awaiting_natal_time"] = True
            return
        if not context.user_data.get("natal_place"):
            await context.bot.send_message(chat_id, escape_markdown_v2("📍 Укажите место рождения (например, 'Москва'):"), parse_mode="MarkdownV2")
            context.user_data["awaiting_natal_place"] = True
            return

        name = context.user_data["natal_name"]
        birth_time = context.user_data["natal_time"]
        birth_place = context.user_data["natal_place"]
        if not validate_date(birth_date) or not validate_time(birth_time):
            await context.bot.send_message(chat_id, escape_markdown_v2("⚠️ Неверный формат даты или времени. Начните заново."), parse_mode="MarkdownV2")
            clear_natal_data(context)
            return

    else:
        logger.warning("⚠️ natal_chart вызван без команды или данных календаря")
        await context.bot.send_message(chat_id, escape_markdown_v2("⚠️ Используйте команду `/natal_chart Имя ДД.ММ.ГГГГ ЧЧ:ММ Город` или выберите дату через меню."), parse_mode="MarkdownV2")
        clear_natal_data(context)
        return

    try:
        processing_message = await send_processing_message(update, escape_markdown_v2(f"🌌 Подготавливаем вашу натальную карту для {name}..."), context)
        natal_chart_text = await get_natal_chart(name, birth_date, birth_time, birth_place)
        logger.debug(f"Текст от OpenAI: {natal_chart_text[:500]}...")

        # Формируем текст без предварительного экранирования
        formatted_chart_raw = (
            f"🌌 Анализ вашей натальной карты:\n"
            "__________________________\n"
            f"Дата рождения: {birth_date}, Время: {birth_time}, Место: {birth_place}\n"
            f"{natal_chart_text}\n"
            "__________________________\n"
            "✨ Совет: Используйте знания натальной карты для развития!"
        )
        logger.debug(f"Сырой текст перед экранированием: {formatted_chart_raw[:500]}...")

        # Экранируем весь текст целиком
        formatted_chart = escape_markdown_v2(formatted_chart_raw)
        logger.debug(f"Экранированный текст перед отправкой: {formatted_chart[:500]}...")

        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await replace_processing_message(context, processing_message, formatted_chart, reply_markup, parse_mode="MarkdownV2")

    except Exception as e:
        logger.error(f"Ошибка при обработке натальной карты: {e}")
        error_message = escape_markdown_v2("⚠️ Произошла ошибка при обработке запроса. Попробуйте позже.")
        if processing_message:
            await replace_processing_message(context, processing_message, error_message, parse_mode="MarkdownV2")
        else:
            await context.bot.send_message(chat_id, error_message, parse_mode="MarkdownV2")
        raise

    finally:
        clear_natal_data(context)

async def handle_natal_input(update: Update, context: CallbackContext) -> None:
    """Обрабатывает ввод пользователя для имени, времени и места рождения."""
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    logger.debug(f"handle_natal_input получил текст: '{text}', context.user_data: {context.user_data}")

    awaiting_keys = ["awaiting_natal_name", "awaiting_natal_time", "awaiting_natal_place"]
    if not any(key in context.user_data for key in awaiting_keys):
        logger.debug(f"Пропускаем обработку текста '{text}' - нет активных флагов ожидания для натальной карты")
        return

    try:
        if context.user_data.get("awaiting_natal_name"):
            context.user_data["natal_name"] = text
            context.user_data.pop("awaiting_natal_name")
            await context.bot.send_message(chat_id, escape_markdown_v2("⏰ Укажите время рождения (например, '14:30'):"), parse_mode="MarkdownV2")
            context.user_data["awaiting_natal_time"] = True
            logger.info(f"Имя '{text}' сохранено, установлен флаг awaiting_natal_time")

        elif context.user_data.get("awaiting_natal_time"):
            if not validate_time(text):
                await update.message.reply_text(escape_markdown_v2("⚠️ Неверный формат времени. Используйте 'ЧЧ:ММ' (например, '14:30'). Повторите ввод:"), parse_mode="MarkdownV2")
                return
            context.user_data["natal_time"] = text
            context.user_data.pop("awaiting_natal_time")
            await context.bot.send_message(chat_id, escape_markdown_v2("📍 Укажите место рождения (например, 'Москва'):"), parse_mode="MarkdownV2")
            context.user_data["awaiting_natal_place"] = True
            logger.info(f"Время '{text}' сохранено, установлен флаг awaiting_natal_place")

        elif context.user_data.get("awaiting_natal_place"):
            context.user_data["natal_place"] = text
            context.user_data.pop("awaiting_natal_place")
            logger.info(f"Место '{text}' сохранено, вызываем natal_chart")
            await natal_chart(update, context)

    except Exception as e:
        logger.error(f"Ошибка при обработке ввода для натальной карты: {e}")
        await context.bot.send_message(chat_id, escape_markdown_v2("⚠️ Произошла ошибка при вводе данных. Начните заново с команды /natal_chart или выбора даты."), parse_mode="MarkdownV2")
        clear_natal_data(context)