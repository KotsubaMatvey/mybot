from __future__ import annotations

from .common import Candle, PDZone, collect_swings


def detect_pd_zones(candles: list[Candle], symbol: str, timeframe: str) -> list[PDZone]:
    if len(candles) < 30:
        return []
    scan = candles[-51:-1]
    previous = candles[-2]
    current = candles[-1]
    swing_highs, swing_lows = collect_swings(scan, symbol, timeframe)
    if not swing_highs or not swing_lows:
        return []

    last_high = swing_highs[-1]
    last_low = swing_lows[-1]
    high = last_high.level
    low = last_low.level
    equilibrium = (high + low) / 2
    results: list[PDZone] = []

    if last_low.index > last_high.index:
        ote_low = low + (high - low) * 0.618
        ote_high = low + (high - low) * 0.786
        if ote_low <= current["high"] <= ote_high and not (ote_low <= previous["high"] <= ote_high):
            results.append(
                PDZone(
                    symbol=symbol,
                    timeframe=timeframe,
                    kind="ote_discount",
                    timestamp=current["time"],
                    equilibrium=equilibrium,
                    zone_low=ote_low,
                    zone_high=ote_high,
                )
            )
            return results

    if last_high.index > last_low.index:
        ote_high = high - (high - low) * 0.618
        ote_low = high - (high - low) * 0.786
        if ote_low <= current["low"] <= ote_high and not (ote_low <= previous["low"] <= ote_high):
            results.append(
                PDZone(
                    symbol=symbol,
                    timeframe=timeframe,
                    kind="ote_premium",
                    timestamp=current["time"],
                    equilibrium=equilibrium,
                    zone_low=ote_low,
                    zone_high=ote_high,
                )
            )
            return results

    if previous["close"] <= equilibrium < current["close"]:
        return [
            PDZone(
                symbol=symbol,
                timeframe=timeframe,
                kind="premium",
                timestamp=current["time"],
                equilibrium=equilibrium,
                zone_low=equilibrium,
                zone_high=equilibrium,
            )
        ]
    if previous["close"] >= equilibrium > current["close"]:
        return [
            PDZone(
                symbol=symbol,
                timeframe=timeframe,
                kind="discount",
                timestamp=current["time"],
                equilibrium=equilibrium,
                zone_low=equilibrium,
                zone_high=equilibrium,
            )
        ]
    return []


__all__ = ["detect_pd_zones"]
