import logging
from typing import Optional
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from src.core.config import settings
from src.bot.handlers.start import router as start_router
from src.bot.handlers.browse import router as browse_router
from src.bot.handlers.registration import router as registration_router

logger = logging.getLogger(__name__)

bot: Optional[Bot] = None
dp: Dispatcher = Dispatcher()

# Register bot handlers
dp.include_router(start_router)
dp.include_router(browse_router)
dp.include_router(registration_router)


def get_bot() -> Optional[Bot]:
    """Get or initialize the Telegram Bot instance."""
    global bot
    if bot is None:
        if not settings.BOT_TOKEN or settings.BOT_TOKEN in ["YOUR_BOT_TOKEN_HERE", "your_telegram_bot_token_here"]:
            logger.warning("BOT_TOKEN is not configured in .env. Telegram Bot polling will be skipped.")
            return None
        bot = Bot(
            token=settings.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
    return bot
