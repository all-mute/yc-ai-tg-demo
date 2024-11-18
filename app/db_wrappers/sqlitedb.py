from loguru import logger
import sqlite3
from typing import List, Optional

logger.warning("Используется sqlitedb!")

DB_PATH = 'data/tgbot.db'

def dict_factory(cursor, row):
    """Создает словарь из строки результата запроса."""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

def get_connection() -> sqlite3.Connection:
    """Устанавливает соединение с базой данных SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    return conn

def get_all_chats() -> List[str]:
    """Получает все chat_id из базы данных."""
    logger.debug("Получение всех чатов из SQLite")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT chat_id FROM tgbot_chats')
        chat_ids = [item['chat_id'] for item in cursor.fetchall()]
    logger.debug(f"Полученные ID чатов: {chat_ids}")
    return chat_ids

def chat_exists(chat_id: str) -> bool:
    """Проверяет существование чата по chat_id."""
    logger.debug(f"Проверка существования чата с ID: {chat_id}")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM tgbot_chats WHERE chat_id = ?', (chat_id,))
        exists = cursor.fetchone() is not None
    return exists

def get_thread_id(chat_id: str) -> Optional[str]:
    """Получает thread_id для указанного chat_id."""
    logger.debug(f"Получение thread_id для чата с ID: {chat_id}")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT thread_id FROM tgbot_chats WHERE chat_id = ?', (chat_id,))
        result = cursor.fetchone()
    return result['thread_id'] if result else None

def set_thread_id(chat_id: str, thread_id: str):
    """Устанавливает thread_id для указанного chat_id."""
    logger.debug(f"Установка thread_id для чата с ID: {chat_id}")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE tgbot_chats SET thread_id = ? WHERE chat_id = ?', (thread_id, chat_id))

def create_chat_and_thread(chat_id: str, thread_id: str):
    """Создает новый чат с указанным chat_id и thread_id."""
    logger.debug(f"Создание чата и thread_id для чата с ID: {chat_id}")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO tgbot_chats (chat_id, thread_id) VALUES (?, ?)', (chat_id, thread_id))

def create_log(chat_id: str, user_nickname: str, message_text: str, message_time: str):
    """Создает лог для указанного чата."""
    logger.debug(f"Создание лога для чата с ID: {chat_id}")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO tgbot_logs (chat_id, user_nickname, message_text, message_time) VALUES (?, ?, ?, ?)',
            (chat_id, user_nickname, message_text, message_time)
        )
