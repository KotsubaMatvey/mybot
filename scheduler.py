"""Production task orchestration."""
from __future__ import annotations

import asyncio
import logging
import signal
from datetime import datetime, timezone
from typing import Any, Callable, Coroutine

from telegram.ext import Application

from config import CHANNEL_ID, CRYPTOBOT_TOKEN, OWNER_IDS, TELEGRAM_BOT_TOKEN
from health import record_error, start_health_server

logger = logging.getLogger(__name__)

_tasks: dict[str, asyncio.Task] = {}
_RESTART_DELAY = 10
_HEALTH_LOG_INTERVAL = 300


class ConfigError(RuntimeError):
    """Raised when required runtime configuration is missing."""


def validate_config() -> None:
    errors: list[str] = []
    warnings: list[str] = []

    if not TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN is not set")
    if not OWNER_IDS:
        warnings.append("OWNER_IDS is empty; no owner will have free access")
    if not CRYPTOBOT_TOKEN:
        warnings.append("CRYPTOBOT_TOKEN is not set; payments are disabled")
    if not CHANNEL_ID:
        warnings.append("CHANNEL_ID is not set; classic channel alerts are disabled")

    for warning in warnings:
        logger.warning("Config warning: %s", warning)
    if errors:
        for error in errors:
            logger.critical("Config error: %s", error)
        raise ConfigError("Bot cannot start: " + "; ".join(errors))

    logger.info("Config validation passed")


async def _managed_task(
    name: str,
    coro_factory: Callable[[], Coroutine[Any, Any, None]],
    *,
    restart: bool = True,
) -> None:
    while True:
        logger.info("[%s] starting", name)
        try:
            await coro_factory()
            logger.warning("[%s] exited normally; expected a long-running task", name)
        except asyncio.CancelledError:
            logger.info("[%s] cancelled", name)
            return
        except Exception as exc:
            record_error()
            logger.error("[%s] crashed: %s", name, exc, exc_info=True)

        if not restart:
            logger.info("[%s] not restarting", name)
            return

        logger.info("[%s] restarting in %ss", name, _RESTART_DELAY)
        await asyncio.sleep(_RESTART_DELAY)


def _spawn(name: str, coro_factory: Callable[[], Coroutine[Any, Any, None]], *, restart: bool = True) -> asyncio.Task:
    task = asyncio.create_task(_managed_task(name, coro_factory, restart=restart), name=name)
    _tasks[name] = task
    return task


async def _health_logger() -> None:
    while True:
        await asyncio.sleep(_HEALTH_LOG_INTERVAL)
        alive = [name for name, task in _tasks.items() if not task.done()]
        dead = [name for name, task in _tasks.items() if task.done()]
        now = datetime.now(timezone.utc).strftime("%H:%M UTC")
        logger.info("[health] %s | alive=%s | dead=%s", now, alive, dead or "none")


async def _shutdown() -> None:
    logger.info("Shutdown requested; cancelling all tasks")
    for name, task in _tasks.items():
        if task.done():
            continue
        task.cancel()
        logger.info("Cancelled: %s", name)
    await asyncio.gather(*_tasks.values(), return_exceptions=True)
    logger.info("Shutdown complete")


def _install_signal_handlers() -> None:
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, lambda: asyncio.create_task(_shutdown()))
        except NotImplementedError:
            pass


async def post_init(application: Application) -> None:
    """Initialize managed background tasks after Telegram app startup."""
    validate_config()
    _install_signal_handlers()

    from alerts import scanner_loop
    from classic_scanner import channel_scheduler
    from database import get_session_alert_users
    from sessions_scheduler import session_scheduler

    _spawn("scanner", lambda: scanner_loop(application))
    _spawn("health_server", lambda: start_health_server(port=8080), restart=False)
    _spawn("health_logger", _health_logger)

    if CHANNEL_ID:
        _spawn("channel", lambda: channel_scheduler(application.bot, CHANNEL_ID))

    _spawn(
        "sessions",
        lambda: session_scheduler(
            application.bot,
            subscribers_fn=get_session_alert_users,
            channel_id=CHANNEL_ID,
        ),
    )

    logger.info(
        "Orchestrator started | tasks=%s | channel=%s | payments=%s",
        list(_tasks.keys()),
        "enabled" if CHANNEL_ID else "disabled",
        "enabled" if CRYPTOBOT_TOKEN else "disabled",
    )


__all__ = ["ConfigError", "post_init", "validate_config"]
