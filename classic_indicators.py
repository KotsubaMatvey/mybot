"""Pure helpers for the classic TA channel scanner."""
from __future__ import annotations


def calc_rsi(candles: list[dict], period: int = 14) -> float | None:
    if len(candles) < period + 1:
        return None
    closes = [candle["close"] for candle in candles[-(period + 1) :]]
    gains: list[float] = []
    losses: list[float] = []
    for index in range(1, len(closes)):
        diff = closes[index] - closes[index - 1]
        gains.append(max(diff, 0.0))
        losses.append(max(-diff, 0.0))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    return round(100 - (100 / (1 + avg_gain / avg_loss)), 1)


def rsi_state(rsi: float) -> tuple[str, str]:
    if rsi >= 80:
        return "Strongly overbought", "bearish"
    if rsi >= 70:
        return "Slightly overbought", "bearish"
    if rsi <= 20:
        return "Strongly oversold", "bullish"
    if rsi <= 30:
        return "Slightly oversold", "bullish"
    return "Neutral", "neutral"


def rsi_is_extreme(rsi: float) -> bool:
    return rsi <= 30 or rsi >= 70


def detect_pattern(candles: list[dict]) -> tuple[str, str] | None:
    """Return (pattern_name, direction) for the last closed candle."""
    if len(candles) < 3:
        return None

    candle = candles[-2]
    previous = candles[-3]
    body = abs(candle["close"] - candle["open"])
    range_size = candle["high"] - candle["low"]
    if range_size == 0:
        return None

    body_ratio = body / range_size
    upper_wick = candle["high"] - max(candle["close"], candle["open"])
    lower_wick = min(candle["close"], candle["open"]) - candle["low"]

    if body_ratio < 0.35:
        if lower_wick > body * 2 and lower_wick > upper_wick * 2:
            return "Pinbar", "bullish"
        if upper_wick > body * 2 and upper_wick > lower_wick * 2:
            return "Pinbar", "bearish"

    previous_body = abs(previous["close"] - previous["open"])
    if body > previous_body * 1.5:
        if candle["close"] > candle["open"] and previous["close"] < previous["open"]:
            return "Predict", "bullish"
        if candle["close"] < candle["open"] and previous["close"] > previous["open"]:
            return "Predict", "bearish"

    if body_ratio < 0.1:
        return "Predict", "neutral"
    return None


def analyze_ob(orderbook: dict, price: float) -> dict:
    bids = orderbook.get("bids", [])
    asks = orderbook.get("asks", [])
    if not bids or not asks:
        return {
            "dominant": "neutral",
            "source": orderbook.get("source", "BINANCE"),
            "support": (0.0, 0.0, 0.0),
            "resistance": (0.0, 0.0, 0.0),
        }

    zone = price * 0.01
    wide = price * 0.02
    support_qty = round(sum(quantity for p, quantity in bids if price - zone <= p <= price), 1)
    resistance_qty = round(sum(quantity for p, quantity in asks if price <= p <= price + zone), 1)
    total_bids = sum(quantity for p, quantity in bids if p >= price - wide)
    total_asks = sum(quantity for p, quantity in asks if p <= price + wide)
    dominant = "bids" if total_bids >= total_asks else "asks"

    return {
        "dominant": dominant,
        "source": orderbook.get("source", "BINANCE"),
        "support": (round(price - zone, 1), round(price, 1), support_qty),
        "resistance": (round(price, 1), round(price + zone, 1), resistance_qty),
    }


def compute_sl_tp(candles: list[dict], direction: str, price: float) -> tuple[float, float, float, float]:
    lookback = candles[-20:]
    high = max(candle["high"] for candle in lookback)
    low = min(candle["low"] for candle in lookback)
    range_size = high - low
    if direction == "bullish":
        return (
            round(low - range_size * 0.015, 2),
            round(price + range_size * 0.25, 2),
            round(price + range_size * 0.50, 2),
            round(price + range_size * 0.85, 2),
        )
    return (
        round(high + range_size * 0.015, 2),
        round(price - range_size * 0.25, 2),
        round(price - range_size * 0.50, 2),
        round(price - range_size * 0.85, 2),
    )


__all__ = [
    "analyze_ob",
    "calc_rsi",
    "compute_sl_tp",
    "detect_pattern",
    "rsi_is_extreme",
    "rsi_state",
]
