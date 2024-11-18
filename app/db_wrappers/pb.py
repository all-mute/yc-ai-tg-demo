from loguru import logger
import pocketbase
import dotenv, os

logger.warning("Используется pocketbase!")

dotenv.load_dotenv()

PB_URL = os.getenv("PB_URL")
PB_ADMIN_EMAIL = os.getenv("PB_ADMIN_EMAIL")
PB_ADMIN_PASSWORD = os.getenv("PB_ADMIN_PASSWORD")
PB_CHATS_TABLENAME = os.getenv("PB_CHATS_TABLENAME")
PB_CHATS_TABLEID = os.getenv("PB_CHATS_TABLEID")
PB_LOGS_TABLENAME = os.getenv("PB_LOGS_TABLENAME")
PB_LOGS_TABLEID = os.getenv("PB_LOGS_TABLEID")
PB_SNIPPETS_TABLENAME = os.getenv("PB_SNIPPETS_TABLENAME")
PB_SNIPPETS_TABLEID = os.getenv("PB_SNIPPETS_TABLEID")
PB_SNIFFER_LOGS_TABLENAME = os.getenv("PB_SNIFFER_LOGS_TABLENAME")
PB_SNIFFER_LOGS_TABLEID = os.getenv("PB_SNIFFER_LOGS_TABLEID")

logger.debug(f"Инициализация PocketBase с URL: {PB_URL}")
pb = pocketbase.PocketBase(PB_URL)
logger.debug(f"Аутентификация администратора с email: {PB_ADMIN_EMAIL}")
pb.admins.auth_with_password(PB_ADMIN_EMAIL, PB_ADMIN_PASSWORD)

def init_commands_and_snippets() -> tuple[dict, dict]:
    logger.debug(f"Получение полного списка сниппетов из таблицы: {PB_SNIPPETS_TABLENAME}")
    table_res = pb.collection(PB_SNIPPETS_TABLENAME).get_full_list()
    
    commands = {item.name: item.snippet_text for item in table_res if item.is_command}
    snippets = {item.name: item.snippet_text for item in table_res if not item.is_command}
    
    logger.debug(f"Команды и сниппеты инициализированы: {commands}")
    return commands, snippets

def get_all_chats() -> list[str]:
    logger.debug(f"Получение всех чатов из таблицы: {PB_CHATS_TABLENAME}")
    table_res = pb.collection(PB_CHATS_TABLENAME).get_full_list()
    chat_ids = [item.group_id for item in table_res]
    logger.debug(f"Полученные ID чатов: {chat_ids}")
    return chat_ids

def create_group_chat_id(chat_id: str):
    logger.debug(f"Создание группы чата с ID: {chat_id}")
    pb.collection(PB_CHATS_TABLENAME).create({"group_id": chat_id})

def remove_group_chat_id(chat_id: str):
    logger.debug(f"Удаление группы чата с ID: {chat_id}")
    res = pb.collection(PB_CHATS_TABLENAME).get_first_list_item(filter = f"group_id = '{chat_id}'")
    if res:
        logger.debug(f"Удаление чата с ID: {res.id}")
        pb.collection(PB_CHATS_TABLENAME).delete(res.id)

def create_log(chat_id: str, logs: dict):
    logger.debug(f"Создание лога для чата с ID: {chat_id}")
    res = pb.collection(PB_LOGS_TABLENAME).create({"group_id": chat_id, "logs": logs})
    logger.debug(f"Лог создан: {res.__dict__}")

def get_snippet_by_name(name: str) -> str:
    logger.debug(f"Получение сниппета с названием: {name}")
    table_res = pb.collection(PB_SNIPPETS_TABLENAME).get_first_list_item(filter = f"name = '{name}'")
    return table_res.snippet_text if table_res else "Сниппет не найден"

def create_sniffer_log(
        chat_id,
        chat_title,
        chat_username,
        user_id,
        user_nickname,
        message_id,
        date,
        chat_type,
        message_text
    ):
    logger.debug(f"Создание лога для чата с ID: {chat_id}")
    res = pb.collection(PB_SNIFFER_LOGS_TABLENAME).create(
        {
            "chat_id": chat_id,
            "chat_title": chat_title,
            "chat_username": chat_username,
            "user_id": user_id,
            "user_nickname": user_nickname,
            "message_id": message_id,
            "date": date,
            "chat_type": chat_type,
            "message_text": message_text
        }
    )
    logger.debug(f"Лог создан: {res.__dict__}")