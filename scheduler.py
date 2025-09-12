import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram.ext import Application
from services.database import get_subscriptions
from services.horoscope_service import get_horoscope
from telegram import Bot

logger = logging.getLogger(__name__)

async def send_daily_horoscopes(app: Application) -> None:
    """Отправляет ежедневные гороскопы подписанным пользователям."""
    bot = app.bot
    try:
        subscriptions = await get_subscriptions()
        for chat_id, zodiac in subscriptions:
            try:
                horoscope = await get_horoscope(zodiac, "today")
                await bot.send_message(chat_id, f"🌟 Гороскоп для {zodiac} на сегодня:\n{horoscope}")
                logger.debug(f"Гороскоп отправлен пользователю {chat_id} для знака {zodiac}")
            except Exception as e:
                logger.error(f"Ошибка отправки гороскопа пользователю {chat_id}: {e}")
    except Exception as e:
        logger.error(f"Ошибка получения подписок: {e}")

async def schedule_daily_messages(app: Application) -> None:
    """Настраивает ежедневную отправку сообщений."""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_daily_horoscopes,
        trigger=CronTrigger(hour=8, minute=0),
        args=[app],
        misfire_grace_time=300
    )
    scheduler.start()
    logger.info("Планировщик ежедневных сообщений запущен")