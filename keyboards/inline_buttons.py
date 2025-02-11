from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Inline-кнопки для Таро
tarot_buttons = [
    [InlineKeyboardButton("🔄 Вытянуть карту", callback_data="draw_tarot")],
    [InlineKeyboardButton("📜 Значение карт", url="https://ru.wikipedia.org/wiki/Таро")]
]
tarot_keyboard = InlineKeyboardMarkup(tarot_buttons)

# Inline-кнопки для гороскопов
horoscope_buttons = [
    [InlineKeyboardButton("♈ Овен", callback_data="horoscope_Овен"),
     InlineKeyboardButton("♉ Телец", callback_data="horoscope_Телец")],
    [InlineKeyboardButton("♊ Близнецы", callback_data="horoscope_Близнецы"),
     InlineKeyboardButton("♋ Рак", callback_data="horoscope_Рак")],
]
horoscope_keyboard = InlineKeyboardMarkup(horoscope_buttons)

# Кнопки для карусели Таро
def tarot_carousel_keyboard():
    buttons = [
        [InlineKeyboardButton("⬅️ Назад", callback_data="prev_tarot"),
         InlineKeyboardButton("🔄 Вытянуть карту", callback_data="draw_tarot"),
         InlineKeyboardButton("➡️ Вперед", callback_data="next_tarot")]
    ]
    return InlineKeyboardMarkup(buttons)
