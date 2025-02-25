from telegram import Update
from telegram.ext import CallbackContext

# Функция для обработки команды /compatibility_fio
async def compatibility_fio(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 6:
        await update.message.reply_text(
            "🔠 Для расчета совместимости по ФИО и дате рождения введите данные в формате:\n"
            "*/compatibility_fio Имя1 Фамилия1 ДД.ММ.ГГГГ Имя2 Фамилия2 ДД.ММ.ГГГГ*"
        )
        return

    name1, surname1, birth_date1 = context.args[:3]
    name2, surname2, birth_date2 = context.args[3:]

    # Простой алгоритм расчета совместимости на основе чисел судьбы 
    compatibility_score = (sum(map(ord, name1 + surname1)) + sum(map(ord, name2 + surname2))) % 100

    compatibility_text = (
        f"🔢 **Совместимость по ФИО и дате рождения**\n"
        f"👤 {name1} {surname1} ({birth_date1})\n"
        f"👤 {name2} {surname2} ({birth_date2})\n\n"
        f"💞 Ваш уровень совместимости: *{compatibility_score}%*\n"
        "✨ Чем выше процент, тем лучше духовное и энергетическое соответствие!"
    )

    await update.message.reply_text(compatibility_text, parse_mode="Markdown")
