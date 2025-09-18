import logging
import os
import asyncio
from aiohttp import web
import telegram
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
)
from telegram.ext.filters import BaseFilter
from telegram.helpers import escape_markdown
from telegram_bot_calendar import WMonthTelegramCalendar
from keyboards.main_menu import main_menu_keyboard, predictions_keyboard
from keyboards.inline_buttons import horoscope_keyboard
from handlers.horoscope import horoscope_callback, process_horoscope, period_callback
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
from utils.button_guard import button_guard
from services.database import init_db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Проверка переменных окружения
required_env_vars = ["TELEGRAM_TOKEN", "WEBHOOK_URL"]
for var in required_env_vars:
    if not os.environ.get(var):
        logger.error(f"{var} не найден в переменных окружения")
        raise ValueError(f"{var} не найден в переменных окружения")

# Создание приложения
telegram_token = os.environ.get("TELEGRAM_TOKEN")
app = Application.builder().token(telegram_token).build()

# Кастомные фильтры
class NatalFilter(BaseFilter):
    def filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        return bool(context.user_data.get("awaiting_natal"))

class CompatibilityFilter(BaseFilter):
    def filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        return bool(context.user_data.get("awaiting_compatibility"))

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
        logger.error("Отсутствует сообщение или effective_chat")
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
app.add_handler(CallbackQueryHandler(period_callback, pattern="^period_.*$"))
app.add_handler(CallbackQueryHandler(fortune_callback, pattern="^fortune_.*$"))

# Регистрация фильтров и хендлеров для текстового ввода
app.add_handler(MessageHandler(
    filters.Regex("^(🔮 Гороскоп|🔢 Нумерология|🌌 Натальная карта|❤️ Совместимость|📜 Послание на день|🎴 Карты Таро|🔮 Предсказания|💰 На деньги|🍀 На удачу|💞 На отношения|🩺 На здоровье|🔙 Вернуться в меню)$"),
    handle_buttons
))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & NatalFilter(), handle_natal_input))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & CompatibilityFilter(), handle_compatibility_input))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_horoscope))

# Webhook handler
async def webhook(request):
    update = telegram.Update.de_json(await request.json(), app.bot)
    await app.process_update(update)
    return web.Response()

async def main():
    logger.info("Запуск webhook-режима бота...")
    loop = asyncio.get_event_loop()
    try:
        await app.initialize()
        await init_db()
        from scheduler import schedule_daily_messages
        loop.create_task(schedule_daily_messages(app))
        webhook_url = f"{os.environ.get('WEBHOOK_URL')}/{os.environ.get('TELEGRAM_TOKEN')}"
        await app.bot.set_webhook(webhook_url)
        logger.info(f"Webhook установлен: {webhook_url}")
        webhook_app = web.Application()
        webhook_app.router.add_post(f"/{os.environ.get('TELEGRAM_TOKEN')}", webhook)
        port = int(os.environ.get("PORT", 10000))
        runner = web.AppRunner(webhook_app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()
        logger.info(f"Webhook server started on 0.0.0.0:{port}/{os.environ.get('TELEGRAM_TOKEN')}")
        await asyncio.Event().wait()
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())