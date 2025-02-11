import logging
import os
import asyncio
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, CallbackContext
from keyboards.main_menu import main_menu_keyboard
from keyboards.inline_buttons import horoscope_keyboard
from handlers.horoscope import horoscope_callback  # Используем правильную функцию
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
from services.openai_service import ask_openai
import openai
import asyncio
import config
import httpx
from services.horoscope_service import get_horoscope  # Импортируем правильную функцию
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

def get_tarot_interpretation() -> str:
    """Запрашивает у OpenAI интерпретацию случайной карты Таро."""
    card = random.choice(tarot_cards)
    prompt = (
        f"Вытащи карту Таро: {card}. Объясни ее значение с точки зрения судьбы, любви, карьеры и духовного пути."
    )
    interpretation = ask_openai(prompt)  
    return f"🎴 **Ваша карта Таро: {card}**\n\n{interpretation}"

def get_natal_chart(name: str, birth_date: str, birth_time: str, birth_place: str) -> str:
    """Запрос к OpenAI для анализа натальной карты."""
    prompt = (
        f"Создай эзотерический анализ натальной карты для {name}. "
        f"Дата рождения: {birth_date}, Время рождения: {birth_time}, Место: {birth_place}. "
        "Опиши характер, предназначение, скрытые таланты и ключевые события судьбы."
    )
    return ask_openai(prompt)  # ❌ Убрали await, так как ask_openai() синхронный

# Функция приветствия
async def start(update: Update, context):
    await update.message.reply_text(
        "🌟 Добро пожаловать в эзотерический бот!\nВыберите нужный раздел:",
        reply_markup=main_menu_keyboard
    )

# Обработчик кнопок главного меню
async def handle_buttons(update: Update, context):
    text = update.message.text

    try:
        if text == "🔮 Гороскоп":
            await update.message.reply_text("Выберите ваш знак зодиака:", reply_markup=horoscope_keyboard)
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
        elif text in ["💰 Предсказание на деньги", "🍀 Предсказание на удачу", "💞 Предсказание на отношения", "🩺 Предсказание на здоровье"]:
            await fortune(update, context)
        elif text == "📜 Послание на день":
            await update.message.reply_text("✨ Ваше послание на день: ... (тут вызов OpenAI)")
        else:
            await update.message.reply_text("⚠️ Неизвестная команда. Используйте меню.")
    except Exception as e:
        logger.error(f"Ошибка при обработке кнопки: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка. Попробуйте снова.")

async def horoscope_callback(update: Update, context: CallbackContext):
    """Обрабатывает нажатие кнопки знака зодиака и запрашивает гороскоп у OpenAI."""
    query = update.callback_query
    sign = query.data.replace('horoscope_', '').capitalize()  # Извлекаем знак зодиака из callback_data

    try:
        horoscope_text = await get_horoscope(sign)  # Запрашиваем гороскоп
        await query.answer()  # Подтверждаем нажатие
        await query.edit_message_text(f"🔮 Ваш гороскоп для *{sign}*:\n\n{horoscope_text}", parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Ошибка при получении гороскопа для {sign}: {e}")
        await query.answer()
        await query.edit_message_text("⚠️ Произошла ошибка при получении гороскопа. Попробуйте позже.")

# Создаем бота
app = Application.builder().token(config.TELEGRAM_TOKEN).build()

# Добавляем обработчики команд
app.add_handler(CommandHandler("start", start))
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

# Добавляем обработчик для кнопок знаков зодиака (callback_data)
app.add_handler(CallbackQueryHandler(horoscope_callback, pattern="^horoscope_.*$"))

# Обработчик текстовых кнопок главного меню
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

# Запускаем бота
logger.info("Бот запущен!")


# Запуск фоновых задач
async def main():
    """Запускает бота и фоновые задачи."""
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
