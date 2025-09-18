import logging
import os
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
)
from telegram.helpers import escape_markdown
from telegram_bot_calendar import WMonthTelegramCalendar
from keyboards.main_menu import main_menu_keyboard, predictions_keyboard
from keyboards.inline_buttons import horoscope_keyboard
from handlers.horoscope import horoscope_callback, process_horoscope
from handlers.natal_chart import natal_chart, handle_natal_input
from handlers.numerology import numerology, process_numerology
from handlers.tarot import tarot
from handlers.compatibility import compatibility, compatibility_natal, handle_compatibility_input
from handlers.compatibility_fio import compatibility_fio
from handlers.fortune import fortune_callback
from handlers.subscription import subscribe, unsubscribe
from handlers.user_profile import set_profile, get_profile
from handlers.message_of_the_day import message_of_the_day_callback
from utils.calendar import start_calendar, handle_calendar
import config
from utils.button_guard import button_guard
from services.database import init_db
import asyncio

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

async def back_to_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        logger.error("Ошибка: back_to_menu_callback вызван без callback_query.")
        return

    await query.answer()
    if not update.effective_chat:
        logger.error("Отсутствует effective_chat в update")
        return
    chat_id = update.effective_chat.id

    try:
        await query.message.edit_text("⏬ Главное меню:", reply_markup=main_menu_keyboard)
    except telegram.error.BadRequest as e:
        logger.warning(f"Ошибка при редактировании сообщения: {e}")
        await context.bot.send_message(chat_id, "⏬ Главное меню:", reply_markup=main_menu_keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat:
        logger.error("Отсутствует effective_chat в update")
        return
    await update.message.reply_text(
        "🌟 Добро пожаловать в эзотерический бот!\nВыберите нужный раздел:",
        reply_markup=main_menu_keyboard
    )

@button_guard
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text or not update.effective_chat:
        logger.error("Отсутствует сообщение или effective_chat в update")
        return

    text = update.message.text
    chat_id = update.message.chat_id
    logger.debug(f"Пользователь {chat_id} выбрал: {text}")

    try:
        if text == "🔮 Гороскоп":
            await update.message.reply_text("Выберите ваш знак зодиака:", reply_markup=horoscope_keyboard)
        elif text == "🔢 Нумерология":
            await update.message.reply_text("🔢 Выберите дату рождения через календарь:")
            context.user_data["awaiting_numerology"] = True
            await start_calendar(update, context)
        elif text == "🌌 Натальная карта":
            await update.message.reply_text("📜 Выберите дату рождения для натальной карты:")
            context.user_data["awaiting_natal"] = True
            await start_calendar(update, context)
        elif text == "❤️ Совместимость":
            await update.message.reply_text("💑 Выберите дату рождения первого человека:")
            context.user_data["awaiting_compatibility"] = True
            await start_calendar(update, context)
        elif text == "📜 Послание на день":
            await message_of_the_day_callback(update, context)
        elif text == "🎴 Карты Таро":
            await tarot(update, context)
        elif text == "🔮 Предсказания":
            await update.message.reply_text("🔮 Выберите категорию предсказания:", reply_markup=predictions_keyboard)
        elif text in ["💰 На деньги", "🍀 На удачу", "💞 На отношения", "🩺 На здоровье"]:
            await fortune_callback(update, context)
        elif text == "🔙 Вернуться в меню":
            await update.message.reply_text("⏬ Главное меню:", reply_markup=main_menu_keyboard)
        else:
            logger.warning(f"Неизвестная команда: {text}")
            await update.message.reply_text("⚠️ Неизвестная команда. Используйте меню.")
    except Exception as e:
        logger.error(f"Ошибка при обработке кнопки {text}: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка. Попробуйте снова.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Ошибка в обработке обновления: {context.error}")
    if update and update.effective_chat:
        await context.bot.send_message(update.effective_chat.id, "⚠️ Произошла ошибка. Попробуйте позже.")

def natal_filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    return bool(context.user_data.get("awaiting_natal"))

def compatibility_filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    return bool(context.user_data.get("awaiting_compatibility"))

app = Application.builder().token(config.TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("natal_chart", natal_chart))
app.add_handler(CommandHandler("numerology", numerology))
app.add_handler(CommandHandler("tarot", tarot))
app.add_handler(CommandHandler("message_of_the_day", message_of_the_day_callback))
app.add_handler(CommandHandler("compatibility", compatibility))
app.add_handler(CommandHandler("compatibility_natal", compatibility_natal))
app.add_handler(CommandHandler("compatibility_fio", compatibility_fio))
app.add_handler(CommandHandler("subscribe", subscribe))
app.add_handler(CommandHandler("unsubscribe", unsubscribe))
app.add_handler(CommandHandler("set_profile", set_profile))
app.add_handler(CommandHandler("get_profile", get_profile))

app.add_handler(CallbackQueryHandler(back_to_menu_callback, pattern="^back_to_menu$"))
app.add_handler(CallbackQueryHandler(message_of_the_day_callback, pattern="^message_of_the_day$"))
app.add_handler(CallbackQueryHandler(handle_calendar, pattern="^cbcal_"))
app.add_handler(CallbackQueryHandler(horoscope_callback, pattern="^horoscope_.*$"))
app.add_handler(CallbackQueryHandler(fortune_callback, pattern="^fortune_.*$"))

app.add_handler(MessageHandler(
    filters.Regex("^(🔮 Гороскоп|🔢 Нумерология|🌌 Натальная карта|❤️ Совместимость|📜 Послание на день|🎴 Карты Таро|🔮 Предсказания|💰 На деньги|🍀 На удачу|💞 На отношения|🩺 На здоровье|🔙 Вернуться в меню)$"),
    handle_buttons
))
app.add_handler(MessageHandler(
    filters.TEXT & ~filters.COMMAND,
    natal_filter,
    handle_natal_input
))
app.add_handler(MessageHandler(
    filters.TEXT & ~filters.COMMAND,
    compatibility_filter,
    handle_compatibility_input
))
app.add_handler(MessageHandler(
    filters.TEXT & ~filters.COMMAND & ~filters.Regex("^(🔮 Гороскоп|🔢 Нумерология|🌌 Натальная карта|❤️ Совместимость|📜 Послание на день|🎴 Карты Таро|🔮 Предсказания|💰 На деньги|🍀 На удачу|💞 На отношения|🩺 На здоровье|🔙 Вернуться в меню)$"),
    process_horoscope
))
app.add_handler(MessageHandler(
    filters.TEXT & ~filters.COMMAND,
    process_numerology
))

app.add_error_handler(error_handler)

def main():
    """Запускает приложение и планировщик."""
    loop = asyncio.get_event_loop()
    
    # Run async init
    loop.run_until_complete(init_db())
    
    # Start scheduler task
    from scheduler import schedule_daily_messages
    loop.create_task(schedule_daily_messages(app))
    
    logger.info("Бот запущен!")
    
    # Run polling (synchronous)
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()