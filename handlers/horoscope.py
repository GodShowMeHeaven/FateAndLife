from telegram import Update
from telegram.ext import CallbackContext
from services.horoscope_service import get_horoscope
from utils.zodiac import get_zodiac_sign

async def horoscope(update: Update, context: CallbackContext) -> None:
    if not context.args:
        await update.message.reply_text(
            "🔮 Введите ваш знак зодиака или дату рождения в формате:\n"
            "*/horoscope Овен* или */horoscope 12.05.1990*"
        )
        return

    user_input = context.args[0]

    # Если введена дата, определяем знак зодиака
    if "." in user_input:
        sign = get_zodiac_sign(user_input)
        if "⚠️" in sign:
            await update.message.reply_text("⚠️ Неверный формат даты! Введите: `/horoscope 12.05.1990`")
            return
    else:
        sign = user_input.capitalize()

    # Проверяем знак
    valid_signs = [
        "Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева",
        "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"
    ]

    if sign not in valid_signs:
        await update.message.reply_text("⚠️ Неверный знак зодиака! Введите, например: `/horoscope Лев`")
        return

    horoscope_text = get_horoscope(sign)

    await update.message.reply_text(horoscope_text, parse_mode="Markdown")
