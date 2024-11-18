import sqlite3
from loguru import logger
import os

def init_sqlite_db():
    db_path = 'data/tgbot.db'
    
    # Проверяем существование директории и создаем её при необходимости
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    logger.info("Инициализация SQLite базы данных...")
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Создаем таблицы, если они не существуют
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tgbot_chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT UNIQUE NOT NULL,
            thread_id TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tgbot_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            user_nickname TEXT,
            message_text TEXT,
            message_time TEXT
        )
        ''')
        
        conn.commit()
    
    logger.info("База данных SQLite успешно инициализирована")

if __name__ == "__main__":
    init_sqlite_db() 