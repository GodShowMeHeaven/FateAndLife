import logging
import re
from telegram import Update
from telegram.ext import CallbackContext
from services.horoscope_service import get_horoscope
from utils.zodiac import get_zodiac_sign

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def horoscope(update: Update, context: CallbackContext) -> None:
    if not context.args:
        await update.message.reply_text(
            "🔮 Введите ваш знак зодиака или дату рождения в формате:\n"
            "*/horoscope Овен* или */horoscope 12.05.1990*"
        )
        return

    user_input = context.args[0]

    # Проверяем, является ли ввод датой
    if re.match(r"\d{2}\.\d{2}\.\d{4}$", user_input):  # Формат: ДД.ММ.ГГГГ
        sign = get_zodiac_sign(user_input)
        if "⚠️" in sign:  # Если знак зодиака не может быть определен
            await update.message.reply_text("⚠️ Неверный формат даты! Введите: `/horoscope 12.05.1990`")
            return
    else:
        sign = user_input.strip().capitalize()

    # Проверяем, что введенный знак зодиака валиден
    valid_signs = [
        "Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева",
        "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"
    ]

    if sign not in valid_signs:
        await update.message.reply_text(
            "⚠️ Неверный знак зодиака! Введите, например: `/horoscope Лев`"
        )
        return

    # Получаем гороскоп для этого знака
    try:
        horoscope_text = await get_horoscope(sign)  # Асинхронный вызов
        await update.message.reply_text(horoscope_text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка при получении гороскопа для {sign}: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка при получении гороскопа. Попробуйте позже.")
