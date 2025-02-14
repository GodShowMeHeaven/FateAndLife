import logging
import os
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, CallbackContext
)
from keyboards.main_menu import main_menu_keyboard, horoscope_keyboard
from handlers.horoscope import horoscope_callback
from handlers.natal_chart import natal_chart
from handlers.numerology import numerology
from handlers.tarot import tarot, tarot_callback
from handlers.compatibility import compatibility, compatibility_natal, compatibility_fio
from handlers.fortune import fortune
from handlers.subscription import subscribe, unsubscribe
from handlers.user_profile import set_profile, get_profile
import openai
import config

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Подключаем OpenAI API-ключ
openai.api_key = config.OPENAI_API_KEY

async def back_to_menu_callback(update: Update, context: CallbackContext) -> None:
    """Обработчик кнопки "🔙 Вернуться в меню"."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔝 Главное меню:", reply_markup=main_menu_keyboard)

async def start(update: Update, context):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "🌟 Добро пожаловать в эзотерический бот!\nВыберите нужный раздел:",
        reply_markup=main_menu_keyboard
    )

async def handle_buttons(update: Update, context):
    """Обрабатывает кнопки главного меню"""
    text = update.message.text

    menu_actions = {
        "🔮 Гороскоп": lambda: update.message.reply_text("Выберите ваш знак зодиака:", reply_markup=horoscope_keyboard),
        "🌌 Натальная карта": lambda: update.message.reply_text(
            "📜 Введите данные в формате:\n`/natal_chart Имя ДД.ММ.ГГГГ ЧЧ:ММ Город`",
            parse_mode="Markdown"
        ),
        "🔢 Нумерология": lambda: update.message.reply_text(
            "🔢 Введите вашу дату рождения в формате:\n`/numerology ДД.ММ.ГГГГ`",
            parse_mode="Markdown"
        ),
        "🎴 Карты Таро": lambda: tarot(update, context),
        "❤️ Совместимость": lambda: update.message.reply_text(
            "💑 Выберите тип совместимости:\n"
            "1️⃣ Гороскоп: `/compatibility Овен Телец`\n"
            "2️⃣ Натальная карта: `/compatibility_natal ...`\n"
            "3️⃣ ФИО и дата рождения: `/compatibility_fio ...`",
            parse_mode="Markdown"
        )
    }

    if text in menu_actions:
        await menu_actions[text]()
    elif text in ["💰 Предсказание на деньги", "🍀 Предсказание на удачу", "💞 Предсказание на отношения", "🩺 Предсказание на здоровье"]:
        await fortune(update, context)
    elif text == "📜 Послание на день":
        await update.message.reply_text("✨ Ваше послание на день: ... (тут вызов OpenAI)")
    else:
        await update.message.reply_text("⚠️ Неизвестная команда. Используйте меню.")

# Создание бота
app = Application.builder().token(config.TELEGRAM_TOKEN).build()

# Регистрация хендлеров
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(horoscope_callback, pattern="^horoscope_.*$"))
app.add_handler(CallbackQueryHandler(tarot_callback, pattern="^draw_tarot$|^prev_tarot$|^next_tarot$"))
app.add_handler(CallbackQueryHandler(back_to_menu_callback, pattern="^back_to_menu$"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

logger.info("Бот запущен!")
app.run_polling()
