"""
scheduler.py — background task launcher
"""
import asyncio
import logging
from telegram.ext import Application
from alerts import scanner_loop
from classic_scanner import channel_scheduler
from health import start_health_server
from config import CHANNEL_ID

logger = logging.getLogger(__name__)


async def post_init(application: Application):
    asyncio.create_task(scanner_loop(application))
    logger.info("Scanner task started")

    if CHANNEL_ID:
        asyncio.create_task(channel_scheduler(application.bot, CHANNEL_ID))
        logger.info("Channel scheduler started")

    asyncio.create_task(start_health_server(port=8080))
