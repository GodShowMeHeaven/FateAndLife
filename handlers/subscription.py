from telegram import Update
from telegram.ext import CallbackContext
from services.database import subscribe_user, unsubscribe_user

async def subscribe(update: Update, context: CallbackContext) -> None:
    if not context.args:
        await update.message.reply_text("🔮 Введите ваш знак зодиака для подписки: `/subscribe Овен`")
        return

    zodiac = context.args[0].capitalize()
    valid_signs = ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева",
                   "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"]

    if zodiac not in valid_signs:
        await update.message.reply_text("⚠️ Неверный знак зодиака! Введите, например: `/subscribe Лев`")
        return

    subscribe_user(update.message.chat_id, zodiac)
    await update.message.reply_text(f"✅ Вы подписаны на ежедневные гороскопы для {zodiac}!")

async def unsubscribe(update: Update, context: CallbackContext) -> None:
    unsubscribe_user(update.message.chat_id)
    await update.message.reply_text("❌ Вы отписаны от ежедневных гороскопов.")
