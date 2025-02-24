import logging
import os
import telegram  # ✅ Добавляем импорт
from telegram import Update, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, CallbackContext
)
from telegram_bot_calendar import DetailedTelegramCalendar, WMonthTelegramCalendar  # ✅ Добавляем импорт
from keyboards.main_menu import main_menu_keyboard, predictions_keyboard
from keyboards.inline_buttons import horoscope_keyboard
from handlers.horoscope import horoscope_callback
from handlers.natal_chart import natal_chart
from handlers.numerology import numerology
from handlers.tarot import tarot  # ✅ Убираем tarot_callback
from handlers.compatibility import compatibility, compatibility_natal
from handlers.compatibility_fio import compatibility_fio
from handlers.fortune import fortune_callback  
from handlers.subscription import subscribe, unsubscribe
from handlers.user_profile import set_profile, get_profile
from handlers.message_of_the_day import message_of_the_day_callback
from utils.calendar import start_calendar, handle_calendar  # ✅ Используем inline-календарь
import config
from utils.button_guard import button_guard

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

async def back_to_menu_callback(update: Update, context: CallbackContext) -> None:
    """Возвращает пользователя в главное меню."""
    query = update.callback_query
    if not query:
        logger.error("Ошибка: back_to_menu_callback вызван без callback_query.")
        return

    await query.answer()

    try:
        await query.message.edit_text("⏬ Главное меню:", reply_markup=main_menu_keyboard)
    except telegram.error.BadRequest as e:
        logger.warning(f"Ошибка при редактировании сообщения: {e}")
        await query.message.reply_text("⏬ Главное меню:", reply_markup=main_menu_keyboard)

async def start(update: Update, context: CallbackContext) -> None:
    """Отправляет приветственное сообщение и главное меню."""
    await update.message.reply_text(
        "🌟 Добро пожаловать в эзотерический бот!\nВыберите нужный раздел:",
        reply_markup=main_menu_keyboard
    )

@button_guard
async def handle_buttons(update: Update, context: CallbackContext) -> None:
    """Обрабатывает нажатия кнопок главного меню."""
    text = update.message.text
    chat_id = update.message.chat_id
    logger.info(f"Пользователь {chat_id} выбрал: {text}")

    try:
        if text == "🔮 Гороскоп":
            await update.message.reply_text("Выберите ваш знак зодиака:", reply_markup=horoscope_keyboard)
        elif text == "🔢 Нумерология":
            await update.message.reply_text("🔢 Выберите дату рождения через календарь:")
            await start_calendar(update, context)  # ✅ Запускаем inline-календарь
        elif text == "🌌 Натальная карта":
            await update.message.reply_text("📜 Выберите дату рождения для натальной карты:")
            await start_calendar(update, context)
        elif text == "❤️ Совместимость":
            await update.message.reply_text("💑 Выберите дату рождения первого человека:")
            await start_calendar(update, context)
        elif text == "📜 Послание на день":
            await message_of_the_day_callback(update, context)  # ✅ Вызываем обработчик сразу, без календаря
        elif text == "🎴 Карты Таро":
            await tarot(update, context)  # ✅ Вызываем обработчик Таро
        elif text == "🔮 Предсказания":
            await update.message.reply_text("🔮 Выберите категорию предсказания:", reply_markup=predictions_keyboard)
        elif text in ["💰 На деньги", "🍀 На удачу", "💞 На отношения", "🩺 На здоровье"]:
            await fortune_callback(update, context)
        else:
            logger.warning(f"Неизвестная команда: {text}")
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
app.add_handler(CommandHandler("tarot", tarot))  # ✅ tarot теперь вызывается только через текст
app.add_handler(CommandHandler("message_of_the_day", message_of_the_day_callback))

# Обработчики кнопок
app.add_handler(CallbackQueryHandler(back_to_menu_callback, pattern="^back_to_menu$"))
app.add_handler(CallbackQueryHandler(message_of_the_day_callback, pattern="^message_of_the_day$"))
app.add_handler(CallbackQueryHandler(handle_calendar, pattern="^cbcal_"))


# Совместимость и предсказания
app.add_handler(CommandHandler("compatibility", compatibility))
app.add_handler(CommandHandler("compatibility_natal", compatibility_natal))
app.add_handler(CommandHandler("compatibility_fio", compatibility_fio))
app.add_handler(CallbackQueryHandler(fortune_callback, pattern="^fortune_.*$"))

# Подписки и профили
app.add_handler(CommandHandler("subscribe", subscribe))
app.add_handler(CommandHandler("unsubscribe", unsubscribe))
app.add_handler(CommandHandler("set_profile", set_profile))
app.add_handler(CommandHandler("get_profile", get_profile))

# Обработчик знаков зодиака
app.add_handler(CallbackQueryHandler(horoscope_callback, pattern="^horoscope_.*$"))

# Обработчик текстовых кнопок главного меню
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

# Запуск бота
logger.info("Бот запущен!")
app.run_polling()
