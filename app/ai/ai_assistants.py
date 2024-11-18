import os
import json
from dotenv import load_dotenv
from loguru import logger
from yandex_cloud_ml_sdk import YCloudML

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение идентификаторов папки и API ключа из переменных окружения
FOLDER_ID = os.getenv('YC_FOLDER_ID')
API_KEY = os.getenv('YC_API_KEY')

# Инициализация SDK Yandex Cloud с использованием полученных идентификаторов
sdk = YCloudML(folder_id=FOLDER_ID, auth=API_KEY)

def create_assistant():
    """Создает ассистента с заданными параметрами."""
    # Открываем файл index_id.json для получения идентификатора индекса
    with open('index_id.json', 'r') as file:
        data = json.load(file)
        index_id = data.get('index_id')  # Извлекаем index_id из данных
        
    # Получаем индекс поиска по его идентификатору
    search_index = sdk.search_indexes.get(index_id)
    # Создаем инструмент поиска с максимальным количеством результатов 5
    search_tool = sdk.tools.search_index(search_index, max_num_results=5)
    
    # Создаем ассистента с заданными параметрами
    return sdk.assistants.create(
        name="foo-assistant",  # Имя ассистента
        model='yandexgpt',  # Модель, которую будет использовать ассистент
        temperature=0.1,  # Параметр, определяющий креативность ответов
        instruction="Вы ассистируете пользователю в Telegram. Отвечайте на вопросы, которые он задает. Игнорируйте контекст, если считаете его нерелевантным.",  # Инструкция для ассистента
        tools=[search_tool],  # Инструменты, которые будет использовать ассистент
        ttl_days=30,  # Время жизни ассистента в днях
        expiration_policy="SINCE_LAST_ACTIVE"  # Политика истечения
    )

# Создаем ассистента и сохраняем его в переменной
assistant = create_assistant()

async def ai_assistant(message: str, thread_id: str):
    """Отправляет сообщение в указанный поток и получает ответ ассистента."""
    # Получаем поток по его идентификатору
    thread = sdk.threads.get(thread_id)
    # Записываем сообщение в поток
    thread.write(message)
    
    # Запускаем ассистента и ждем ответа
    response = assistant.run(thread.id).wait()
    return response.message.parts[0]  # Возвращаем первый элемент ответа

async def ai_assistant_new_thread(chat_id: str) -> str:
    """Создает новый поток для чата."""
    # Создаем новый поток с заданным именем и временем жизни 7 дней
    thread = sdk.threads.create(
        name=f'thread-{chat_id}',  # Имя потока, основанное на идентификаторе чата
        ttl_days=7,  # Время жизни потока в днях
        expiration_policy="SINCE_LAST_ACTIVE"  # Политика истечения
    )
    return thread.id  # Возвращаем идентификатор нового потока