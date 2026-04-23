"""Human-readable market interpretation for classic pattern bundles."""
from __future__ import annotations


def get_market_condition(candles: list[dict]) -> tuple[str, str]:
    """Return a simple range-position condition and bias."""
    if len(candles) < 14:
        return "", ""
    lookback = candles[-14:]
    high = max(candle["high"] for candle in lookback)
    low = min(candle["low"] for candle in lookback)
    if high == low:
        return "", ""
    last_close = candles[-1]["close"]
    position = (last_close - low) / (high - low)

    if position >= 0.85:
        return "Strongly overbought", "bearish"
    if position >= 0.65:
        return "Moderately overbought", "bearish"
    if position <= 0.15:
        return "Strongly oversold", "bullish"
    if position <= 0.35:
        return "Moderately oversold", "bullish"
    return "Neutral", "neutral"


def get_sl_tp(candles: list[dict], direction: str) -> tuple[float, list[float]]:
    if len(candles) < 20:
        return 0.0, []
    lookback = candles[-20:]
    high = max(candle["high"] for candle in lookback)
    low = min(candle["low"] for candle in lookback)
    last = candles[-1]["close"]
    range_size = high - low

    if direction == "bullish":
        stop_loss = round(low - range_size * 0.02, 4)
        targets = [
            round(last + range_size * 0.3, 4),
            round(last + range_size * 0.6, 4),
            round(last + range_size * 1.0, 4),
        ]
    else:
        stop_loss = round(high + range_size * 0.02, 4)
        targets = [
            round(last - range_size * 0.3, 4),
            round(last - range_size * 0.6, 4),
            round(last - range_size * 1.0, 4),
        ]
    return stop_loss, targets


def pattern_to_interpretation(patterns: list[dict], candles: list[dict], symbol: str, timeframe: str) -> str | None:
    if not patterns or not candles:
        return None

    last_price = candles[-1]["close"]
    pattern_types = {pattern["type"] for pattern in patterns}
    directions = {pattern.get("direction", "") for pattern in patterns}
    bullish_score = sum(
        [
            "Bullish" in directions,
            "BOS" in pattern_types and "Bullish" in directions,
            "CHoCH" in pattern_types and "Bullish" in directions,
            "Sweeps" in pattern_types and "Bullish" in directions,
            "IFVG" in pattern_types and "Bullish" in directions,
        ]
    )
    bearish_score = sum(
        [
            "Bearish" in directions,
            "BOS" in pattern_types and "Bearish" in directions,
            "CHoCH" in pattern_types and "Bearish" in directions,
            "Sweeps" in pattern_types and "Bearish" in directions,
            "IFVG" in pattern_types and "Bearish" in directions,
        ]
    )

    condition, condition_direction = get_market_condition(candles)
    if bullish_score > bearish_score:
        direction = "bullish"
    elif bearish_score > bullish_score:
        direction = "bearish"
    elif condition_direction in {"bullish", "bearish"}:
        direction = condition_direction
    else:
        return None

    if "CHoCH" in pattern_types:
        signal_label = "CHoCH - potential reversal"
        signal_type = "reversal"
    elif "Sweeps" in pattern_types:
        signal_label = "Liquidity sweep"
        signal_type = "reversal"
    elif "BOS" in pattern_types:
        signal_label = "BOS - continuation"
        signal_type = "trend"
    elif "IFVG" in pattern_types:
        signal_label = "IFVG retest"
        signal_type = "bounce"
    elif "FVG" in pattern_types:
        signal_label = "FVG in play"
        signal_type = "bounce"
    elif "OB" in pattern_types:
        signal_label = "Order block reaction"
        signal_type = "bounce"
    elif condition and condition != "Neutral":
        signal_label = condition
        signal_type = "condition"
    else:
        return None

    stop_loss, targets = get_sl_tp(candles, direction)
    if not targets:
        return None

    trade_type = {
        "trend": f"Trend {'Long' if direction == 'bullish' else 'Short'}",
        "reversal": f"Reversal {'Long' if direction == 'bullish' else 'Short'}",
        "bounce": f"Reaction {'Long' if direction == 'bullish' else 'Short'}",
        "condition": f"Bias {'Bullish' if direction == 'bullish' else 'Bearish'}",
    }[signal_type]

    def fmt(price: float) -> str:
        return f"{price:,.2f}" if price > 100 else f"{price:.4f}"

    return "\n".join(
        [
            f"*{timeframe} | {trade_type}*",
            f"*#{symbol}* | current price `{fmt(last_price)}`",
            "",
            f"*{signal_label}*",
            f"Entry: `{fmt(last_price)}`",
            f"Stop-loss: `{fmt(stop_loss)}`",
            "Targets:",
            f"1. `{fmt(targets[0])}`",
            f"2. `{fmt(targets[1])}`",
            f"3. `{fmt(targets[2])}`",
        ]
    )


__all__ = ["get_market_condition", "get_sl_tp", "pattern_to_interpretation"]
