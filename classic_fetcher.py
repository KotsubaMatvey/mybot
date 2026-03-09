"""
classic_fetcher.py — all HTTP data fetching for classic TA scanner.
Single shared aiohttp session per scan cycle — no per-request session creation.
"""
import aiohttp
import logging

logger = logging.getLogger(__name__)

BINANCE_FUTURES_API = "https://fapi.binance.com"
BINANCE_SPOT_API    = "https://api.binance.com"

_connector: aiohttp.TCPConnector | None = None


def _get_connector() -> aiohttp.TCPConnector:
    """Reuse connector across requests — avoids DNS lookup on every call."""
    global _connector
    if _connector is None or _connector.closed:
        _connector = aiohttp.TCPConnector(limit=10, ttl_dns_cache=300)
    return _connector


async def fetch_candles(symbol: str, interval: str, limit: int = 100) -> list:
    url    = f"{BINANCE_FUTURES_API}/fapi/v1/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    try:
        async with aiohttp.ClientSession(connector=_get_connector(),
                                         connector_owner=False) as s:
            async with s.get(url, params=params,
                             timeout=aiohttp.ClientTimeout(total=10)) as r:
                data = await r.json()
        return [
            {"time": int(d[0]), "open": float(d[1]), "high": float(d[2]),
             "low": float(d[3]), "close": float(d[4]), "volume": float(d[5])}
            for d in data
        ]
    except Exception as e:
        logger.error(f"fetch_candles {symbol} {interval}: {e}")
        return []


async def fetch_orderbook(symbol: str) -> dict:
    """Binance SPOT orderbook."""
    url    = f"{BINANCE_SPOT_API}/api/v3/depth"
    params = {"symbol": symbol, "limit": 500}
    try:
        async with aiohttp.ClientSession(connector=_get_connector(),
                                         connector_owner=False) as s:
            async with s.get(url, params=params,
                             timeout=aiohttp.ClientTimeout(total=10)) as r:
                data = await r.json()
        return {
            "bids":   [(float(p), float(q)) for p, q in data.get("bids", [])],
            "asks":   [(float(p), float(q)) for p, q in data.get("asks", [])],
            "source": "BINANCE",
        }
    except Exception as e:
        logger.error(f"fetch_orderbook {symbol}: {e}")
        return {"bids": [], "asks": [], "source": "BINANCE"}


async def fetch_cme_close() -> float | None:
    """Weekly BTCUSDT close as CME proxy."""
    url    = f"{BINANCE_FUTURES_API}/fapi/v1/klines"
    params = {"symbol": "BTCUSDT", "interval": "1w", "limit": 2}
    try:
        async with aiohttp.ClientSession(connector=_get_connector(),
                                         connector_owner=False) as s:
            async with s.get(url, params=params,
                             timeout=aiohttp.ClientTimeout(total=10)) as r:
                data = await r.json()
        if data and len(data) >= 2:
            return float(data[-2][4])
    except Exception as e:
        logger.error(f"fetch_cme_close: {e}")
    return None
