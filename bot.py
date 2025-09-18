import logging
import os
import asyncio
from aiohttp import web
import telegram
from telegram import Update
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

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Создание приложения
app = Application.builder().token(os.environ.get("TELEGRAM_TOKEN", config.TELEGRAM_TOKEN)).build()

# Определение функций
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

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
            await update.message.reply_text("📜 Введите ваше имя:")
            context.user_data["awaiting_natal"] = True
            context.user_data["natal_step"] = "name"
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

# Регистрация хендлеров
app.add_handler(CommandHandler("start", start_handler))
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
    filters.TEXT & ~filters.COMMAND & filters.create(natal_filter),
    handle_natal_input
))
app.add_handler(MessageHandler(
    filters.TEXT & ~filters.COMMAND & filters.create(compatibility_filter),
    handle_compatibility_input
))
app.add_handler(MessageHandler(
    filters.TEXT & ~filters.COMMAND & ~filters.Regex("^(🔮 Гороскоп|🔢 Нумерология|🌌 Натальная карта|❤️ Совместимость|📜 Послание на день|🎴 Карты Таро|🔮 Предсказания|💰 На деньги|🍀 На удачу|💞 На отношения|🩺 На здоровье|🔙 Вернуться в меню)$"),
    process_horoscope
))
app.add_handler(MessageHandler(
    filters.TEXT & ~filters.COMMAND & ~filters.Regex("^(🔮 Гороскоп|🔢 Нумерология|🌌 Натальная карта|❤️ Совместимость|📜 Послание на день|🎴 Карты Таро|🔮 Предсказания|💰 На деньги|🍀 На удачу|💞 На отношения|🩺 На здоровье|🔙 Вернуться в меню)$"),
    process_numerology
))

app.add_error_handler(error_handler)

# Webhook сервер
TOKEN = os.environ.get("TELEGRAM_TOKEN", config.TELEGRAM_TOKEN)
PORT = int(os.environ.get("PORT", 8000))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
WEBHOOK_PATH = f"/{TOKEN}"

if not TOKEN:
    logger.error("TELEGRAM_TOKEN не задан.")
    raise RuntimeError("TELEGRAM_TOKEN не задан.")

async def webhook_handler(request: web.Request):
    """Обрабатывает входящие POST-запросы от Telegram."""
    try:
        data = await request.json()
    except Exception:
        text = await request.text()
        logger.warning("Получен не-JSON payload: %s", text)
        return web.Response(status=400, text="Bad Request")

    try:
        update = Update.de_json(data, app.bot)
        await app.process_update(update)
        return web.Response(status=200, text="OK")
    except Exception as e:
        logger.exception("Ошибка при обработке апдейта: %s", e)
        return web.Response(status=500, text="Internal Server Error")

async def run_webhook():
    """Инициализация БД, планировщика, установка webhook и запуск aiohttp."""
    # Инициализация БД
    await init_db()

    # Запуск планировщика
    from scheduler import schedule_daily_messages
    asyncio.create_task(schedule_daily_messages(app))

    # Установка webhook
    if WEBHOOK_URL:
        full_url = WEBHOOK_URL.rstrip("/") + WEBHOOK_PATH
        try:
            await app.bot.set_webhook(full_url)
            logger.info("Webhook установлен: %s", full_url)
        except Exception as e:
            logger.exception("Не удалось установить webhook: %s", e)
    else:
        logger.error("WEBHOOK_URL не задан.")
        raise RuntimeError("WEBHOOK_URL не задан.")

    # Запуск aiohttp сервера
    aio_app = web.Application()
    aio_app.router.add_post(WEBHOOK_PATH, webhook_handler)
    runner = web.AppRunner(aio_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info("Webhook server started on 0.0.0.0:%s%s", PORT, WEBHOOK_PATH)

    # Держим процесс живым
    while True:
        await asyncio.sleep(3600)

def main():
    """Запускает бот в webhook-режиме."""
    logger.info("Запуск webhook-режима бота...")
    try:
        asyncio.run(run_webhook())
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: %s", e)
        raise

if __name__ == "__main__":
    main()