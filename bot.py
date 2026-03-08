"""
Trillion Strategy Alert Bot
ICT pattern scanner + classic TA channel alerts
"""
import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters
)
from database import init_db
from config import TELEGRAM_BOT_TOKEN
from scheduler import post_init
from handlers import (
    start, reset, stop_cmd, resume_cmd,
    status_cmd, zones_cmd, confluence_cmd, help_cmd,
    callback_handler, menu_button_handler
)
from payment_flow import pay_cmd

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    init_db()
    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )
    app.add_handler(CommandHandler("start",      start))
    app.add_handler(CommandHandler("pay",        pay_cmd))
    app.add_handler(CommandHandler("reset",      reset))
    app.add_handler(CommandHandler("stop",       stop_cmd))
    app.add_handler(CommandHandler("resume",     resume_cmd))
    app.add_handler(CommandHandler("status",     status_cmd))
    app.add_handler(CommandHandler("zones",      zones_cmd))
    app.add_handler(CommandHandler("confluence", confluence_cmd))
    app.add_handler(CommandHandler("help",       help_cmd))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_button_handler))

    logger.info("Bot started")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
