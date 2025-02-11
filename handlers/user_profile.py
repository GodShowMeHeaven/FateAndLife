from telegram import Update
from telegram.ext import CallbackContext
from services.user_profile import set_user_profile, get_user_profile

async def set_profile(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 4:
        await update.message.reply_text(
            "📜 *Введите данные для вашего астрологического профиля в формате:*\n"
            "`/set_profile Имя ДД.ММ.ГГГГ ЧЧ:ММ Город`",
            parse_mode="Markdown"
        )
        return

    name, birth_date, birth_time, birth_place = context.args[0], context.args[1], context.args[2], " ".join(context.args[3:])
    set_user_profile(update.message.chat_id, name, birth_date, birth_time, birth_place)

    await update.message.reply_text("✅ Ваш астрологический профиль сохранен!")

async def get_profile(update: Update, context: CallbackContext) -> None:
    profile_text = get_user_profile(update.message.chat_id)
    await update.message.reply_text(profile_text, parse_mode="Markdown")
