import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, LOG_LEVEL
from database.engine import init_db
from handlers import start, menu, quiz, daily_challenge, profile, admin

# Logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set! Create .env file from .env.example")
        return

    await init_db()
    logger.info("Database initialized.")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Register routers
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(quiz.router)
    dp.include_router(daily_challenge.router)
    dp.include_router(profile.router)
    dp.include_router(admin.router)

    logger.info("FootballIQ bot starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped.")