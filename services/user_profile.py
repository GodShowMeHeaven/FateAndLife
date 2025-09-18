from services.database import save_user_profile as db_save, get_user_profile as db_get  # Corrected import names

async def save_user_profile(chat_id: int, name: str, birth_date: str, birth_time: str, birth_place: str) -> None:
    """Сохраняет астрологический профиль пользователя."""
    await db_save(chat_id, name, birth_date, birth_time, birth_place)

async def get_user_profile(chat_id: int) -> tuple:
    """Возвращает сохраненный астрологический профиль пользователя."""
    profile = await db_get(chat_id)
    if profile:
        name, birth_date, birth_time, birth_place = profile
        return (
            f"🪐 *Ваш астрологический профиль*\n"
            f"👤 Имя: {name}\n"
            f"📅 Дата рождения: {birth_date}\n"
            f"⏰ Время рождения: {birth_time}\n"
            f"📍 Место рождения: {birth_place}\n"
        )
    return "⚠️ У вас пока нет сохраненного профиля!"