from telegram import Update
from telegram.ext import CallbackContext
from services.numerology_service import calculate_life_path_number, get_numerology_interpretation
import datetime

async def numerology(update: Update, context: CallbackContext) -> None:
    if not context.args:
        await update.message.reply_text(
            "🔢 Введите вашу дату рождения в формате:\n"
            "*/numerology ДД.ММ.ГГГГ*",
            parse_mode="Markdown"
        )
        return

    birth_date = context.args[0]

    try:
        # Проверяем валидность даты
        date_obj = datetime.strptime(birth_date, "%d.%m.%Y")
        life_path_number = calculate_life_path_number(birth_date)

        # Запрашиваем интерпретацию у OpenAI
        interpretation = get_numerology_interpretation(life_path_number)

        numerology_text = (
            f"🔢 **Ваше число судьбы: {life_path_number}**\n\n"
            f"✨ *Интерпретация:* {interpretation}\n\n"
            "🔮 Число судьбы определяет вашу главную жизненную энергию и предназначение!"
        )

        await update.message.reply_text(numerology_text, parse_mode="Markdown")

    except ValueError:
        await update.message.reply_text(
            "⚠️ *Неверный формат даты!* Введите в формате ДД.ММ.ГГГГ, например: `/numerology 12.05.1990`",
            parse_mode="Markdown"
        )
