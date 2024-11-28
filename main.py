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

        try:
            # Запуск бота
            await application.initialize()
            await application.start()
            await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)

            logger.info("Бот запущен. Нажмите Ctrl+C для остановки.")
            
            # Ожидание прерывания
            await stop_event.wait()
                
        except KeyboardInterrupt:
            logger.info("Получен сигнал остановки (Ctrl+C)")
        finally:
            # Корректная остановка бота
            await application.stop()
            await application.shutdown()
            
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise
    finally:
        logger.info("Работа бота завершена.")

def signal_handler(signum, frame):
    """Обработчик сигналов для всех платформ."""
    logger.info("Получен сигнал остановки...")
    stop_event.set()

if __name__ == "__main__":
    # Установка обработчика сигналов перед запуском
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    asyncio.run(bot_runner())
