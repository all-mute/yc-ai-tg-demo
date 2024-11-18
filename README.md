# ТГ бот для использования сервисов Yandex Cloud:
* [Search API Generative answer](https://yandex.cloud/ru/services/search-api)
* [AI Assistants](https://yandex.cloud/ru/events/979)

## Описание
Этот проект представляет собой Telegram-бота, который позволяет использовать сервисы Yandex Cloud:
* **Search API Generative answer** - сервис получения ответов на вопросы по документам, размещенным в интернете
* **AI Assistants** - сервис для создания и использования AI-ассистентов с возможностью получения ответов на вопросы по внутренним приматным документам

через интерфейс телеграм-бота. Требуется предвартельная настройка.

### Описание команд

* `/start` - Начинает работу с ботом и приветствует пользователя.
* `/help` - Предоставляет информацию о возможностях бота и его командах.
* `/searchapi` - Выполняет поиск через Search API. Пользователь должен ввести запрос после команды.
* `/searchapi_contextual` - Выполняет поиск через Search API с учетом контекста текущего треда и записью в негг. Пользователь должен ввести запрос после команды.
* `/new_thread` - Создает новый поток для чата, позволяя пользователю начать новый разговор с ботом.

Примеры взаимодействия с ботом:


## До начала установки

1. Зарегистрируйте бота в [Telegram BotFather](https://t.me/BotFather) и получите токен. (введите команду `/newbot` и следуйте инструкциям)
2. Зарегистрируйтесь в [Yandex Cloud](https://cloud.yandex.ru/) и создайте сервисный аккаунт с ролями `ai.assistant.editor` и `ai.search-api.user`. [как это сделать?](https://yandex.cloud/ru/docs/iam/concepts/users/service-accounts) [как это сделать (2)?](https://yandex.cloud/ru/docs/search-api/operations/workaround#create-api-key)
2. Получите API ключ и идентификатор папки в Yandex Cloud. [как это сделать?](https://yandex.cloud/ru/docs/foundation-models/quickstart/yandexgpt)
3. Убедитесь, что у вас установлен Python 3.10 или выше. [как это сделать?](https://www.python.org/downloads/)
4. (Не обязательно) Убедитесь, что у вас установлен Docker и Docker Compose. [как это сделать (1)?](https://docs.docker.com/get-docker/) [как это сделать (2)?](https://docs.docker.com/compose/install/)
5. (Для использования Search API) Зарегистрируйтесь в сервисе [SearchAPI](https://yandex.cloud/ru/docs/search-api/quickstart#registration)

## Подготовка к запуску

1. Клонируйте репозиторий:
   ```bash
   git clone <URL_репозитория>
   cd <имя_папки>
   ```

Или скачайте архив с проектом и распакуйте его в любую директорию.

2. Создайте директорию для данных RAG:
   ```bash
   mkdir knowledge/<имя_директории>
   ```

   В директории должны быть файлы с данными в формате .txt, .pdf, .docx

3. Создайте файл `.env` в корневой директории проекта и заполните его следующими переменными окружения:
   ```env
   # Telegram
   TELEGRAM_TOKEN=<токен вашего бота, полученный от BotFather>

   # Yandex Cloud
   YC_API_KEY=<API ключ вашего сервисного аккаунта>
   YC_FOLDER_ID=<идентификатор папки вашего сервисного аккаунта>

   # Search API, подробнее: https://yandex.cloud/ru/docs/search-api/concepts/generative-response#parametry-zaprosa
   SERP_SITE=
   SERP_HOST=
   SERP_URL=

   # Настройки бота
   BOT_NAME=<имя вашего бота>
   DATA_DIR=<имя директории с данными для RAG>
   ```

4. Запустите скрипт для создания индекса:
   ```bash
   python create_rag_index.py
   ```

## Запуск

* Если хотите протестировать бота в локальной среде разработки, установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
   и запустите бота:
   ```bash
   python main.py
   ```

* Если хотите запустить бота в контейнере:
   ```bash
   docker-compose up -d --build
   ```

