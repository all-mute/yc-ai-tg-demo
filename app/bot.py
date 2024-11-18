from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from loguru import logger
import dotenv, os
from app.handlers import sniffer, snippet_response_command, send_news_command, start_command, add_chat_command, remove_chat_command, all_guides_command, presend_news_command, searchapi_command
from telegram import BotCommand, BotCommandScope
from telegram.constants import BotCommandScopeType

dotenv.load_dotenv()

DB_CHOICE = os.getenv("DB_CHOICE")
if DB_CHOICE == "pocketbase":
    from app.db_wrappers.pb import init_commands_and_snippets
elif DB_CHOICE == "sqlite":
    from app.db_wrappers.sqlitedb import init_commands_and_snippets
elif DB_CHOICE == "jsondb":
    from app.db_wrappers.jsondb import init_commands_and_snippets
else:
    logger.error(f"Неизвестный тип базы данных: {DB_CHOICE}")
    raise ValueError(f"Неизвестный тип базы данных: {DB_CHOICE}")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_ADMIN_IDS = [int(item) for item in os.getenv("TELEGRAM_ADMIN_IDS").split(',')]

commands, snippets = {}, {}
used_commands = ("start", "add_chat", "remove_chat", "all_guides", "send_news", "sync_pb")

async def register_handlers(application: Application) -> None:
    global commands, snippets
    
    logger.debug("Начинаем регистрацию обработчиков.")
    
    if not all([item in used_commands for item in commands]):
        logger.error(f"Не все команды присутствуют в used_commands (из pocketbase)! команды: {commands}")
    
    application.add_handler(CommandHandler("start", start_command))
    logger.debug("Обработчик команды /start зарегистрирован.")
    
    application.add_handler(CommandHandler("add_chat", add_chat_command, filters=filters.ChatType.GROUP | filters.ChatType.SUPERGROUP))
    logger.debug("Обработчик команды /add_chat зарегистрирован.")
    
    application.add_handler(CommandHandler("remove_chat", remove_chat_command, filters=filters.ChatType.GROUP | filters.ChatType.SUPERGROUP))
    logger.debug("Обработчик команды /remove_chat зарегистрирован.")
    
    application.add_handler(CommandHandler("all_guides", all_guides_command))
    logger.debug("Обработчик команды /all_guides зарегистрирован.")
    
    application.add_handler(CommandHandler("searchapi", searchapi_command))
    logger.debug("Обработчик команды /searchapi зарегистрирован.")
    
    application.add_handler(
        MessageHandler(
            filters.TEXT,
            sniffer
        ),
    )
    logger.debug("Обработчик команды /sniffer зарегистрирован.")
    
    application.add_handler(CommandHandler("send_news",
                                           send_news_command,
                                           filters=filters.User(user_id=TELEGRAM_ADMIN_IDS)
                                           ))
    logger.debug("Обработчик команды /send_news зарегистрирован.")
    
    application.add_handler(CommandHandler("presend_news",
                                           presend_news_command,
                                           filters=filters.User(user_id=TELEGRAM_ADMIN_IDS)
                                           ))
    logger.debug("Обработчик команды /presend_news зарегистрирован.")
    
    for snippet, value in snippets.items():
        application.add_handler(CommandHandler(snippet, snippet_response_command))
        logger.debug(f"Обработчик сниппета /{snippet} зарегистрирован.")
        
    # Устанавливаем общие команды для всех пользователей
    await application.bot.set_my_commands([
        BotCommand("start", "Начать работу с ботом"),
        BotCommand("add_chat", "Добавить чат"),
        BotCommand("remove_chat", "Удалить чат"),
        BotCommand("all_guides", "Показать все сниппеты"),
        BotCommand("help", "Помощь"), # WARNING, ITS SNIPPET
    ])
    logger.debug("Общие команды установлены.")
    
    # Устанавливаем специальные команды только для админа
    """await application.bot.set_my_commands(
        commands=[
            BotCommand("send_news", "Отправить новость во все чаты"),
            BotCommand("sync_pb", "Синхранизировать команды и сниппеты"),
        ],
        scope={"type": BotCommandScopeType.CHAT, "chat_id": TELEGRAM_ADMIN_IDS}
    )"""
    logger.debug("Специальные команды для админа установлены.")

async def bot_init():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    global commands, snippets
    commands, snippets = init_commands_and_snippets()
    
    logger.debug("Инициализация бота завершена, команды и сниппеты загружены.")
    
    application.add_handler(CommandHandler("sync_pb", sync_pb))
    logger.debug("Обработчик команды /sync_pb зарегистрирован.")
    
    # Регистрируем остальные обработчики
    await register_handlers(application)
    
    logger.info("Обработчики зарегистрированы.")
    return application

async def sync_pb(update: Update, context: Application) -> None:
    try:
        global commands, snippets
        commands, snippets = init_commands_and_snippets()
        
        logger.debug("Команды и сниппеты синхронизированы.")
        
        context.application.handlers.clear()
        context.application.add_handler(CommandHandler("sync_pb", sync_pb))
        # Регистрируем остальные обработчики
        await register_handlers(context.application)
        
        await update.message.reply_text("Команды и сниппеты успешно обновлены! ✅")
        logger.info("Обработчики повторно зарегистрированы после команды sync_pb.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при обновлении: {str(e)} ❌")
        logger.error(f"Ошибка во время sync_pb: {e}")
