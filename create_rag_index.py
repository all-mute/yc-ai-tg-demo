import os
import json
from dotenv import load_dotenv
from loguru import logger
from yandex_cloud_ml_sdk import YCloudML
from yandex_cloud_ml_sdk.search_indexes import VectorSearchIndexType, StaticIndexChunkingStrategy

# Загрузка переменных окружения
load_dotenv('/home/asuka0/tgbot_ai_serp/yc-ai-tg-demo/.env')

# Получение идентификатора папки и API ключа из переменных окружения
FOLDER_ID = os.getenv("YC_FOLDER_ID")
YANDEX_API_KEY = os.getenv("YC_API_KEY")
DATA_DIR = os.getenv("DATA_DIR")

# Инициализация SDK с авторизацией
sdk = YCloudML(folder_id=FOLDER_ID, auth=YANDEX_API_KEY)

# Путь к директории с данными
current_dir = os.path.dirname(os.path.abspath(__file__))
data_directory = os.path.join(current_dir, "knowledge", DATA_DIR)

# Проверка наличия файлов в директории
files = os.listdir(data_directory)
if not files:
    logger.error(f"Директория {data_directory} пуста")
    raise FileNotFoundError(f"В директории {data_directory} нет файлов")

# Список для хранения ссылок на загруженные файлы
uploaded_files = []

# Загрузка всех файлов из директории данных
for filename in os.listdir(data_directory):
    file_path = os.path.join(data_directory, filename)
    if os.path.isfile(file_path):
        uploaded_file = sdk.files.upload(
            file_path,
            name=filename,
            description=f"Данные базы знаний из {data_directory}",
            ttl_days=30,
            expiration_policy="SINCE_LAST_ACTIVE"
        )
        uploaded_files.append(uploaded_file)

# Создание типа векторного поискового индекса
index_type = VectorSearchIndexType(
    chunking_strategy=StaticIndexChunkingStrategy(
        max_chunk_size_tokens=1000,
        chunk_overlap_tokens=200
    ),
    doc_embedder_uri=f"emb://{FOLDER_ID}/text-search-doc/rc",
    query_embedder_uri=f"emb://{FOLDER_ID}/text-search-query/rc"
)

# Создание поискового индекса с загруженными файлами
operation = sdk.search_indexes.create_deferred(
    files=uploaded_files,
    index_type=index_type,
    name="rag_search_index",
    description=f"Данные базы знаний из {data_directory}",
    ttl_days=30,
    expiration_policy="SINCE_LAST_ACTIVE"
)

# Ожидание завершения создания поискового индекса
index = operation.wait()

# Сохранение идентификатора индекса в JSON файл
index_id = {"index_id": index.id}
with open("index_id.json", "w") as json_file:
    json.dump(index_id, json_file, indent=4)