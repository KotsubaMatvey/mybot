"""
sessions.py — trading session alerts module

Sessions (UTC):
  Asia    00:00 – 09:00
  London  08:00 – 17:00
  NY      13:00 – 22:00

Overlaps:
  London+Asia  08:00 – 09:00
  London+NY    13:00 – 17:00  ← most active

Events fired per day (UTC times):
  00:00  Asia Open
  08:00  London Open   + Asian range
  09:00  Asia Close
  13:00  NY Open       + Asian range  + London+NY overlap start
  17:00  London Close  + overlap end
  22:00  NY Close
"""
import asyncio
import logging
from datetime import datetime, timezone, date

import aiohttp

logger = logging.getLogger(__name__)

BINANCE_FUTURES = "https://fapi.binance.com"
SYMBOL          = "BTCUSDT"   # range always shown for BTC

# ── Session schedule (UTC hour, minute) → event key
# Each entry: (hour, minute, event_key)
_EVENTS: list[tuple[int, int, str]] = [
    (0,  0,  "asia_open"),
    (8,  0,  "london_open"),
    (9,  0,  "asia_close"),
    (13, 0,  "ny_open"),
    (17, 0,  "london_close"),
    (22, 0,  "ny_close"),
]

# Session windows for "current session" query
_SESSIONS = {
    "Asia":   (0,  9),
    "London": (8,  17),
    "NY":     (13, 22),
}

# Fired today: {date: {event_key}}
_fired: dict[date, set] = {}


# ══════════════════════════════════════════════════════════════════════════════
#  DATA
# ══════════════════════════════════════════════════════════════════════════════



async def _fetch_asian_range() -> tuple[float, float] | None:
    """
    Asian session range = high/low of candles from 00:00 to 08:00 UTC today.
    Uses 1h candles — last 8 candles covers exactly the Asian session.
    """
    url    = f"{BINANCE_FUTURES}/fapi/v1/klines"
    params = {"symbol": SYMBOL, "interval": "1h", "limit": 10}
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, params=params,
                             timeout=aiohttp.ClientTimeout(total=8)) as r:
                data = await r.json()

        now_utc = datetime.now(timezone.utc)
        # Asian session: today 00:00–08:00 UTC
        asia_start_ts = int(datetime(
            now_utc.year, now_utc.month, now_utc.day, 0, 0,
            tzinfo=timezone.utc
        ).timestamp() * 1000)
        asia_end_ts = int(datetime(
            now_utc.year, now_utc.month, now_utc.day, 8, 0,
            tzinfo=timezone.utc
        ).timestamp() * 1000)

        asian_candles = [
            c for c in data
            if asia_start_ts <= int(c[0]) < asia_end_ts
        ]
        if not asian_candles:
            return None

        high = max(float(c[2]) for c in asian_candles)
        low  = min(float(c[3]) for c in asian_candles)
        return high, low

    except Exception as e:
        logger.error(f"sessions fetch_asian_range: {e}")
        return None


# ══════════════════════════════════════════════════════════════════════════════
#  MESSAGE BUILDERS
# ══════════════════════════════════════════════════════════════════════════════

def _fmt(p: float) -> str:
    return f"{p:,.1f}" if p >= 1000 else f"{p:.2f}"


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M UTC")


def _build_open(name: str, emoji: str, asian_range: tuple | None, extra: str = "") -> str:
    lines = [f"{emoji} *{name} Open*  ·  {_ts()}"]
    if extra:
        lines.append(extra)
    if asian_range:
        hi, lo = asian_range
        lines.append(f"\nAsian Range:  `{_fmt(lo)} — {_fmt(hi)}`")
    return "\n".join(lines)


def _build_close(name: str, emoji: str) -> str:
    return f"{emoji} *{name} Close*  ·  {_ts()}"


def _build_overlap(action: str) -> str:
    emoji = "⚡" if action == "start" else "🔔"
    verb  = "started" if action == "start" else "ended"
    return f"{emoji} *London + NY Overlap {verb}*  ·  {_ts()}\n_Most active period of the day_"


async def _build_message(event_key: str) -> str | None:
    """Build the right message for each event. Returns None on data failure."""

    needs_range = event_key in ("london_open", "ny_open")

    asian_range = await _fetch_asian_range() if needs_range else None

    match event_key:
        case "asia_open":
            return _build_open("Asia", "🌏", None)
        case "asia_close":
            return _build_close("Asia", "🌏")
        case "london_open":
            return _build_open("London", "🌍", asian_range)
        case "london_close":
            return (
                _build_overlap("end") + "\n\n" +
                _build_close("London", "🌍")
            )
        case "ny_open":
            return (
                _build_open("NY", "🗽", asian_range) + "\n\n" +
                _build_overlap("start")
            )
        case "ny_close":
            return _build_close("NY", "🗽")

    return None


# ══════════════════════════════════════════════════════════════════════════════
#  CURRENT SESSION QUERY  (/session command)
# ══════════════════════════════════════════════════════════════════════════════

async def get_current_session_message() -> str:
    now_h   = datetime.now(timezone.utc).hour
    active  = [name for name, (start, end) in _SESSIONS.items()
               if start <= now_h < end]
    if not active:
        # 22:00–00:00 — between NY close and Asia open
        msg = "🌙 *No major session active*  ·  Pre-Asia\n"
    elif len(active) == 2:
        overlap_name = " + ".join(active)
        msg = f"⚡ *{overlap_name} Overlap*  ·  {_ts()}\n_Most active period_\n"
    else:
        emojis = {"Asia": "🌏", "London": "🌍", "NY": "🗽"}
        name   = active[0]
        msg    = f"{emojis[name]} *{name} Session active*  ·  {_ts()}\n"

    return msg


# ══════════════════════════════════════════════════════════════════════════════
#  SCHEDULER LOOP
# ══════════════════════════════════════════════════════════════════════════════

def _seconds_until(hour: int, minute: int) -> float:
    now  = datetime.now(timezone.utc)
    tgt  = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    diff = (tgt - now).total_seconds()
    if diff <= 0:
        diff += 86400   # next day
    return diff


async def session_scheduler(bot, subscribers_fn, channel_id: str = ""):
    """
    Fires session events at exact UTC times.
    subscribers_fn() — callable returning list of user_ids to notify.
    channel_id — optional, also post to public channel.
    """
    logger.info("Session scheduler started")

    while True:
        now    = datetime.now(timezone.utc)
        today  = now.date()

        # Find the next upcoming event
        upcoming = []
        for hour, minute, key in _EVENTS:
            secs = _seconds_until(hour, minute)
            upcoming.append((secs, hour, minute, key))
        upcoming.sort()

        wait_secs, tgt_h, tgt_m, event_key = upcoming[0]
        await asyncio.sleep(wait_secs)

        # Dedup — only fire once per event per day
        fire_date = datetime.now(timezone.utc).date()
        if event_key in _fired.get(fire_date, set()):
            continue
        _fired.setdefault(fire_date, set()).add(event_key)

        # Cleanup old dates
        for d in list(_fired):
            if d < fire_date:
                del _fired[d]

        # Build and send
        msg = await _build_message(event_key)
        if not msg:
            logger.error(f"session: failed to build message for {event_key}")
            continue

        # Send to all subscribed users
        user_ids = subscribers_fn()
        for uid in user_ids:
            try:
                await bot.send_message(uid, msg, parse_mode="Markdown")
                await asyncio.sleep(0.05)
            except Exception as e:
                logger.error(f"session alert {uid}: {e}")

        # Optionally post to channel
        if channel_id:
            try:
                await bot.send_message(channel_id, msg, parse_mode="Markdown")
            except Exception as e:
                logger.error(f"session channel post: {e}")

        logger.info(f"Session event fired: {event_key}")
