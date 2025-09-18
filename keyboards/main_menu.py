from telegram import ReplyKeyboardMarkup

# Кнопки главного меню
##main_menu_buttons = [
    ##["🔮 Гороскоп", "🌌 Натальная карта"],
    ##["🔢 Нумерология", "🎴 Карты Таро"],
    ##["🔮 Предсказания", "📜 Послание на день"]
##]

# Кнопки главного меню
main_menu_buttons = [
    ["🔮 Гороскоп", "🎴 Карты Таро"],
    ["🔮 Предсказания", "📜 Послание на день"]
]
main_menu_keyboard = ReplyKeyboardMarkup(main_menu_buttons, resize_keyboard=True)

# Вложенное меню предсказаний
predictions_buttons = [
    ["💰 На деньги", "🍀 На удачу"],
    ["💞 На отношения", "🩺 На здоровье"],
    ["🔙 Вернуться в меню"]  # ✅ Кнопка возврата
]

predictions_keyboard = ReplyKeyboardMarkup(predictions_buttons, resize_keyboard=True)
