import asyncio
import signal
from telegram import Update
from telegram.ext import Application
from loguru import logger
from app.bot import bot_init
from app.db_wrappers.init_sqlite_db import init_sqlite_db

# Configure logging
logger.add("logs/app.log", rotation="5 MB", retention="100 days", level="DEBUG")

# Create an event to signal when to stop the bot
stop_event = asyncio.Event()

async def bot_runner():
    try:
        # Initialize database before starting the bot
        logger.info("Initializing database...")
        init_sqlite_db()
        
        # Initialize bot and application
        application: Application = await bot_init()

        # Set up signal handlers
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(application)))

        # Start the bot
        await application.initialize()
        await application.start()
        await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)

        logger.info("Bot started. Press Ctrl+C to stop.")

        # Wait until the stop event is set
        await stop_event.wait()

        # Stop the bot gracefully
        await application.stop()
        await application.shutdown()
        
    except Exception as e:
        logger.error(f"Error while starting the bot: {e}")
        raise
    finally:
        logger.info("Bot has finished working")

async def shutdown(application: Application):
    """Gracefully shut down the application."""
    logger.info("Received stop signal, shutting down...")
    stop_event.set()
    try:
        await asyncio.wait_for(application.stop(), timeout=5.0)
    except asyncio.TimeoutError:
        logger.warning("Shutdown timed out, forcing exit")

if __name__ == "__main__":
    asyncio.run(bot_runner())
