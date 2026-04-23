from __future__ import annotations

from .common import Candle, EqualLiquidityLevel, KeyLevel, cluster_levels, collect_swings


def detect_eqh(candles: list[Candle], symbol: str, timeframe: str, tolerance: float = 0.001) -> list[EqualLiquidityLevel]:
    if len(candles) < 20:
        return []
    current = candles[-1]
    swing_highs, _ = collect_swings(candles[-50:-1], symbol, timeframe)
    groups = _equal_level_groups([swing.level for swing in swing_highs], tolerance)
    results: list[EqualLiquidityLevel] = []
    for group in groups:
        level = sum(group) / len(group)
        proximity = abs(current["high"] - level) / level
        if current["high"] <= level and proximity <= 0.002:
            results.append(
                EqualLiquidityLevel(
                    symbol=symbol,
                    timeframe=timeframe,
                    direction="bearish",
                    timestamp=current["time"],
                    level=level,
                    touches=len(group),
                    tolerance=tolerance,
                )
            )
    return results


def detect_eql(candles: list[Candle], symbol: str, timeframe: str, tolerance: float = 0.001) -> list[EqualLiquidityLevel]:
    if len(candles) < 20:
        return []
    current = candles[-1]
    _, swing_lows = collect_swings(candles[-50:-1], symbol, timeframe)
    groups = _equal_level_groups([swing.level for swing in swing_lows], tolerance)
    results: list[EqualLiquidityLevel] = []
    for group in groups:
        level = sum(group) / len(group)
        proximity = abs(current["low"] - level) / level
        if current["low"] >= level and proximity <= 0.002:
            results.append(
                EqualLiquidityLevel(
                    symbol=symbol,
                    timeframe=timeframe,
                    direction="bullish",
                    timestamp=current["time"],
                    level=level,
                    touches=len(group),
                    tolerance=tolerance,
                )
            )
    return results


def detect_key_levels(candles: list[Candle], symbol: str, timeframe: str) -> list[KeyLevel]:
    if len(candles) < 35:
        return []
    closed = candles[:-1]
    swing_highs, swing_lows = collect_swings(closed[-60:], symbol, timeframe)
    levels = [item.level for item in swing_highs] + [item.level for item in swing_lows]
    clusters = cluster_levels(levels, tolerance=0.0025)
    current = closed[-1]
    results: list[KeyLevel] = []
    for cluster in clusters:
        if len(cluster) < 2:
            continue
        level = sum(cluster) / len(cluster)
        proximity = abs(current["close"] - level) / level
        if proximity > 0.0035:
            continue
        direction = "bullish" if current["close"] >= level else "bearish"
        bias = "support" if direction == "bullish" else "resistance"
        results.append(
            KeyLevel(
                symbol=symbol,
                timeframe=timeframe,
                direction=direction,
                timestamp=current["time"],
                level=level,
                touches=len(cluster),
                bias=bias,
            )
        )
    return sorted(results, key=lambda item: (-item.touches, abs(current["close"] - item.level)))


def _equal_level_groups(levels: list[float], tolerance: float) -> list[list[float]]:
    groups: list[list[float]] = []
    consumed: set[int] = set()
    for index, level in enumerate(levels):
        if index in consumed:
            continue
        group = [level]
        for other_index in range(index + 1, len(levels)):
            other = levels[other_index]
            if level > 0 and abs(other - level) / level <= tolerance:
                consumed.add(other_index)
                group.append(other)
        if len(group) >= 2:
            groups.append(group)
    return groups


__all__ = ["detect_eqh", "detect_eql", "detect_key_levels"]
