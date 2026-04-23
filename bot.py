"""Application entrypoint."""
from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from config import TELEGRAM_BOT_TOKEN
from database import init_db
from handlers import (
    callback_handler,
    chart_cmd,
    charts_cmd,
    help_cmd,
    menu_button_handler,
    reset,
    resume_cmd,
    session_status_cmd,
    sessions_cmd,
    start,
    status_cmd,
    stop_cmd,
    zones_cmd,
)
from payment_flow import pay_cmd
from scheduler import post_init

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
    app.add_handler(CommandHandler("help",       help_cmd))
    app.add_handler(CommandHandler("session",    session_status_cmd))
    app.add_handler(CommandHandler("chart",      chart_cmd))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_button_handler))

    logger.info("Bot started")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
