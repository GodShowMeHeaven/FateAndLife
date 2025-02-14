import logging
import re
from telegram import Update
from telegram.ext import CallbackContext
from datetime import datetime
from services.numerology_service import calculate_life_path_number
from openai import OpenAI
import config

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Подключаем OpenAI API-ключ
client = OpenAI(api_key=config.OPENAI_API_KEY)

def validate_date(birth_date: str) -> bool:
    """Проверяет, что дата в формате ДД.ММ.ГГГГ"""
    return bool(re.match(r"^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.\d{4}$", birth_date))

def get_numerology_interpretation(life_path_number: int) -> str:
    """
    Запрашивает интерпретацию числа судьбы у OpenAI API.
    """
    prompt = f"""
    Напиши эзотерическое толкование числа судьбы {life_path_number}.
    Опиши ключевые качества личности, предназначение и кармический смысл этого числа.
    Добавь мистическую символику и советы по гармонизации энергии."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Ты эксперт в нумерологии и эзотерике."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        interpretation = response.choices[0].message.content.strip()
        logger.info(f"Интерпретация числа {life_path_number}: {interpretation[:50]}...")
        return interpretation

    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenAI API: {e}")
        return "⚠️ Не удалось получить интерпретацию числа судьбы. Попробуйте позже."

async def numerology(update: Update, context: CallbackContext) -> None:
    """Обрабатывает команду /numerology и вычисляет число судьбы"""
    if not context.args:
        await update.message.reply_text(
            "🔢 Введите вашу дату рождения в формате:\n"
            "*/numerology ДД.ММ.ГГГГ*",
            parse_mode="Markdown"
        )
        return

    birth_date = context.args[0].strip()

    if not validate_date(birth_date):
        await update.message.reply_text(
            "⚠️ *Неверный формат даты!* Введите в формате ДД.ММ.ГГГГ, например: `/numerology 12.05.1990`",
            parse_mode="Markdown"
        )
        return

    try:
        datetime.strptime(birth_date, "%d.%m.%Y")
        life_path_number = calculate_life_path_number(birth_date)

        # ✅ Убрали `await`, так как `get_numerology_interpretation()` теперь синхронная функция
        interpretation = get_numerology_interpretation(life_path_number)

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
