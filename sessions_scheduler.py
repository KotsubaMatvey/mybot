"""
sessions_scheduler.py — timing and dispatch for session alerts.
Composes sessions_data + sessions_messages. No formatting, no HTTP here.
"""
import asyncio
import logging
from datetime import datetime, timezone, date

from sessions_data     import fetch_asian_range, close_client
from sessions_messages import EVENTS, build_event_message

logger = logging.getLogger(__name__)

# Fired today: {date: {event_key}} — prevents double-firing
_fired: dict[date, set] = {}


def _seconds_until(hour: int, minute: int) -> float:
    now  = datetime.now(timezone.utc)
    tgt  = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    diff = (tgt - now).total_seconds()
    if diff <= 0:
        diff += 86400
    return diff


def _next_event() -> tuple[float, str]:
    """Return (seconds_to_wait, event_key) for the next upcoming event."""
    candidates = [
        (_seconds_until(h, m), key)
        for h, m, key in EVENTS
    ]
    return min(candidates, key=lambda x: x[0])


def _already_fired(event_key: str) -> bool:
    today = datetime.now(timezone.utc).date()
    return event_key in _fired.get(today, set())


def _mark_fired(event_key: str):
    today = datetime.now(timezone.utc).date()
    _fired.setdefault(today, set()).add(event_key)
    # Cleanup past dates
    for d in [d for d in _fired if d < today]:
        del _fired[d]


async def _fetch_range_if_needed(event_key: str) -> tuple | None:
    if event_key in ("london_open", "ny_open"):
        return await fetch_asian_range()
    return None


async def _dispatch(bot, event_key: str, user_ids: list[int], channel_id: str):
    """Fetch data, build message, send to all recipients."""
    asian_range = await _fetch_range_if_needed(event_key)
    msg = build_event_message(event_key, asian_range)
    if not msg:
        return

    for uid in user_ids:
        try:
            await bot.send_message(uid, msg, parse_mode="Markdown")
            await asyncio.sleep(0.05)
        except Exception as e:
            logger.error(f"session send {uid}: {e}")

    if channel_id:
        try:
            await bot.send_message(channel_id, msg, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"session channel {channel_id}: {e}")

    logger.info(f"Session fired: {event_key} → {len(user_ids)} users")


async def session_scheduler(bot, subscribers_fn, channel_id: str = ""):
    """
    Main loop. Sleeps until next event, fires it, repeats.
    subscribers_fn() — called at fire time to get fresh user list.
    """
    logger.info("Session scheduler started")
    try:
        while True:
            wait, event_key = _next_event()
            await asyncio.sleep(wait)

            if _already_fired(event_key):
                continue

            _mark_fired(event_key)
            user_ids = subscribers_fn()
            await _dispatch(bot, event_key, user_ids, channel_id)

    finally:
        await close_client()
        logger.info("Session scheduler stopped, HTTP client closed")
