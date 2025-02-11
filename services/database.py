import sqlite3

DB_PATH = "bot_data.db"

def init_db():
    """Создает таблицу для подписчиков, если ее нет."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            user_id INTEGER PRIMARY KEY,
            zodiac TEXT,
            subscribed INTEGER DEFAULT 1
        )
    """)
    conn.commit()
    conn.close()

def subscribe_user(user_id: int, zodiac: str):
    """Добавляет пользователя в базу подписчиков."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO subscriptions (user_id, zodiac, subscribed) VALUES (?, ?, 1)", (user_id, zodiac))
    conn.commit()
    conn.close()

def unsubscribe_user(user_id: int):
    """Удаляет пользователя из подписок."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subscriptions WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_subscribed_users():
    """Получает список подписанных пользователей."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, zodiac FROM subscriptions WHERE subscribed = 1")
    users = cursor.fetchall()
    conn.close()
    return users
def init_history_db():
    """Создает таблицу для хранения истории гаданий."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarot_history (
            user_id INTEGER,
            card TEXT,
            interpretation TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_tarot_reading(user_id: int, card: str, interpretation: str):
    """Сохраняет результат гадания в базу данных."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tarot_history (user_id, card, interpretation) VALUES (?, ?, ?)", (user_id, card, interpretation))
    conn.commit()
    conn.close()

def get_tarot_history(user_id: int):
    """Получает последние 5 гаданий пользователя."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT card, interpretation, timestamp FROM tarot_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT 5", (user_id,))
    history = cursor.fetchall()
    conn.close()
    return history
