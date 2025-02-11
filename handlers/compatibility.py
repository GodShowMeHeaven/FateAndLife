from telegram import Update
from telegram.ext import CallbackContext
from services.compatibility_service import get_zodiac_compatibility, get_natal_compatibility

async def compatibility(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 2:
        await update.message.reply_text(
            "💑 *Введите знаки зодиака для проверки совместимости:*\n"
            "`/compatibility Овен Телец`",
            parse_mode="Markdown"
        )
        return

    sign1, sign2 = context.args[0].capitalize(), context.args[1].capitalize()
    compatibility_text = get_zodiac_compatibility(sign1, sign2)

    formatted_text = (
        f"💞 *Совместимость {sign1} и {sign2}*\n"
        "__________________________\n"
        f"{compatibility_text}\n"
        "__________________________\n"
        "💡 *Совет:* Используйте знание зодиака для гармонии!"
    )

    await update.message.reply_text(formatted_text, parse_mode="Markdown")

async def compatibility_natal(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 8:
        await update.message.reply_text(
            "🌌 *Введите данные для совместимости по натальной карте:*\n"
            "`/compatibility_natal Имя1 ДД.ММ.ГГГГ ЧЧ:ММ Город1 Имя2 ДД.ММ.ГГГГ ЧЧ:ММ Город2`",
            parse_mode="Markdown"
        )
        return

    name1, birth1, time1, place1 = context.args[:4]
    name2, birth2, time2, place2 = context.args[4:]

    compatibility_text = get_natal_compatibility(name1, birth1, time1, place1, name2, birth2, time2, place2)

    formatted_text = (
        f"🔮 *Астрологическая совместимость {name1} и {name2}*\n"
        "__________________________\n"
        f"{compatibility_text}\n"
        "__________________________\n"
        "✨ *Совет:* Используйте астрологию для гармонии в паре!"
    )

    await update.message.reply_text(formatted_text, parse_mode="Markdown")
