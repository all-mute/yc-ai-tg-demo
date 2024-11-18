import requests
import os
import dotenv
from loguru import logger

dotenv.load_dotenv()

SEARCH_API_GENERATIVE = f"https://ya.ru/search/xml/generative?folderid={os.getenv('FOLDER_ID')}"

async def search_api_generative(message: str):
    headers = {"Authorization": f"Api-Key {os.getenv('YANDEX_API_KEY')}"}
    data = {
        "messages": [
           {
                "content": message,
                "role": "user"
            }
        ],
        "site": "https://yandex.cloud/ru/docs",
        #"host": "yandex.cloud/ru/docs"
        #"url": "https://yandex.cloud/ru/docs/foundation-models/pricing"
    }

    response = requests.post(SEARCH_API_GENERATIVE, headers=headers, json=data)

    content = ""
    sources = []
    if "application/json" in response.headers["Content-Type"]:
        content = response.json()["message"]["content"]
        sources = response.json().get("links", [])
        logger.info(content)
        for i, link in enumerate(sources, start=1):
            logger.info(f"[{i}]: {link}")
    elif "text/xml" in response.headers["Content-Type"]:
        logger.error(f"Error: {response.text}")
    else:
        logger.error(f"Unexpected content type: {response.text}")

    combined_content = f"Ответ SearchAPI:\n{content}\n\nИсточники:\n" + "\n".join(sources)
    return combined_content
