from telegram import Update
from telegram.ext import CallbackContext
from services.natal_chart_service import get_natal_chart

async def natal_chart(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 4:
        await update.message.reply_text(
            "📜 *Введите данные для натальной карты в формате:*\n"
            "`/natal_chart Имя ДД.ММ.ГГГГ ЧЧ:ММ Город`",
            parse_mode="Markdown"
        )
        return

    name = context.args[0]
    birth_date = context.args[1]
    birth_time = context.args[2]
    birth_place = " ".join(context.args[3:])  # Поддержка названий с пробелами

    natal_chart_text = get_natal_chart(name, birth_date, birth_time, birth_place)

    formatted_chart = (
        f"🌌 *Анализ натальной карты для {name}*\n"
        "__________________________\n"
        f"{natal_chart_text}\n"
        "__________________________\n"
        "✨ *Совет:* Используйте знания натальной карты для развития!"
    )

    await update.message.reply_text(formatted_chart, parse_mode="Markdown")
