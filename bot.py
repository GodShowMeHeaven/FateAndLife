import logging
import os
import asyncio
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from keyboards.main_menu import main_menu_keyboard
from keyboards.inline_buttons import horoscope_keyboard
from handlers.horoscope import horoscope
from handlers.natal_chart import natal_chart
from handlers.numerology import numerology
from handlers.tarot import tarot, tarot_callback
from handlers.compatibility import compatibility
from handlers.compatibility_natal import compatibility_natal
from handlers.compatibility_fio import compatibility_fio
from handlers.fortune import fortune
from handlers.subscription import subscribe, unsubscribe
from handlers.user_profile import set_profile, get_profile
from scheduler import schedule_daily_messages
import openai
import config
import httpx

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Подключаем OpenAI API-ключ
openai.api_key = config.OPENAI_API_KEY

# Список карт Таро
tarot_cards = [
    "Шут", "Маг", "Верховная Жрица", "Императрица", "Император",
    "Иерофант", "Влюбленные", "Колесница", "Справедливость", "Отшельник",
    "Колесо Фортуны", "Сила", "Повешенный", "Смерть", "Умеренность",
    "Дьявол", "Башня", "Звезда", "Луна", "Солнце", "Суд", "Мир"
]

# Асинхронные функции для работы с OpenAI
async def ask_openai(prompt: str) -> str:
    """
    Отправляет запрос к OpenAI API для получения интерпретации.
    """
    try:
        # Используем chat/completions вместо completions
        response = openai.chat.completions.create(  # ✅ Новый метод!
            model="gpt-3.5-turbo",  # Указываем чат-модель
            messages=[{"role": "user", "content": prompt}],  # ✅ Новый формат API
            max_tokens=150,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenAI: {e}")
        return f"⚠️ Ошибка при получении данных: {e}"

async def get_tarot_interpretation() -> str:
    """Запрашивает у OpenAI интерпретацию случайной карты Таро."""
    card = random.choice(tarot_cards)
    prompt = (
        f"Вытащи карту Таро: {card}. Объясни ее значение с точки зрения судьбы, любви, карьеры и духовного пути."
    )
    interpretation = await ask_openai(prompt)  # Используем await для асинхронного вызова
    return f"🎴 **Ваша карта Таро: {card}**\n\n{interpretation}"

async def get_natal_chart(name: str, birth_date: str, birth_time: str, birth_place: str) -> str:
    """Запрос к OpenAI для анализа натальной карты."""
    prompt = (
        f"Создай эзотерический анализ натальной карты для {name}. "
        f"Дата рождения: {birth_date}, Время рождения: {birth_time}, Место: {birth_place}. "
        "Опиши характер, предназначение, скрытые таланты и ключевые события судьбы."
    )
    return await ask_openai(prompt)  # Используем await для асинхронного вызова

# Функция приветствия
async def start(update: Update, context):
    await update.message.reply_text(
        "🌟 Добро пожаловать в эзотерический бот!\n"
        "Выберите нужный раздел:",
        reply_markup=main_menu_keyboard
    )

# Функция обработки нажатий кнопок
async def handle_buttons(update: Update, context):
    text = update.message.text

    try:
        if text == "🔮 Гороскоп":
            await update.message.reply_text("Выберите ваш знак зодиака:", reply_markup=horoscope_keyboard)
        elif text == "💰 Предсказание на деньги":
            await fortune(update, context)
        elif text == "🍀 Предсказание на удачу":
            await fortune(update, context)
        elif text == "💞 Предсказание на отношения":
            await fortune(update, context)
        elif text == "🩺 Предсказание на здоровье":
            await fortune(update, context)
        elif text == "🌌 Натальная карта":
            await update.message.reply_text(
                "📜 Введите данные в формате:\n"
                "`/natal_chart Имя ДД.ММ.ГГГГ ЧЧ:ММ Город`",
                parse_mode="Markdown"
            )
        elif text == "🔢 Нумерология":
            await update.message.reply_text(
                "🔢 Введите вашу дату рождения в формате:\n"
                "`/numerology ДД.ММ.ГГГГ`",
                parse_mode="Markdown"
            )
        elif text == "🎴 Карты Таро":
            await tarot(update, context)
        elif text == "❤️ Совместимость":
            await update.message.reply_text(
                "💑 Выберите тип совместимости:\n"
                "1️⃣ Гороскоп: `/compatibility Овен Телец`\n"
                "2️⃣ Натальная карта: `/compatibility_natal Имя1 ДД.ММ.ГГГГ ЧЧ:ММ Город1 Имя2 ДД.ММ.ГГГГ ЧЧ:ММ Город2`\n"
                "3️⃣ ФИО и дата рождения: `/compatibility_fio Имя1 Фамилия1 ДД.ММ.ГГГГ Имя2 Фамилия2 ДД.ММ.ГГГГ`",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("⚠️ Неизвестная команда. Используйте меню.", parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка при обработке кнопки: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка. Попробуйте снова.")

# Создаем бота
app = Application.builder().token(config.TELEGRAM_TOKEN).get_updates_http_version("1.1").build()

# Добавляем обработчики команд
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("horoscope", horoscope))
app.add_handler(CommandHandler("natal_chart", natal_chart))
app.add_handler(CommandHandler("numerology", numerology))
app.add_handler(CommandHandler("tarot", tarot))
app.add_handler(CallbackQueryHandler(tarot_callback, pattern="^draw_tarot$"))
app.add_handler(CallbackQueryHandler(tarot_callback, pattern="^prev_tarot$"))
app.add_handler(CallbackQueryHandler(tarot_callback, pattern="^next_tarot$"))
app.add_handler(CommandHandler("compatibility", compatibility))
app.add_handler(CommandHandler("compatibility_natal", compatibility_natal))
app.add_handler(CommandHandler("compatibility_fio", compatibility_fio))
app.add_handler(CommandHandler("fortune", fortune))
app.add_handler(CommandHandler("subscribe", subscribe))
app.add_handler(CommandHandler("unsubscribe", unsubscribe))
app.add_handler(CommandHandler("set_profile", set_profile))
app.add_handler(CommandHandler("get_profile", get_profile))

# Обработчик нажатий на кнопки
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

# Запускаем бота
logger.info("Бот запущен!")
app.run_polling()

# Настройка фоновых задач
async def main():
    """Запускает бота и фоновые задачи."""
    asyncio.create_task(schedule_daily_messages())  # Запускаем ежедневные гороскопы
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
