from __future__ import annotations

from presentation.types import AlertPayload

_candle_cache: dict[tuple[str, str], list[dict]] = {}
_pattern_cache: dict[tuple[str, str], list[AlertPayload]] = {}
_active_zones: dict[str, dict[str, list[AlertPayload]]] = {}


def get_cached_candles(symbol: str, timeframe: str) -> list[dict]:
    return _candle_cache.get((symbol, timeframe), [])


def set_cached_candles(symbol: str, timeframe: str, candles: list[dict]) -> None:
    _candle_cache[(symbol, timeframe)] = candles


def get_cached_patterns(symbol: str, timeframe: str) -> list[AlertPayload]:
    return _pattern_cache.get((symbol, timeframe), [])


def replace_pattern_cache(alerts: list[AlertPayload]) -> None:
    _pattern_cache.clear()
    for alert in alerts:
        _pattern_cache.setdefault((alert.symbol, alert.timeframe), []).append(alert)


def get_active_zones() -> dict[str, dict[str, list[AlertPayload]]]:
    return dict(_active_zones)


def replace_active_zones(zones: dict[str, dict[str, list[AlertPayload]]]) -> None:
    _active_zones.clear()
    _active_zones.update(zones)


__all__ = [
    "get_active_zones",
    "get_cached_candles",
    "get_cached_patterns",
    "replace_active_zones",
    "replace_pattern_cache",
    "set_cached_candles",
]
