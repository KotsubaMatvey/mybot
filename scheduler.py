"""
scheduler.py — production orchestration layer

Responsibilities:
  - Startup config validation (fail fast, not silently)
  - Managed task lifecycle with auto-restart on crash
  - Graceful shutdown with cleanup
  - Health logging every N minutes
  - Single source of truth for what's running
"""
import asyncio
import logging
import signal
from datetime import datetime, timezone
from typing import Callable, Coroutine, Any

from telegram.ext import Application

from config import TELEGRAM_BOT_TOKEN, CHANNEL_ID, CRYPTOBOT_TOKEN, OWNER_IDS
from health import start_health_server, record_error

logger = logging.getLogger(__name__)

# ── Task registry: name → asyncio.Task
_tasks: dict[str, asyncio.Task] = {}

# ── Restart config per task
_RESTART_DELAY  = 10   # seconds before restarting a crashed task
_HEALTH_LOG_INT = 300  # log health summary every 5 minutes


# ══════════════════════════════════════════════════════════════════════════════
#  CONFIG VALIDATION
# ══════════════════════════════════════════════════════════════════════════════

class ConfigError(RuntimeError):
    pass


def validate_config():
    """
    Check all required config at startup.
    Raises ConfigError immediately — never silently continue with bad config.
    """
    errors   = []
    warnings = []

    if not TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN is not set")

    if not OWNER_IDS:
        warnings.append("OWNER_IDS is empty — no owner will have free access")

    if not CRYPTOBOT_TOKEN:
        warnings.append(
            "CRYPTOBOT_TOKEN is not set — payment system disabled. "
            "Bot will run but subscriptions cannot be created."
        )

    if not CHANNEL_ID:
        warnings.append(
            "CHANNEL_ID is not set — classic TA channel alerts disabled."
        )

    for w in warnings:
        logger.warning(f"Config warning: {w}")

    if errors:
        for e in errors:
            logger.critical(f"Config error: {e}")
        raise ConfigError(
            f"Bot cannot start — fix these config errors: {'; '.join(errors)}"
        )

    logger.info("Config validation passed")


# ══════════════════════════════════════════════════════════════════════════════
#  MANAGED TASK — auto-restart on crash
# ══════════════════════════════════════════════════════════════════════════════

async def _managed_task(
    name: str,
    coro_factory: Callable[[], Coroutine[Any, Any, None]],
    restart: bool = True,
):
    """
    Runs a coroutine. If it crashes and restart=True, waits _RESTART_DELAY
    seconds and restarts it. Logs every crash clearly.
    """
    while True:
        logger.info(f"[{name}] starting")
        try:
            await coro_factory()
            # Coroutine returned normally (shouldn't happen for infinite loops)
            logger.warning(f"[{name}] exited normally — expected infinite loop")
        except asyncio.CancelledError:
            logger.info(f"[{name}] cancelled")
            return
        except Exception as e:
            record_error()
            logger.error(f"[{name}] crashed: {e}", exc_info=True)

        if not restart:
            logger.info(f"[{name}] not restarting (restart=False)")
            return

        logger.info(f"[{name}] restarting in {_RESTART_DELAY}s")
        await asyncio.sleep(_RESTART_DELAY)


def _spawn(name: str, coro_factory: Callable, restart: bool = True):
    task = asyncio.create_task(
        _managed_task(name, coro_factory, restart),
        name=name,
    )
    _tasks[name] = task
    return task


# ══════════════════════════════════════════════════════════════════════════════
#  HEALTH LOGGER
# ══════════════════════════════════════════════════════════════════════════════

async def _health_logger():
    while True:
        await asyncio.sleep(_HEALTH_LOG_INT)
        alive  = [n for n, t in _tasks.items() if not t.done()]
        dead   = [n for n, t in _tasks.items() if t.done()]
        now    = datetime.now(timezone.utc).strftime("%H:%M UTC")
        logger.info(
            f"[health] {now} | "
            f"tasks alive: {alive} | "
            f"tasks dead: {dead if dead else 'none'}"
        )


# ══════════════════════════════════════════════════════════════════════════════
#  GRACEFUL SHUTDOWN
# ══════════════════════════════════════════════════════════════════════════════

async def _shutdown():
    logger.info("Shutdown requested — cancelling all tasks")
    for name, task in _tasks.items():
        if not task.done():
            task.cancel()
            logger.info(f"Cancelled: {name}")
    # Wait for all cancellations to complete
    await asyncio.gather(*_tasks.values(), return_exceptions=True)
    logger.info("All tasks stopped — shutdown complete")


def _install_signal_handlers():
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, lambda: asyncio.create_task(_shutdown()))
        except NotImplementedError:
            # Windows doesn't support add_signal_handler
            pass


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

async def post_init(application: Application):
    """Called by python-telegram-bot after bot is initialised."""

    # 1. Validate config — raises ConfigError if broken
    validate_config()

    # 2. Install OS signal handlers for graceful shutdown
    _install_signal_handlers()

    # 3. Import here to avoid circular imports at module level
    from alerts import scanner_loop
    from classic_scanner import channel_scheduler
    from sessions_scheduler import session_scheduler
    from database import get_session_alert_users

    # 4. Spawn managed tasks
    _spawn("scanner",       lambda: scanner_loop(application))
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
        )
    )

    # 5. Log startup summary
    logger.info(
        f"Orchestrator started | "
        f"tasks: {list(_tasks.keys())} | "
        f"channel: {'enabled' if CHANNEL_ID else 'disabled'} | "
        f"payments: {'enabled' if CRYPTOBOT_TOKEN else 'DISABLED'}"
    )
