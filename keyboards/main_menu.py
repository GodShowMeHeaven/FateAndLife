from telegram import ReplyKeyboardMarkup

# Кнопки главного меню
main_menu_buttons = [
    ["🔮 Гороскоп", "🌌 Натальная карта"],
    ["🔢 Нумерология", "🎴 Карты Таро"],
    ["❤️ Совместимость", "📜 Послание на день"],
    ["🔮 Предсказания"],  # ✅ Группируем предсказания в одну кнопку
]

main_menu_keyboard = ReplyKeyboardMarkup(main_menu_buttons, resize_keyboard=True)

# Вложенное меню предсказаний
predictions_buttons = [
    ["💰 На деньги", "🍀 На удачу"],
    ["💞 На отношения", "🩺 На здоровье"],
    ["🔙 Вернуться в меню"]  # ✅ Кнопка возврата
]

predictions_keyboard = ReplyKeyboardMarkup(predictions_buttons, resize_keyboard=True)
