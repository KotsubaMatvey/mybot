from __future__ import annotations

from .common import Candle, VolumeSignal


def detect_volume(candles: list[Candle], symbol: str, timeframe: str) -> list[VolumeSignal]:
    if len(candles) < 22:
        return []
    last = candles[-2]
    avg_volume = sum(c["volume"] for c in candles[-22:-2]) / 20
    if avg_volume == 0:
        return []
    ratio = last["volume"] / avg_volume
    if ratio < 2.0:
        return []
    direction = "bullish" if last["close"] >= last["open"] else "bearish"
    return [
        VolumeSignal(
            symbol=symbol,
            timeframe=timeframe,
            signal_type="spike",
            direction=direction,
            timestamp=last["time"],
            level=last["volume"],
            magnitude=ratio,
            metadata={
                "usd_volume": last["volume"] * last["close"],
                "tier": "Extreme" if ratio >= 5.0 else "Elevated" if ratio >= 3.0 else "Notable",
            },
        )
    ]


def detect_volume_profile(candles: list[Candle], symbol: str, timeframe: str) -> list[VolumeSignal]:
    if len(candles) < 35:
        return []
    closed = candles[:-1]
    window = closed[-48:]
    prices = [c["close"] for c in window]
    low = min(prices)
    high = max(prices)
    if high <= low:
        return []

    bins = 24
    step = (high - low) / bins
    histogram = [0.0] * bins
    for candle in window:
        index = min(int((candle["close"] - low) / step), bins - 1)
        histogram[index] += candle["volume"]

    poc_index = max(range(bins), key=lambda idx: histogram[idx])
    poc = low + (poc_index + 0.5) * step
    current = closed[-1]
    if abs(current["close"] - poc) / poc > 0.003:
        return []

    direction = "bullish" if current["close"] >= current["open"] else "bearish"
    return [
        VolumeSignal(
            symbol=symbol,
            timeframe=timeframe,
            signal_type="profile",
            direction=direction,
            timestamp=current["time"],
            level=poc,
            magnitude=histogram[poc_index],
            metadata={"poc_index": poc_index},
        )
    ]


__all__ = ["detect_volume", "detect_volume_profile"]
