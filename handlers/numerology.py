from telegram import Update
from telegram.ext import CallbackContext

# Функция для обработки команды /numerology
async def numerology(update: Update, context: CallbackContext) -> None:
    if not context.args:
        await update.message.reply_text(
            "🔢 Введите вашу дату рождения в формате:\n"
            "*/numerology ДД.ММ.ГГГГ*"
        )
        return

    birth_date = context.args[0]

    # Проверяем правильность формата даты
    try:
        day, month, year = map(int, birth_date.split("."))
        life_path_number = (sum(map(int, str(day))) +
                            sum(map(int, str(month))) +
                            sum(map(int, str(year))))

        while life_path_number >= 10:  # Считаем до однозначного числа
            life_path_number = sum(map(int, str(life_path_number)))

    except ValueError:
        await update.message.reply_text("⚠️ Неверный формат! Введите дату в формате ДД.ММ.ГГГГ, например: `/numerology 12.05.1990`")
        return

    # Заглушка — сюда можно добавить расшифровку чисел
    numerology_text = f"🔢 **Ваше число судьбы: {life_path_number}**\n\n" \
                      f"✨ Это число символизирует вашу основную жизненную энергию."

    await update.message.reply_text(numerology_text, parse_mode="Markdown")
