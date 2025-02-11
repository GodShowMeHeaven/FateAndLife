from telegram import ReplyKeyboardMarkup

# Кнопки главного меню
main_menu_buttons = [
    ["🔮 Гороскоп", "🌌 Натальная карта"],
    ["🔢 Нумерология", "🎴 Карты Таро"],
    ["❤️ Совместимость", "📜 Послание на день"],
    ["💰 Предсказание на деньги", "🍀 Предсказание на удачу"],
    ["💞 Предсказание на отношения", "🩺 Предсказание на здоровье"]
]

main_menu_keyboard = ReplyKeyboardMarkup(
    main_menu_buttons,
    resize_keyboard=True,
    one_time_keyboard=False,  # Оставляем клавиатуру активной
    input_field_placeholder="Выберите категорию:"
)
