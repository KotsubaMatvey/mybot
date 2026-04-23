"""HTTP data fetching for the classic TA channel scanner."""
from __future__ import annotations

import logging

import aiohttp

logger = logging.getLogger(__name__)

BINANCE_FUTURES_API = "https://fapi.binance.com"
BINANCE_SPOT_API = "https://api.binance.com"
_connector: aiohttp.TCPConnector | None = None


def _get_connector() -> aiohttp.TCPConnector:
    global _connector
    if _connector is None or _connector.closed:
        _connector = aiohttp.TCPConnector(limit=10, ttl_dns_cache=300)
    return _connector


async def fetch_candles(symbol: str, interval: str, limit: int = 100) -> list[dict]:
    url = f"{BINANCE_FUTURES_API}/fapi/v1/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    try:
        async with aiohttp.ClientSession(connector=_get_connector(), connector_owner=False) as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                data = await response.json()
        if not isinstance(data, list):
            return []
        return [
            {
                "time": int(item[0]),
                "open": float(item[1]),
                "high": float(item[2]),
                "low": float(item[3]),
                "close": float(item[4]),
                "volume": float(item[5]),
            }
            for item in data
        ]
    except Exception as exc:
        logger.error("fetch_candles %s %s: %s", symbol, interval, exc)
        return []


async def fetch_orderbook(symbol: str) -> dict:
    url = f"{BINANCE_SPOT_API}/api/v3/depth"
    params = {"symbol": symbol, "limit": 500}
    try:
        async with aiohttp.ClientSession(connector=_get_connector(), connector_owner=False) as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                data = await response.json()
        return {
            "bids": [(float(price), float(quantity)) for price, quantity in data.get("bids", [])],
            "asks": [(float(price), float(quantity)) for price, quantity in data.get("asks", [])],
            "source": "BINANCE",
        }
    except Exception as exc:
        logger.error("fetch_orderbook %s: %s", symbol, exc)
        return {"bids": [], "asks": [], "source": "BINANCE"}


async def fetch_cme_close() -> float | None:
    """Use weekly BTCUSDT futures close as a CME proxy."""
    url = f"{BINANCE_FUTURES_API}/fapi/v1/klines"
    params = {"symbol": "BTCUSDT", "interval": "1w", "limit": 2}
    try:
        async with aiohttp.ClientSession(connector=_get_connector(), connector_owner=False) as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                data = await response.json()
        if isinstance(data, list) and len(data) >= 2:
            return float(data[-2][4])
    except Exception as exc:
        logger.error("fetch_cme_close: %s", exc)
    return None


__all__ = ["fetch_candles", "fetch_cme_close", "fetch_orderbook"]
