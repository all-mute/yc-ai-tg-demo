from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger
import dotenv
import os
from app.ai.searchapi import search_api_generative, search_api_generative_contextual
from app.ai.ai_assistants import ai_assistant, ai_assistant_new_thread
from app.db_wrappers.sqlitedb import create_log, chat_exists, get_thread_id, set_thread_id, create_chat_and_thread

# Загрузка переменных окружения
dotenv.load_dotenv()

# Получение имени бота из переменных окружения
BOT_NAME = os.getenv("BOT_NAME")

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    logger.debug(f"Вызвана команда /start от пользователя с ID: {update.effective_user.id}")
    await update.message.reply_text(f"Привет! Я {BOT_NAME} - бот, который помогает находить информацию в документации Yandex Cloud.")

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help."""
    logger.debug(f"Вызвана команда /help от пользователя с ID: {update.effective_user.id}")
    await update.message.reply_text("Я бот, который помогает находить информацию в документации Yandex Cloud.")

async def searchapi_contextual_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик запросов API поиска с контекстом треда."""
    logger.debug("Запрос API поиска с контекстом треда")
    
    chat_id = update.effective_chat.id
    user_nickname = update.effective_user.username or "Неизвестный пользователь"
    date = update.message.date
    
    await context.bot.send_chat_action(chat_id=chat_id, action='typing')
    
    query = update.message.text.split(" ", 1)
    
    if len(query) < 2:
        await update.message.reply_text("Пожалуйста, введите запрос после команды /searchapi")
        return
    
    query = query[1]
    thread_id = await safely_get_thread_id(chat_id)
    
    try:
        generated_content = await search_api_generative_contextual(query, thread_id)
        await update.message.reply_text(generated_content)
        
        # Логируем информацию
        create_log(chat_id, user_nickname, query, date.isoformat())
        create_log(chat_id, user_nickname, generated_content, date.isoformat())
    except Exception as e:
        await update.message.reply_text("Произошла ошибка при обработке запроса.")
        logger.error(f"Ошибка при обработке запроса: {e}")
        
        # Логируем ошибку
        create_log(chat_id, user_nickname, query, date.isoformat())
        create_log(chat_id, user_nickname, str(e), date.isoformat())

async def searchapi_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("Обработка запроса к API поиска")
    
    chat_id = update.effective_chat.id
    user_nickname = update.effective_user.username or "Неизвестный пользователь"
    date = update.message.date
    
    await context.bot.send_chat_action(chat_id=chat_id, action='typing')
    
    query = update.message.text.split(" ", 1)
    
    if len(query) < 2:
        await update.message.reply_text("Пожалуйста, введите запрос после команды /searchapi.")
        return
    
    query = query[1]
    
    try:
        generated_content = await search_api_generative(query)
        await update.message.reply_text(generated_content)
        
        # Логируем информацию о запросе и ответе
        create_log(chat_id, user_nickname, query, date.isoformat())
        create_log(chat_id, user_nickname, generated_content, date.isoformat())
    except Exception as e:
        await update.message.reply_text("Произошла ошибка при обработке вашего запроса.")
        logger.error(f"Ошибка при обработке запроса: {e}")
        
        # Логируем информацию об ошибке
        create_log(chat_id, user_nickname, query, date.isoformat())
        create_log(chat_id, user_nickname, str(e), date.isoformat())

async def new_thread_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("Создание нового потока")
    
    chat_id = update.effective_chat.id
    thread_id = await ai_assistant_new_thread(chat_id=chat_id)
    
    if chat_exists(chat_id):
        set_thread_id(chat_id, thread_id)
    else:
        create_chat_and_thread(chat_id, thread_id)
        
    await update.message.reply_text(f"Новый поток успешно создан: {thread_id}")

async def ai_assistant_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("Обработка запроса к AI")
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    chat_id = update.effective_chat.id
    thread_id = await safely_get_thread_id(chat_id)
    
    answer = await ai_assistant(update.message.text, thread_id)
    await update.message.reply_text(answer)

async def safely_get_thread_id(chat_id: str) -> str:
    thread_id = get_thread_id(chat_id)
    
    if not thread_id:
        await new_thread_handler(chat_id)
        
    return get_thread_id(chat_id)