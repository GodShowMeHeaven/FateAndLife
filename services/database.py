import sqlite3
from contextlib import closing

DB_PATH = "bot_data.db"

def execute_query(query, params=(), fetch=False):
    """Универсальная функция для запросов в SQLite"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.fetchall() if fetch else None

def init_db():
    """Создает таблицу для подписчиков, если ее нет."""
    query = """
    CREATE TABLE IF NOT EXISTS subscriptions (
        user_id INTEGER PRIMARY KEY,
        zodiac TEXT,
        subscribed INTEGER DEFAULT 1
    )
    """
    execute_query(query)

def subscribe_user(user_id: int, zodiac: str):
    """Добавляет пользователя в базу подписчиков."""
    query = "REPLACE INTO subscriptions (user_id, zodiac, subscribed) VALUES (?, ?, 1)"
    execute_query(query, (user_id, zodiac))

def unsubscribe_user(user_id: int):
    """Удаляет пользователя из подписок."""
    query = "DELETE FROM subscriptions WHERE user_id = ?"
    execute_query(query, (user_id,))

def get_subscribed_users():
    """Получает список подписанных пользователей."""
    query = "SELECT user_id, zodiac FROM subscriptions WHERE subscribed = 1"
    return execute_query(query, fetch=True)

def init_history_db():
    """Создает таблицу для хранения истории гаданий."""
    query = """
    CREATE TABLE IF NOT EXISTS tarot_history (
        user_id INTEGER,
        card TEXT,
        interpretation TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
    execute_query(query)

def save_tarot_reading(user_id: int, card: str, interpretation: str):
    """Сохраняет результат гадания в базу данных."""
    query = "INSERT INTO tarot_history (user_id, card, interpretation) VALUES (?, ?, ?)"
    execute_query(query, (user_id, card, interpretation))

def get_tarot_history(user_id: int):
    """Получает последние 5 гаданий пользователя."""
    query = "SELECT card, interpretation, timestamp FROM tarot_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT 5"
    return execute_query(query, (user_id,), fetch=True)

def save_user_preference(user_id: int, preference: str):
    """Сохраняет предпочтения пользователя."""
    query = "REPLACE INTO subscriptions (user_id, zodiac) VALUES (?, ?)"
    execute_query(query, (user_id, preference))

def get_user_preference(user_id: int):
    """Получает предпочтение пользователя."""
    query = "SELECT zodiac FROM subscriptions WHERE user_id = ?"
    result = execute_query(query, (user_id,), fetch=True)
    return result[0][0] if result else None
