import asyncio
from telegram import Bot
from services.database import get_subscribed_users
from services.horoscope_service import get_horoscope
import config
import logging

bot = Bot(token=config.TELEGRAM_TOKEN)

async def send_daily_horoscope():
    """Рассылает ежедневные гороскопы подписанным пользователям."""
    users = get_subscribed_users()
    for user_id, zodiac in users:
        horoscope = get_horoscope(zodiac, "сегодня")
        try:
            await bot.send_message(user_id, f"🔮 *Ваш ежедневный гороскоп для {zodiac}*:\n\n{horoscope}", parse_mode="Markdown")
        except Exception as e:
            print(f"Ошибка при отправке пользователю {user_id}: {e}")

async def schedule_daily_messages():
    while True:
        try:
            await send_daily_horoscope()
        except Exception as e:
            logging.error(f"Ошибка в ежедневной рассылке: {e}")
        await asyncio.sleep(86400)  # 24 часа
