import logging
import re
from telegram import Update
from telegram.ext import CallbackContext
from datetime import datetime
from services.numerology_service import calculate_life_path_number, get_numerology_interpretation

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)
def validate_date(birth_date: str) -> bool:
    """Проверяет, что дата в формате ДД.ММ.ГГГГ"""
    return bool(re.match(r"^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.\d{4}$", birth_date))

async def numerology(update: Update, context: CallbackContext) -> None:
    if not context.args:
        await update.message.reply_text(
            "🔢 Введите вашу дату рождения в формате:\n"
            "*/numerology ДД.ММ.ГГГГ*",
            parse_mode="Markdown"
        )
        return

    birth_date = context.args[0].strip()

    # Проверяем формат даты с помощью регулярного выражения
    if not re.match(r"\d{2}\.\d{2}\.\d{4}$", birth_date):
        await update.message.reply_text(
            "⚠️ *Неверный формат даты!* Введите в формате ДД.ММ.ГГГГ, например: `/numerology 12.05.1990`",
            parse_mode="Markdown"
        )
        return

    try:
        # Проверяем валидность даты
        date_obj = datetime.strptime(birth_date, "%d.%m.%Y")
        life_path_number = calculate_life_path_number(birth_date)

        # Запрашиваем интерпретацию у OpenAI API
        interpretation = await get_numerology_interpretation(life_path_number)  # ✅ Добавлен await

        numerology_text = (
            f"🔢 **Ваше число судьбы: {life_path_number}**\n\n"
            f"✨ *Интерпретация:* {interpretation}\n\n"
            "🔮 Число судьбы определяет вашу главную жизненную энергию и предназначение!"
        )

        await update.message.reply_text(numerology_text, parse_mode="Markdown")

    except ValueError:
        await update.message.reply_text(
            "⚠️ *Неверная дата!* Введите дату в формате ДД.ММ.ГГГГ, например: `/numerology 12.05.1990`",
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error(f"Ошибка при обработке команды /numerology: {e}")
        await update.message.reply_text(
            "⚠️ Произошла ошибка при обработке запроса. Попробуйте позже.",
            parse_mode="Markdown"
        )
