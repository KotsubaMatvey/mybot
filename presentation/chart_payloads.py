from __future__ import annotations

from presentation.types import AlertPayload


def visible_alerts_for_chart(candles: list[dict], alerts: list[AlertPayload], max_items: int = 8) -> list[AlertPayload]:
    if not candles or not alerts:
        return []
    lows = [candle["low"] for candle in candles]
    highs = [candle["high"] for candle in candles]
    price_low = min(lows)
    price_high = max(highs)
    range_size = max(price_high - price_low, 1e-9)
    expanded_low = price_low - range_size * 0.5
    expanded_high = price_high + range_size * 0.5

    visible = [alert for alert in alerts if _alert_intersects_range(alert, expanded_low, expanded_high)]
    visible.sort(key=lambda item: (item.alert_kind != "strategy", -(item.score or 0), -item.timestamp))
    return visible[:max_items]


def _alert_intersects_range(alert: AlertPayload, low: float, high: float) -> bool:
    levels = [
        alert.level,
        alert.gap_low,
        alert.gap_high,
        alert.ob_low,
        alert.ob_high,
        alert.entry_low,
        alert.entry_high,
        alert.invalidation,
        alert.sweep_level,
        alert.structure_level,
    ]
    for level in levels:
        if level is not None and low <= level <= high:
            return True
    return False


__all__ = ["visible_alerts_for_chart"]
