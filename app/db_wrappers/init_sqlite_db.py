import sqlite3
from loguru import logger
import os

def init_sqlite_db():
    db_path = 'data/tgbot.db'
    db_exists = os.path.exists(db_path)
    
    # Проверяем существование директории
    os.makedirs('data', exist_ok=True)
    
    logger.info("Инициализация SQLite базы данных...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Создаем таблицы
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tgbot_chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id TEXT UNIQUE
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tgbot_snippets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        snippet_text TEXT,
        is_command BOOLEAN
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tgbot_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id TEXT,
        logs TEXT
    )
    ''')
    
    # Добавляем таблицу для снифер-логов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tgbot_sniffer_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id TEXT,
        chat_title TEXT,
        chat_username TEXT,
        user_id TEXT,
        user_nickname TEXT,
        message_id TEXT,
        date TEXT,
        chat_type TEXT,
        message_text TEXT
    )
    ''')
    
    # Добавляем начальные данные только если база данных новая
    if not db_exists:
        default_snippets = [
            (True, "start", "Добро пожаловать в бота\!\n\n**Доступные команды**:\n• /add\_chat\n• /remove\_chat\n• /all\_guides\n• /send\_news\n• /sync\_pb"),
            (True, "add_chat", "Чат успешно добавлен"),
            (True, "remove_chat", "Чат успешно удален\!"),
            (True, "all_guides", "Вот все **доступные сниппеты**"),
            (True, "send_news", "Новости успешно отправлены"),
            (True, "sync_pb", "Команды и сниппеты успешно синхронизированы"),
            (False, "snippet1_name", "snippet1\_text")
        ]
        
        cursor.executemany(
            'INSERT OR IGNORE INTO tgbot_snippets (is_command, name, snippet_text) VALUES (?, ?, ?)',
            default_snippets
        )
        logger.info("Добавлены стандартные сниппеты")
    
    conn.commit()
    conn.close()
    logger.info("База данных SQLite успешно инициализирована")

if __name__ == "__main__":
    init_sqlite_db() 