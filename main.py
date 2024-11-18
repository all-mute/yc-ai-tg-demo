import asyncio
import signal
from telegram import Update
from telegram.ext import Application
from loguru import logger
from app.bot import bot_init
from app.db_wrappers.init_sqlite_db import init_sqlite_db

# Настройка логирования
logger.add("logs/app.log", rotation="5 MB", retention="100 days", level="DEBUG")

# Создание события для сигнализации о завершении работы бота
stop_event = asyncio.Event()

async def bot_runner():
    """Основная функция для запуска бота."""
    try:
        logger.info("Инициализация базы данных...")
        init_sqlite_db()
        
        # Инициализация бота и приложения
        application: Application = await bot_init()

        # Настройка обработчиков сигналов
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(application)))

        # Запуск бота
        await application.initialize()
        await application.start()
        await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)

        logger.info("Бот запущен. Нажмите Ctrl+C для остановки.")

        # Ожидание сигнала для остановки
        await stop_event.wait()

        # Корректная остановка бота
        await application.stop()
        await application.shutdown()
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise
    finally:
        logger.info("Работа бота завершена.")

async def shutdown(application: Application):
    """Корректное завершение работы приложения."""
    logger.info("Получен сигнал остановки, завершение работы...")
    stop_event.set()
    try:
        await asyncio.wait_for(application.stop(), timeout=5.0)
    except asyncio.TimeoutError:
        logger.warning("Время ожидания завершения истекло, принудительный выход.")

if __name__ == "__main__":
    asyncio.run(bot_runner())
