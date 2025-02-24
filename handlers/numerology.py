import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from datetime import datetime
from services.numerology_service import calculate_life_path_number
from openai import OpenAI
import config
from utils.button_guard import button_guard
from utils.loading_messages import send_processing_message, replace_processing_message
from utils.calendar import start_calendar

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
    return bool(re.match(r"^(0[1-9]|[12][0-9]|3[01])\\.(0[1-9]|1[0-2])\\.\\d{4}$", birth_date))

def get_numerology_interpretation(life_path_number: int) -> str:
    """
    Запрашивает интерпретацию числа судьбы у OpenAI API.
    """
    prompt = f"""
    Напиши эзотерическое толкование числа судьбы {life_path_number}.
    Опиши ключевые качества личности, предназначение и кармический смысл этого числа.
    Добавь мистическую символику и советы по гармонизации энергии.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Ты эксперт в нумерологии и эзотерике."},
                      {"role": "user", "content": prompt}],
            temperature=0.7
        )

        interpretation = response.choices[0].message.content.strip()
        logger.info(f"Интерпретация числа {life_path_number}: {interpretation[:50]}...")
        return interpretation

    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenAI API: {e}")
        return "⚠️ Не удалось получить интерпретацию числа судьбы. Попробуйте позже."

@button_guard
async def numerology(update: Update, context: CallbackContext) -> None:
    """Обрабатывает команду /numerology и предлагает выбрать дату рождения."""
    await start_calendar(update, context)  # ✅ Запускаем календарь для выбора даты

async def handle_numerology_callback(update: Update, context: CallbackContext) -> None:
    """Обрабатывает callback из календаря и выполняет расчет нумерологии."""
    query = update.callback_query
    if not query:
        return
    
    logger.info(f"📥 Получен callback данные: {query.data}")
    await query.answer()

    match = re.search(r'cbcal_0_s_d_(\\d+)_(\\d+)_(\\d+)', query.data)
    if not match:
        logger.error("⚠️ Ошибка: не удалось распознать дату из callback.")
        await query.message.edit_text("⚠️ Ошибка: не удалось распознать дату. Попробуйте снова.")
        return
    
    year, month, day = match.groups()
    birth_date = f"{day}.{month}.{year}"
    context.user_data["selected_date"] = birth_date
    await query.message.edit_text(f"✅ Вы выбрали дату: {birth_date}")

    await process_numerology(update, context, birth_date)

async def process_numerology(update: Update, context: CallbackContext, birth_date: str) -> None:
    """Выполняет расчет нумерологии и отправляет результат пользователю."""
    processing_message = await send_processing_message(update, "🔢 Подготавливаем ваш нумерологический расчет...")

    try:
        life_path_number = calculate_life_path_number(birth_date)
        interpretation = get_numerology_interpretation(life_path_number)

        numerology_text = (
            f"🔢 **Ваше число судьбы: {life_path_number}**\n\n"
            f"✨ *Интерпретация:* {interpretation}\n\n"
            "🔮 Число судьбы определяет вашу главную жизненную энергию и предназначение!"
        )

        keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await replace_processing_message(context, processing_message, numerology_text, reply_markup)
    except Exception as e:
        logger.error(f"Ошибка при нумерологическом расчете: {e}")
        await replace_processing_message(context, processing_message, "⚠️ Произошла ошибка при расчете. Попробуйте позже.")
