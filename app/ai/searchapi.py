import os
import requests
import dotenv
from loguru import logger
from yandex_cloud_ml_sdk import YCloudML

# Загрузка переменных окружения
dotenv.load_dotenv()

# Получение идентификаторов папки и API ключа
FOLDER_ID = os.getenv('YC_FOLDER_ID')
API_KEY = os.getenv('YC_API_KEY')

# URL для генеративного поиска
SEARCH_API_GENERATIVE = f"https://ya.ru/search/xml/generative?folderid={FOLDER_ID}"
SERP_SITE = os.getenv('SERP_SITE', None)
SERP_HOST = os.getenv('SERP_HOST', None)
SERP_URL = os.getenv('SERP_URL', None)

# Инициализация SDK Yandex Cloud
sdk = YCloudML(folder_id=FOLDER_ID, auth=API_KEY)

def process_response(response):
    """Обрабатывает ответ от API и возвращает комбинированный контент."""
    content = ""
    sources = []

    if "application/json" in response.headers.get("Content-Type", ""):
        content = response.json().get("message", {}).get("content", "")
        sources = response.json().get("links", [])
        logger.info(content)
        for i, link in enumerate(sources, start=1):
            logger.info(f"[{i}]: {link}")
    elif "text/xml" in response.headers.get("Content-Type", ""):
        logger.error(f"Ошибка: {response.text}")
    else:
        logger.error(f"Неожиданный тип контента: {response.text}")

    combined_content = f"Ответ SearchAPI:\n{content}\n\nИсточники:\n" + "\n".join(sources)
    return combined_content

async def search_api_generative_contextual(message: str, thread_id: str):
    """Выполняет генеративный поиск с учетом контекста треда."""
    thread_messages = sdk.threads.get(thread_id).read()
    messages = [{"content": item.parts[0], "role": item.role} for item in thread_messages]
    
    messages.append({"content": message, "role": "user"})
    
    headers = {"Authorization": f"Api-Key {API_KEY}"}
    data = {
        "messages": messages,
        "site": SERP_SITE,
        "host": SERP_HOST,
        "url": SERP_URL
    }

    response = requests.post(SEARCH_API_GENERATIVE, headers=headers, json=data)
    combined_content = process_response(response)
    
    thread = sdk.threads.get(thread_id)
    thread.write(message)
    thread.write(combined_content, labels={"role": "assistant"})
    return combined_content

async def search_api_generative(message: str):
    """Выполняет генеративный поиск без контекста треда."""
    headers = {"Authorization": f"Api-Key {API_KEY}"}
    data = {
        "messages": [{"content": message, "role": "user"}],
        "site": SERP_SITE,
        "host": SERP_HOST,
        "url": SERP_URL
    }

    response = requests.post(SEARCH_API_GENERATIVE, headers=headers, json=data)
    combined_content = process_response(response)
    
    return combined_content