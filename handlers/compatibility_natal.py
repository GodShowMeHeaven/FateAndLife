from telegram import Update
from telegram.ext import CallbackContext

# Функция для обработки команды /compatibility_natal
async def compatibility_natal(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 8:
        await update.message.reply_text(
            "🔮 Для расчета совместимости по натальной карте введите данные в формате:\n"
            "*/compatibility_natal Имя1 ДД.ММ.ГГГГ ЧЧ:ММ Город1 Имя2 ДД.ММ.ГГГГ ЧЧ:ММ Город2*"
        )
        return

    name1, birth_date1, birth_time1, birth_place1 = context.args[:4]
    name2, birth_date2, birth_time2, birth_place2 = context.args[4:]

    # Заглушка — сюда можно подключить реальный API
    compatibility_text = (
        f"💑 **Совместимость по натальной карте**\n"
        f"👤 {name1} ({birth_date1}, {birth_time1}, {birth_place1})\n"
        f"👤 {name2} ({birth_date2}, {birth_time2}, {birth_place2})\n\n"
        "✨ Ваша астрологическая совместимость высокая! Ваши энергетические поля дополняют друг друга."
    )

    await update.message.reply_text(compatibility_text, parse_mode="Markdown")
