import logging
import os
import random
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, CallbackContext
)
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
from handlers.message_of_the_day import message_of_the_day_callback
from scheduler import schedule_daily_messages
from services.openai_service import ask_openai
import openai
import config
import httpx
from services.horoscope_service import get_horoscope  # Импортируем правильную функцию
from keyboards.main_menu import main_menu_keyboard
from utils.button_guard import button_guard  # ✅ Импорт защиты кнопок

async def back_to_menu_callback(update: Update, context: CallbackContext) -> None:
    """Возвращает пользователя в главное меню с защитой от спама."""
    query = update.callback_query
    if query:
        await query.answer()  # ✅ Подтверждаем callback
        await query.message.reply_text("⏬ Главное меню:", reply_markup=main_menu_keyboard)

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Подключаем OpenAI API-ключ
openai.api_key = config.OPENAI_API_KEY

# Функция приветствия
async def start(update: Update, context: CallbackContext) -> None:
    """Отправляет приветственное сообщение и главное меню."""
    await update.message.reply_text(
        "🌟 Добро пожаловать в эзотерический бот!\nВыберите нужный раздел:",
        reply_markup=main_menu_keyboard
    )

@button_guard
async def handle_buttons(update: Update, context: CallbackContext) -> None:
    """Обрабатывает нажатия кнопок главного меню с защитой от многократных нажатий"""
    text = update.message.text
    chat_id = update.message.chat_id

    logger.info(f"Пользователь {chat_id} выбрал: {text}")

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
        logger.error(f"Ошибка при обработке кнопки {text}: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка. Попробуйте снова.")

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
app.add_handler(CallbackQueryHandler(back_to_menu_callback, pattern="^back_to_menu$"))
app.add_handler(CommandHandler("message_of_the_day", message_of_the_day_callback))
app.add_handler(CallbackQueryHandler(message_of_the_day_callback, pattern="^message_of_the_day$"))
# Добавляем обработчик для кнопок знаков зодиака (callback_data)
app.add_handler(CallbackQueryHandler(horoscope_callback, pattern="^horoscope_.*$"))

# Обработчик текстовых кнопок главного меню с защитой от многократных нажатий
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

# Запуск бота
logger.info("Бот запущен!")
app.run_polling()
