from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Inline-кнопки для Таро
tarot_buttons = [
    [InlineKeyboardButton("🔄 Вытянуть карту", callback_data="draw_tarot")],
    [InlineKeyboardButton("📜 Значение карт", url="https://ru.wikipedia.org/wiki/Таро")]
]
tarot_keyboard = InlineKeyboardMarkup(tarot_buttons)

# Inline-кнопки для гороскопов (добавлены все знаки)
horoscope_buttons = [
    [InlineKeyboardButton("♈ Овен", callback_data="horoscope_Овен"),
     InlineKeyboardButton("♉ Телец", callback_data="horoscope_Телец"),
     InlineKeyboardButton("♊ Близнецы", callback_data="horoscope_Близнецы")],
    
    [InlineKeyboardButton("♋ Рак", callback_data="horoscope_Рак"),
     InlineKeyboardButton("♌ Лев", callback_data="horoscope_Лев"),
     InlineKeyboardButton("♍ Дева", callback_data="horoscope_Дева")],

    [InlineKeyboardButton("♎ Весы", callback_data="horoscope_Весы"),
     InlineKeyboardButton("♏ Скорпион", callback_data="horoscope_Скорпион"),
     InlineKeyboardButton("♐ Стрелец", callback_data="horoscope_Стрелец")],

    [InlineKeyboardButton("♑ Козерог", callback_data="horoscope_Козерог"),
     InlineKeyboardButton("♒ Водолей", callback_data="horoscope_Водолей"),
     InlineKeyboardButton("♓ Рыбы", callback_data="horoscope_Рыбы")]
]
horoscope_keyboard = InlineKeyboardMarkup(horoscope_buttons)

# Кнопки для карусели Таро
def create_carousel_keyboard(buttons, prev_callback, next_callback):
    buttons.append([
        InlineKeyboardButton("⬅️ Назад", callback_data=prev_callback),
        InlineKeyboardButton("➡️ Вперед", callback_data=next_callback)
    ])
    return InlineKeyboardMarkup(buttons)

# Карусель Таро
tarot_carousel_keyboard = create_carousel_keyboard([
    [InlineKeyboardButton("🔄 Вытянуть карту", callback_data="draw_tarot")]
], "prev_tarot", "next_tarot")
