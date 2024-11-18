import os
import json
from dotenv import load_dotenv
from loguru import logger
from yandex_cloud_ml_sdk import YCloudML

# Загрузка переменных окружения
load_dotenv()

# Получение идентификаторов папки и API ключа
FOLDER_ID = os.getenv('YC_FOLDER_ID')
API_KEY = os.getenv('YC_API_KEY')

# Инициализация SDK Yandex Cloud
sdk = YCloudML(folder_id=FOLDER_ID, auth=API_KEY)

def create_assistant():
    """Создает ассистента с заданными параметрами."""
    with open('index_id.json', 'r') as file:
        data = json.load(file)
        index_id = data.get('index_id')
        
    search_index = sdk.search_indexes.get(index_id)
    search_tool = sdk.tools.search_index(search_index, max_num_results=5)
    
    return sdk.assistants.create(
        name="foo-assistant",
        model='yandexgpt',
        temperature=0.1,
        instruction="Вы ассистируете пользователю в Telegram. Отвечайте на вопросы, которые он задает. Игнорируйте контекст, если считаете его нерелевантным.",
        tools=[search_tool],
        ttl_days=30,
        expiration_policy="SINCE_LAST_ACTIVE"
    )

assistant = create_assistant()

async def ai_assistant(message: str, thread_id: str):
    """Отправляет сообщение в указанный поток и получает ответ ассистента."""
    thread = sdk.threads.get(thread_id)
    thread.write(message)
    
    response = assistant.run(thread.id).wait()
    return response.message.parts[0]

async def ai_assistant_new_thread(chat_id: str) -> str:
    """Создает новый поток для чата."""
    thread = sdk.threads.create(
        name=f'thread-{chat_id}',
        ttl_days=7,
        expiration_policy="SINCE_LAST_ACTIVE"
    )
    return thread.id