from __future__ import annotations

from typing import Literal

from strategies.types import PrimitiveSnapshot, SetupStatus

CandleDict = dict[str, float | int]
Side = Literal["long", "short"]


def primitive_direction(side: Side) -> Literal["bullish", "bearish"]:
    return "bullish" if side == "long" else "bearish"


def opposite_direction(direction: Literal["bullish", "bearish"]) -> Literal["bearish", "bullish"]:
    return "bearish" if direction == "bullish" else "bullish"


def closed_candles(snapshot: PrimitiveSnapshot) -> list[CandleDict]:
    return snapshot.candles[:-1] if len(snapshot.candles) > 1 else list(snapshot.candles)


def current_candle(snapshot: PrimitiveSnapshot) -> CandleDict | None:
    if not snapshot.candles:
        return None
    return snapshot.candles[-1]


def candle_touches_zone(candle: CandleDict, low: float, high: float) -> bool:
    return float(candle["low"]) <= high and float(candle["high"]) >= low


def first_closed_touch_after(snapshot: PrimitiveSnapshot, armed_time: int, low: float, high: float) -> CandleDict | None:
    for candle in closed_candles(snapshot):
        if int(candle["time"]) <= armed_time:
            continue
        if candle_touches_zone(candle, low, high):
            return candle
    return None


def current_price(snapshot: PrimitiveSnapshot) -> float | None:
    candle = current_candle(snapshot)
    if candle is not None:
        return float(candle["close"])
    closed = closed_candles(snapshot)
    if closed:
        return float(closed[-1]["close"])
    return None


def timeframe_to_ms(timeframe: str) -> int | None:
    unit = timeframe[-1:]
    try:
        value = int(timeframe[:-1])
    except ValueError:
        return None
    if unit == "m":
        return value * 60_000
    if unit == "h":
        return value * 60 * 60_000
    if unit == "d":
        return value * 24 * 60 * 60_000
    return None


def max_age_ms(timeframe: str, bars: int) -> int | None:
    tf_ms = timeframe_to_ms(timeframe)
    return tf_ms * bars if tf_ms is not None else None


def is_recent_enough(current_timestamp: int, candidate_timestamp: int, timeframe: str, max_bars: int) -> bool:
    age_ms = max_age_ms(timeframe, max_bars)
    if age_ms is None:
        return True
    return current_timestamp - candidate_timestamp <= age_ms


def classify_zone_status(
    snapshot: PrimitiveSnapshot,
    *,
    zone_low: float,
    zone_high: float,
    armed_time: int,
) -> tuple[SetupStatus, int] | None:
    live = current_candle(snapshot)
    if live and candle_touches_zone(live, zone_low, zone_high):
        return "triggered", int(live["time"])

    historical_touch = first_closed_touch_after(snapshot, armed_time, zone_low, zone_high)
    if historical_touch is not None:
        closed = closed_candles(snapshot)
        last_closed_time = int(closed[-1]["time"]) if closed else None
        touch_time = int(historical_touch["time"])
        if last_closed_time is not None and touch_time == last_closed_time:
            return "triggered", touch_time
        return None

    price = current_price(snapshot)
    if price is None:
        return "watching", armed_time
    if zone_low <= price <= zone_high:
        return "triggered", armed_time

    zone_mid = (zone_low + zone_high) / 2
    zone_width = max(abs(zone_high - zone_low), max(zone_mid * 0.0015, 1e-9))
    distance = min(abs(price - zone_low), abs(price - zone_high))
    if distance <= zone_width * 1.25:
        return "confirmed", armed_time
    return "watching", armed_time


def sweep_label(side: Side) -> str:
    return "SSL" if side == "long" else "BSL"


__all__ = [
    "Side",
    "candle_touches_zone",
    "classify_zone_status",
    "closed_candles",
    "current_candle",
    "first_closed_touch_after",
    "is_recent_enough",
    "max_age_ms",
    "opposite_direction",
    "primitive_direction",
    "sweep_label",
    "timeframe_to_ms",
]
