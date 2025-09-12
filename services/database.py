# Убедитесь, что aiosqlite установлен: `pip install aiosqlite`
import aiosqlite
import logging
import config

logger = logging.getLogger(__name__)

async def init_db() -> None:
    """Инициализирует базу данных."""
    try:
        async with aiosqlite.connect(config.DB_PATH) as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS subscriptions (
                    chat_id INTEGER PRIMARY KEY,
                    zodiac TEXT NOT NULL
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS profiles (
                    chat_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    birth_date TEXT NOT NULL,
                    birth_time TEXT NOT NULL
                )
            ''')
            await conn.commit()
            logger.info("База данных инициализирована")
    except Exception as e:
        logger.error(f"Ошибка инициализации базы данных: {e}")
        raise

async def add_subscription(chat_id: int, zodiac: str) -> None:
    """Добавляет подписку пользователя."""
    try:
        async with aiosqlite.connect(config.DB_PATH) as conn:
            await conn.execute(
                "INSERT OR REPLACE INTO subscriptions (chat_id, zodiac) VALUES (?, ?)",
                (chat_id, zodiac)
            )
            await conn.commit()
            logger.debug(f"Подписка добавлена: {chat_id}, {zodiac}")
    except Exception as e:
        logger.error(f"Ошибка добавления подписки: {e}")
        raise

async def remove_subscription(chat_id: int) -> None:
    """Удаляет подписку пользователя."""
    try:
        async with aiosqlite.connect(config.DB_PATH) as conn:
            await conn.execute("DELETE FROM subscriptions WHERE chat_id = ?", (chat_id,))
            await conn.commit()
            logger.debug(f"Подписка удалена: {chat_id}")
    except Exception as e:
        logger.error(f"Ошибка удаления подписки: {e}")
        raise

async def get_subscriptions() -> list:
    """Возвращает список всех подписок."""
    try:
        async with aiosqlite.connect(config.DB_PATH) as conn:
            cursor = await conn.execute("SELECT chat_id, zodiac FROM subscriptions")
            return await cursor.fetchall()
    except Exception as e:
        logger.error(f"Ошибка получения подписок: {e}")
        raise

async def save_user_profile(chat_id: int, name: str, birth_date: str, birth_time: str) -> None:
    """Сохраняет профиль пользователя."""
    try:
        async with aiosqlite.connect(config.DB_PATH) as conn:
            await conn.execute(
                "INSERT OR REPLACE INTO profiles (chat_id, name, birth_date, birth_time) VALUES (?, ?, ?, ?)",
                (chat_id, name, birth_date, birth_time)
            )
            await conn.commit()
            logger.debug(f"Профиль сохранен: {chat_id}, {name}")
    except Exception as e:
        logger.error(f"Ошибка сохранения профиля: {e}")
        raise

async def get_user_profile(chat_id: int) -> tuple:
    """Возвращает профиль пользователя."""
    try:
        async with aiosqlite.connect(config.DB_PATH) as conn:
            cursor = await conn.execute("SELECT name, birth_date, birth_time FROM profiles WHERE chat_id = ?", (chat_id,))
            return await cursor.fetchone()
    except Exception as e:
        logger.error(f"Ошибка получения профиля: {e}")
        raise