from services.database import save_user_preference, get_user_preference

def set_user_profile(user_id: int, name: str, birth_date: str, birth_time: str, birth_place: str):
    """Сохраняет астрологический профиль пользователя."""
    preference = f"{name}|{birth_date}|{birth_time}|{birth_place}"
    save_user_preference(user_id, preference)

def get_user_profile(user_id: int) -> str:
    """Возвращает сохраненный астрологический профиль пользователя."""
    preference = get_user_preference(user_id)
    if preference:
        name, birth_date, birth_time, birth_place = preference.split("|")
        return (
            f"🪐 *Ваш астрологический профиль*\n"
            f"👤 Имя: {name}\n"
            f"📅 Дата рождения: {birth_date}\n"
            f"⏰ Время рождения: {birth_time}\n"
            f"📍 Место рождения: {birth_place}\n"
        )
    return "⚠️ У вас пока нет сохраненного профиля!"
