from loguru import logger
import dotenv, os

dotenv.load_dotenv()

import json

logger.warning("Используется jsondb!")

# В начало файла после импортов
DATA_FILE = 'data/data.json'

# Загрузка данных из JSON файла
def load_data(filename: str):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"Файл {filename} не найден")
        raise
    except json.JSONDecodeError:
        logger.error(f"Ошибка декодирования JSON в файле {filename}")
        raise

def init_commands_and_snippets() -> tuple[dict, dict]:
    logger.debug(f"Получение полного списка сниппетов из файла: {DATA_FILE}")
    data = load_data(DATA_FILE)
    
    commands = {item['name']: item['snippet_text'] for item in data['tgbot_snippets'] if item['is_command']}
    snippets = {item['name']: item['snippet_text'] for item in data['tgbot_snippets'] if not item['is_command']}
    
    logger.debug(f"Команды и сниппеты инициализированы: {commands}")
    return commands, snippets

def get_all_chats() -> list[str]:
    logger.debug(f"Получение всех чатов из файла: {DATA_FILE}")
    data = load_data(DATA_FILE)
    chat_ids = [item['group_id'] for item in data['tgbot_chats']]
    logger.debug(f"Полученные ID чатов: {chat_ids}")
    return chat_ids

def chat_exists(chat_id: str) -> bool:
    logger.debug(f"Проверка существования чата с ID: {chat_id}")
    data = load_data(DATA_FILE)
    return any(item['group_id'] == chat_id for item in data['tgbot_chats'])

def create_group_chat_id(chat_id: str):
    if chat_exists(chat_id):
        logger.warning(f"Чат с ID {chat_id} уже существует")
        return False
    logger.debug(f"Создание группы чата с ID: {chat_id}")
    data = load_data(DATA_FILE)
    data['tgbot_chats'].append({"group_id": chat_id})
    save_data(DATA_FILE, data)
    return True

def remove_group_chat_id(chat_id: str):
    logger.debug(f"Удаление группы чата с ID: {chat_id}")
    data = load_data(DATA_FILE)
    data['tgbot_chats'] = [item for item in data['tgbot_chats'] if item['group_id'] != chat_id]
    save_data(DATA_FILE, data)  # Сохранение изменений в файл

def create_log(chat_id: str, logs: dict):
    logger.debug(f"Создание лога для чата с ID: {chat_id}")
    data = load_data(DATA_FILE)
    data['tgbot_logs'].append({"group_id": chat_id, "logs": logs})
    save_data(DATA_FILE, data)  # Сохранение изменений в файл

def get_snippet_by_name(name: str) -> str:
    logger.debug(f"Получение сниппета с названием: {name}")
    data = load_data(DATA_FILE)
    snippet = next((item['snippet_text'] for item in data['tgbot_snippets'] if item['name'] == name), None)
    if snippet is None:
        logger.warning(f"Сниппет с названием {name} не найден")
        return "Сниппет не найден"
    return snippet

def save_data(filename: str, data):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except IOError:
        logger.error(f"Ошибка при сохранении данных в файл {filename}")
        raise

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
    data = load_data(DATA_FILE)
    data['tgbot_sniffer_logs'].append({
        "chat_id": chat_id,
        "chat_title": chat_title,
        "chat_username": chat_username,
        "user_id": user_id,
        "user_nickname": user_nickname,
        "message_id": message_id,
        "date": date,
        "chat_type": chat_type,
        "message_text": message_text
    })
    save_data(DATA_FILE, data)
