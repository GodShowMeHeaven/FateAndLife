import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.horoscope_service import get_horoscope
from utils.loading_messages import send_processing_message, replace_processing_message
from utils.validation import sanitize_input
from keyboards.inline_buttons import horoscope_keyboard

logger = logging.getLogger(__name__)

async def horoscope_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает выбор знака зодиака и предлагает выбрать период гороскопа."""
    query = update.callback_query
    await query.answer()

    if not query.data or not update.effective_chat:
        logger.error("Отсутствует callback_data или effective_chat")
        return

    # Получаем знак зодиака из callback_data
    sign = query.data.replace("horoscope_", "").capitalize()
    context.user_data["selected_sign"] = sign

    # Создаём клавиатуру с выбором периода
    period_keyboard = [
        [
            InlineKeyboardButton("Гороскоп на сегодня", callback_data="period_today"),
            InlineKeyboardButton("Гороскоп на неделю", callback_data="period_week"),
            InlineKeyboardButton("Гороскоп на месяц", callback_data="period_month"),
        ],
        [InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(period_keyboard)

    # Экранируем текст для MarkdownV2
    message_text = sanitize_input(f"Вы выбрали знак: {sign}\nВыберите период для гороскопа:")

    # Редактируем сообщение, предлагая выбрать период
    try:
        await query.message.edit_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode="MarkdownV2"
        )
    except Exception as e:
        logger.error(f"Ошибка при редактировании сообщения: {e}")
        await context.bot.send_message(
            update.effective_chat.id,
            message_text,
            reply_markup=reply_markup,
            parse_mode="MarkdownV2"
        )

async def period_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает выбор периода гороскопа и отправляет гороскоп."""
    query = update.callback_query
    await query.answer()

    if not query.data or not update.effective_chat:
        logger.error("Отсутствует callback_data или effective_chat")
        return

    chat_id = update.effective_chat.id
    sign = context.user_data.get("selected_sign")
    if not sign:
        logger.error("Знак зодиака не найден в user_data")
        await query.message.edit_text(
            sanitize_input("⚠️ Пожалуйста, выберите знак зодиака заново."),
            parse_mode="MarkdownV2"
        )
        return

    period = query.data.replace("period_", "")
    period_text = {
        "today": "сегодня",
        "week": "эту неделю",
        "month": "этот месяц"
    }.get(period, "сегодня")

    logger.info(f"Пользователь {chat_id} запросил гороскоп для {sign} на {period_text}")

    processing_message = None
    try:
        # Отправляем сообщение о генерации
        processing_message = await send_processing_message(
            update,
            sanitize_input(f"🔮 Формируем гороскоп для {sign} на {period_text}..."),
            parse_mode="MarkdownV2"
        )

        # Получаем гороскоп
        horoscope_text = await get_horoscope(sign, period)

        # Экранируем текст для MarkdownV2
        horoscope_text = sanitize_input(horoscope_text)

        # Отправляем гороскоп
        await context.bot.send_message(
            chat_id,
            f"🌟 Гороскоп для {sanitize_input(sign)} на {sanitize_input(period_text)}:\n\n{horoscope_text}",
            parse_mode="MarkdownV2"
        )

        # Удаляем сообщение о генерации
        await replace_processing_message(
            context,
            processing_message,
            sanitize_input(f"✅ Гороскоп для {sign} на {period_text} готов!"),
            parse_mode="MarkdownV2"
        )

    except Exception as e:
        logger.error(f"Ошибка получения гороскопа: {e}")
        error_message = sanitize_input(f"⚠️ Ошибка: {str(e)}")
        if processing_message:
            await replace_processing_message(context, processing_message, error_message, parse_mode="MarkdownV2")
        else:
            await context.bot.send_message(chat_id, error_message, parse_mode="MarkdownV2")

async def process_horoscope(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает текстовый ввод для гороскопа (если пользователь вводит знак напрямую)."""
    if not update.message or not update.message.text or not update.effective_chat:
        logger.error("Отсутствует сообщение или effective_chat")
        return

    sign = update.message.text.strip().capitalize()
    from utils.zodiac import get_zodiac_sign
    if not get_zodiac_sign(sign):
        await update.message.reply_text(
            sanitize_input("⚠️ Пожалуйста, выберите знак зодиака из меню:"),
            reply_markup=horoscope_keyboard,
            parse_mode="MarkdownV2"
        )
        return

    context.user_data["selected_sign"] = sign
    period_keyboard = [
        [
            InlineKeyboardButton("На сегодня", callback_data="period_today"),
            InlineKeyboardButton("На неделю", callback_data="period_week"),
            InlineKeyboardButton("На месяц", callback_data="period_month"),
        ],
        [InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(period_keyboard)

    await update.message.reply_text(
        sanitize_input(f"Вы выбрали знак: {sign}\nВыберите период для гороскопа:"),
        reply_markup=reply_markup,
        parse_mode="MarkdownV2"
    )