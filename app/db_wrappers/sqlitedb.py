from loguru import logger
import sqlite3
import json

logger.warning("Используется sqlitedb!")

DB_PATH = 'data/tgbot.db'

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    return conn

def init_commands_and_snippets() -> tuple[dict, dict]:
    logger.debug("Получение полного списка сниппетов из SQLite")
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM tgbot_snippets')
    items = cursor.fetchall()
    
    commands = {item['name']: item['snippet_text'] for item in items if item['is_command']}
    snippets = {item['name']: item['snippet_text'] for item in items if not item['is_command']}
    
    conn.close()
    logger.debug(f"Команды и сниппеты инициализированы: {commands}")
    return commands, snippets

def get_all_chats() -> list[str]:
    logger.debug("Получение всех чатов из SQLite")
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT group_id FROM tgbot_chats')
    chat_ids = [item['group_id'] for item in cursor.fetchall()]
    
    conn.close()
    logger.debug(f"Полученные ID чатов: {chat_ids}")
    return chat_ids

def chat_exists(chat_id: str) -> bool:
    logger.debug(f"Проверка существования чата с ID: {chat_id}")
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT 1 FROM tgbot_chats WHERE group_id = ?', (chat_id,))
    exists = cursor.fetchone() is not None
    
    conn.close()
    return exists

def create_group_chat_id(chat_id: str):
    if chat_exists(chat_id):
        logger.warning(f"Чат с ID {chat_id} уже существует")
        return False
        
    logger.debug(f"Создание группы чата с ID: {chat_id}")
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('INSERT INTO tgbot_chats (group_id) VALUES (?)', (chat_id,))
    
    conn.commit()
    conn.close()
    return True

def remove_group_chat_id(chat_id: str):
    logger.debug(f"Удаление группы чата с ID: {chat_id}")
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM tgbot_chats WHERE group_id = ?', (chat_id,))
    
    conn.commit()
    conn.close()

def create_log(chat_id: str, logs: dict):
    logger.debug(f"Создание лога для чата с ID: {chat_id}")
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO tgbot_logs (group_id, logs) VALUES (?, ?)',
        (chat_id, json.dumps(logs))
    )
    
    conn.commit()
    conn.close()

def get_snippet_by_name(name: str) -> str:
    logger.debug(f"Получение сниппета с названием: {name}")
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT snippet_text FROM tgbot_snippets WHERE name = ?', (name,))
    result = cursor.fetchone()
    
    conn.close()
    return result['snippet_text'] if result else "Сниппет не найден"

def create_sniffer_log(
    chat_id: str,
    chat_title: str,
    chat_username: str,
    user_id: str,
    user_nickname: str,
    message_id: str,
    date: str,
    chat_type: str,
    message_text: str
):
    logger.debug(f"Создание снифер-лога для чата с ID: {chat_id}")
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO tgbot_sniffer_logs (chat_id, chat_title, chat_username, user_id, user_nickname, message_id, date, chat_type, message_text) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (chat_id, chat_title, chat_username, user_id, user_nickname, message_id, date, chat_type, message_text)
    )
    
    conn.commit()
    conn.close()