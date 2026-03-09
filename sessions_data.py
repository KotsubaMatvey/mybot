"""
sessions_data.py — HTTP data fetching for session alerts.
Single shared connector, no ClientSession created per call.
"""
import asyncio
import logging
from datetime import datetime, timezone

import aiohttp

logger = logging.getLogger(__name__)

BINANCE_FUTURES = "https://fapi.binance.com"
SYMBOL          = "BTCUSDT"

# ── Shared HTTP client — created once, reused across all calls
_client: aiohttp.ClientSession | None = None
_lock   = asyncio.Lock()


async def get_client() -> aiohttp.ClientSession:
    """Return the shared session, creating it if needed."""
    global _client
    async with _lock:
        if _client is None or _client.closed:
            connector = aiohttp.TCPConnector(limit=5, ttl_dns_cache=300)
            _client   = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=8),
            )
    return _client


async def close_client():
    """Call on shutdown to cleanly close the shared session."""
    global _client
    if _client and not _client.closed:
        await _client.close()
        _client = None


async def fetch_asian_range() -> tuple[float, float] | None:
    """
    Returns (high, low) of the Asian session (00:00–08:00 UTC today).
    Uses 1h candles from Binance Futures.
    """
    url    = f"{BINANCE_FUTURES}/fapi/v1/klines"
    params = {"symbol": SYMBOL, "interval": "1h", "limit": 10}
    try:
        client = await get_client()
        async with client.get(url, params=params) as r:
            data = await r.json()

        now_utc = datetime.now(timezone.utc)
        asia_start = int(datetime(
            now_utc.year, now_utc.month, now_utc.day, 0, 0,
            tzinfo=timezone.utc
        ).timestamp() * 1000)
        asia_end = int(datetime(
            now_utc.year, now_utc.month, now_utc.day, 8, 0,
            tzinfo=timezone.utc
        ).timestamp() * 1000)

        candles = [c for c in data if asia_start <= int(c[0]) < asia_end]
        if not candles:
            return None

        return (
            max(float(c[2]) for c in candles),  # high
            min(float(c[3]) for c in candles),  # low
        )

    except Exception as e:
        logger.error(f"fetch_asian_range: {e}")
        return None
