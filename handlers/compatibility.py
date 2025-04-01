from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.compatibility_service import get_zodiac_compatibility, get_natal_compatibility
from utils.loading_messages import send_processing_message, replace_processing_message
from utils.calendar import start_calendar, handle_calendar
import logging
import re

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def escape_markdown_v2(text: str) -> str:
    """Экранирует все зарезервированные символы для MarkdownV2."""
    reserved_chars = r'([_*[\]()~`>#+-=|{}.!])'
    return re.sub(reserved_chars, r'\\\1', text)

async def compatibility(update: Update, context: CallbackContext) -> None:
    """Обрабатывает запрос совместимости по знакам зодиака."""
    if not update.message or len(context.args) < 2:
        await update.message.reply_text(
            escape_markdown_v2("💑 *Введите знаки зодиака для проверки совместимости:*\n"
                              "`/compatibility Овен Телец`"),
            parse_mode="MarkdownV2"
        )
        return

    sign1, sign2 = context.args[0].capitalize(), context.args[1].capitalize()
    processing_message = await send_processing_message(update, f"💞 Подготавливаем совместимость {sign1} и {sign2}...", context)

    try:
        compatibility_text = get_zodiac_compatibility(sign1, sign2)

        # Экранируем текст для MarkdownV2
        sign1_escaped = escape_markdown_v2(sign1)
        sign2_escaped = escape_markdown_v2(sign2)
        compatibility_text_escaped = escape_markdown_v2(compatibility_text)

        formatted_text = (
            f"💞 *Совместимость {sign1_escaped} и {sign2_escaped}*\n"
            "__________________________\n"
            f"{compatibility_text_escaped}\n"
            "__________________________\n"
            "💡 *Совет:* Используйте знание зодиака для гармонии!"
        )
        logger.debug(f"Отправляемый текст: {formatted_text}")

        # Добавляем кнопку возврата
        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await replace_processing_message(context, processing_message, formatted_text, reply_markup, parse_mode="MarkdownV2")
    except Exception as e:
        logger.error(f"Ошибка при расчете совместимости: {e}")
        error_message = escape_markdown_v2("⚠️ Ошибка при расчете совместимости. Попробуйте позже.")
        await replace_processing_message(context, processing_message, error_message, parse_mode="MarkdownV2")

async def compatibility_natal(update: Update, context: CallbackContext) -> None:
    """Обрабатывает запрос астрологической совместимости: через команду или календарь."""
    chat_id = update.effective_chat.id
    processing_message = None

    # Проверяем источник вызова: команда или календарь
    if update.message and context.args:  # Вызов через команду
        if len(context.args) < 8:
            await update.message.reply_text(
                escape_markdown_v2("🌌 *Введите данные для совместимости по натальной карте:*\n"
                                  "`/compatibility_natal Имя1 ДД.ММ.ГГГГ ЧЧ:ММ Город1 Имя2 ДД.ММ.ГГГГ ЧЧ:ММ Город2`"),
                parse_mode="MarkdownV2"
            )
            return

        name1, birth1, time1, place1 = context.args[:4]
        name2, birth2, time2, place2 = context.args[4:]

    else:  # Вызов через меню или календарь
        # Проверяем, все ли данные собраны
        required_keys = ["compat_name1", "compat_birth1", "compat_time1", "compat_place1",
                         "compat_name2", "compat_birth2", "compat_time2", "compat_place2"]
        if all(key in context.user_data for key in required_keys):
            name1 = context.user_data["compat_name1"]
            birth1 = context.user_data["compat_birth1"]
            time1 = context.user_data["compat_time1"]
            place1 = context.user_data["compat_place1"]
            name2 = context.user_data["compat_name2"]
            birth2 = context.user_data["compat_birth2"]
            time2 = context.user_data["compat_time2"]
            place2 = context.user_data["compat_place2"]
        else:
            # Если данных нет, запрашиваем имя первой персоны
            if not context.user_data.get("compat_name1") and not context.user_data.get("awaiting_compat_name1"):
                await context.bot.send_message(
                    chat_id,
                    escape_markdown_v2("📜 Укажите имя первой персоны (например, 'Анна'):"),
                    parse_mode="MarkdownV2"
                )
                context.user_data["awaiting_compat_name1"] = True
                context.user_data["awaiting_compatibility"] = True  # Указываем, что начали процесс
            return  # Ждём ввода через handle_compatibility_input

    try:
        # Отправляем сообщение о подготовке
        processing_message = await send_processing_message(update, f"🔮 Подготавливаем астрологическую совместимость {name1} и {name2}...", context)

        # Получаем совместимость
        compatibility_text = get_natal_compatibility(name1, birth1, time1, place1, name2, birth2, time2, place2)

        # Экранируем текст для MarkdownV2
        name1_escaped = escape_markdown_v2(name1)
        name2_escaped = escape_markdown_v2(name2)
        birth1_escaped = escape_markdown_v2(birth1)
        time1_escaped = escape_markdown_v2(time1)
        place1_escaped = escape_markdown_v2(place1)
        birth2_escaped = escape_markdown_v2(birth2)
        time2_escaped = escape_markdown_v2(time2)
        place2_escaped = escape_markdown_v2(place2)
        compatibility_text_escaped = escape_markdown_v2(compatibility_text)

        formatted_text = (
            f"🔮 *Астрологическая совместимость {name1_escaped} и {name2_escaped}*\n"
            "__________________________\n"
            f"{name1_escaped}: {birth1_escaped}, {time1_escaped}, {place1_escaped}\n"
            f"{name2_escaped}: {birth2_escaped}, {time2_escaped}, {place2_escaped}\n"
            f"{compatibility_text_escaped}\n"
            "__________________________\n"
            "✨ *Совет:* Используйте астрологию для гармонии в паре!"
        )
        logger.debug(f"Отправляемый текст: {formatted_text}")

        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await replace_processing_message(context, processing_message, formatted_text, reply_markup, parse_mode="MarkdownV2")

        # Очищаем временные данные
        clear_compatibility_data(context)

    except Exception as e:
        logger.error(f"Ошибка при расчете астрологической совместимости: {e}")
        error_message = escape_markdown_v2("⚠️ Ошибка при расчете совместимости. Попробуйте позже.")
        if processing_message:
            await replace_processing_message(context, processing_message, error_message, parse_mode="MarkdownV2")
        else:
            await context.bot.send_message(chat_id, error_message, parse_mode="MarkdownV2")

async def handle_compatibility_input(update: Update, context: CallbackContext) -> None:
    """Обрабатывает ввод пользователя для данных совместимости."""
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    logger.debug(f"handle_compatibility_input получил текст: '{text}', context.user_data: {context.user_data}")

    # Проверяем, ожидается ли ввод для совместимости
    if not context.user_data.get("awaiting_compatibility"):
        logger.debug(f"Пропускаем обработку текста '{text}' - процесс совместимости не активен")
        return

    try:
        if context.user_data.get("awaiting_compat_name1"):
            context.user_data["compat_name1"] = text
            context.user_data.pop("awaiting_compat_name1")
            # После ввода имени запускаем календарь для выбора даты
            await context.bot.send_message(
                chat_id,
                escape_markdown_v2("📅 Выберите дату рождения первой персоны:"),
                parse_mode="MarkdownV2"
            )
            await start_calendar(update, context)

        elif context.user_data.get("awaiting_compat_time1"):
            if not any(char.isdigit() for char in text) or ":" not in text:
                await update.message.reply_text(
                    escape_markdown_v2("⏰ Формат времени неверный. Используйте 'ЧЧ:ММ' (например, '14:30')."),
                    parse_mode="MarkdownV2"
                )
                return
            context.user_data["compat_time1"] = text
            context.user_data.pop("awaiting_compat_time1")
            await context.bot.send_message(
                chat_id,
                escape_markdown_v2("📍 Укажите место рождения первой персоны (например, 'Москва'):"),
                parse_mode="MarkdownV2"
            )
            context.user_data["awaiting_compat_place1"] = True

        elif context.user_data.get("awaiting_compat_place1"):
            context.user_data["compat_place1"] = text
            context.user_data.pop("awaiting_compat_place1")
            await context.bot.send_message(
                chat_id,
                escape_markdown_v2("📜 Укажите имя второй персоны (например, 'Иван'):"),
                parse_mode="MarkdownV2"
            )
            context.user_data["awaiting_compat_name2"] = True

        elif context.user_data.get("awaiting_compat_name2"):
            context.user_data["compat_name2"] = text
            context.user_data.pop("awaiting_compat_name2")
            # После ввода имени второй персоны запускаем календарь
            await context.bot.send_message(
                chat_id,
                escape_markdown_v2("📅 Выберите дату рождения второй персоны:"),
                parse_mode="MarkdownV2"
            )
            await start_calendar(update, context)

        elif context.user_data.get("awaiting_compat_time2"):
            if not any(char.isdigit() for char in text) or ":" not in text:
                await update.message.reply_text(
                    escape_markdown_v2("⏰ Формат времени неверный. Используйте 'ЧЧ:ММ' (например, '09:15')."),
                    parse_mode="MarkdownV2"
                )
                return
            context.user_data["compat_time2"] = text
            context.user_data.pop("awaiting_compat_time2")
            await context.bot.send_message(
                chat_id,
                escape_markdown_v2("📍 Укажите место рождения второй персоны (например, 'Санкт-Петербург'):"),
                parse_mode="MarkdownV2"
            )
            context.user_data["awaiting_compat_place2"] = True

        elif context.user_data.get("awaiting_compat_place2"):
            context.user_data["compat_place2"] = text
            context.user_data.pop("awaiting_compat_place2")
            # Все данные собраны, запускаем расчёт совместимости
            await compatibility_natal(update, context)

    except Exception as e:
        logger.error(f"Ошибка при обработке ввода для совместимости: {e}")
        await context.bot.send_message(
            chat_id,
            escape_markdown_v2("⚠️ Произошла ошибка при вводе данных. Начните заново с команды /compatibility_natal или выбора даты."),
            parse_mode="MarkdownV2"
        )
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