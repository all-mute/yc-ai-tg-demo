from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from loguru import logger
import dotenv
import os
from app.handlers import (
    start_handler,
    searchapi_handler,
    searchapi_contextual_handler,
    ai_assistant_handler,
    new_thread_handler,
    help_handler
)
from telegram import BotCommand

# Загрузка переменных окружения
dotenv.load_dotenv()

# Получение токена и настройки ответа
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
REPLY_ALL = os.getenv("REPLY_ALL") == "True"

async def register_handlers(application: Application) -> None:
    """Регистрация обработчиков команд и сообщений."""
    commands = [
        BotCommand("start", "Начать работу с ботом"),
        BotCommand("help", "Помощь"),
        BotCommand("searchapi", "Поиск через SearchAPI"),
        BotCommand("searchapi_contextual", "Поиск через SearchAPI с контекстом треда"),
        BotCommand("new_thread", "Создать новый поток")
    ]
    
    # Устанавливаем команды для бота
    await application.bot.set_my_commands(commands)
    logger.debug("Команды успешно установлены.")
    
    logger.debug("Начинаем регистрацию обработчиков.")
    
    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("searchapi", searchapi_handler))
    application.add_handler(CommandHandler("searchapi_contextual", searchapi_contextual_handler))
    application.add_handler(CommandHandler("new_thread", new_thread_handler))
    
    # Регистрация обработчика текстовых сообщений
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            ai_assistant_handler
        ),
    )
    
    logger.info("Все обработчики успешно зарегистрированы.")

async def bot_init() -> Application:
    """Инициализация бота и регистрация обработчиков."""
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    logger.debug("Инициализация бота завершена.")
    
    # Регистрируем обработчики
    await register_handlers(application)
    
    return application
