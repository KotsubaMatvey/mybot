from __future__ import annotations

from .common import BreakerBlock, Candle, OrderBlock, collect_swings


def detect_order_blocks(candles: list[Candle], symbol: str, timeframe: str) -> list[OrderBlock]:
    if len(candles) < 20:
        return []

    closed = candles[:-1]
    lookback = closed[-40:]
    swing_highs, swing_lows = collect_swings(lookback, symbol, timeframe)
    results: list[OrderBlock] = []
    current = lookback[-1]
    n = len(lookback)

    if swing_highs:
        swing = swing_highs[-1]
        bos_idx = next((idx for idx in range(swing.index + 1, n) if lookback[idx]["close"] > swing.level), None)
        if bos_idx is not None and 1 < bos_idx < n:
            ob_candle = _largest_body_run(lookback, bos_idx - 1, bearish=True)
            if ob_candle is not None:
                zone_low = min(ob_candle["open"], ob_candle["close"])
                zone_high = max(ob_candle["open"], ob_candle["close"])
                midpoint = (zone_low + zone_high) / 2
                in_zone = zone_low <= current["close"] <= zone_high or zone_low <= current["low"] <= zone_high
                invalidated = current["close"] < midpoint
                validated = lookback[bos_idx]["close"] > zone_high
                results.append(
                    OrderBlock(
                        symbol=symbol,
                        timeframe=timeframe,
                        direction="bullish",
                        timestamp=current["time"],
                        origin_time=ob_candle["time"],
                        zone_low=zone_low,
                        zone_high=zone_high,
                        midpoint=midpoint,
                        mitigated=in_zone,
                        invalidated=invalidated,
                        open=ob_candle["open"],
                        close=ob_candle["close"],
                        high=ob_candle["high"],
                        low=ob_candle["low"],
                        mean_threshold=midpoint,
                        validated=validated,
                        validation_time=lookback[bos_idx]["time"] if validated else None,
                        invalidation_time=current["time"] if invalidated else None,
                        metadata={
                            "broken_level": swing.level,
                            "mean_threshold": midpoint,
                            "validated": validated,
                            "invalidation_rule": "close_below_mean_threshold",
                        },
                    )
                )

    if swing_lows:
        swing = swing_lows[-1]
        bos_idx = next((idx for idx in range(swing.index + 1, n) if lookback[idx]["close"] < swing.level), None)
        if bos_idx is not None and 1 < bos_idx < n:
            ob_candle = _largest_body_run(lookback, bos_idx - 1, bearish=False)
            if ob_candle is not None:
                zone_low = min(ob_candle["open"], ob_candle["close"])
                zone_high = max(ob_candle["open"], ob_candle["close"])
                midpoint = (zone_low + zone_high) / 2
                in_zone = zone_low <= current["close"] <= zone_high or zone_low <= current["high"] <= zone_high
                invalidated = current["close"] > midpoint
                validated = lookback[bos_idx]["close"] < zone_low
                results.append(
                    OrderBlock(
                        symbol=symbol,
                        timeframe=timeframe,
                        direction="bearish",
                        timestamp=current["time"],
                        origin_time=ob_candle["time"],
                        zone_low=zone_low,
                        zone_high=zone_high,
                        midpoint=midpoint,
                        mitigated=in_zone,
                        invalidated=invalidated,
                        open=ob_candle["open"],
                        close=ob_candle["close"],
                        high=ob_candle["high"],
                        low=ob_candle["low"],
                        mean_threshold=midpoint,
                        validated=validated,
                        validation_time=lookback[bos_idx]["time"] if validated else None,
                        invalidation_time=current["time"] if invalidated else None,
                        metadata={
                            "broken_level": swing.level,
                            "mean_threshold": midpoint,
                            "validated": validated,
                            "invalidation_rule": "close_above_mean_threshold",
                        },
                    )
                )
    return results


def detect_breaker_blocks(candles: list[Candle], symbol: str, timeframe: str) -> list[BreakerBlock]:
    if len(candles) < 25:
        return []

    closed = candles[:-1]
    if not closed:
        return []
    current = closed[-1]
    lookback = closed[-50:]
    highs, lows = collect_swings(lookback, symbol, timeframe, left=1, right=1)
    results: list[BreakerBlock] = []
    n = len(lookback)

    for idx in range(len(lows) - 1, 0, -1):
        low2 = lows[idx]
        low1 = lows[idx - 1]
        if low2.level >= low1.level:
            continue
        highs_between = [s for s in highs if low1.index < s.index < low2.index]
        if not highs_between:
            continue
        pivot = highs_between[-1]
        bos_idx = next((i for i in range(low2.index + 1, n) if lookback[i]["close"] > pivot.level), None)
        if bos_idx is None:
            continue
        candle = next((lookback[i] for i in range(pivot.index, max(pivot.index - 3, -1), -1) if lookback[i]["close"] > lookback[i]["open"]), None)
        if candle is None:
            continue
        zone_low = min(candle["open"], candle["close"])
        zone_high = max(candle["open"], candle["close"])
        retested = zone_low <= current["close"] <= zone_high or zone_low <= current["low"] <= zone_high
        results.append(
            BreakerBlock(
                symbol=symbol,
                timeframe=timeframe,
                direction="bullish",
                timestamp=current["time"],
                origin_time=candle["time"],
                trigger_time=lookback[bos_idx]["time"],
                zone_low=zone_low,
                zone_high=zone_high,
                retested=retested,
                source_order_block_time=candle["time"],
                source_order_block_direction="bearish",
                sweep_time=low2.timestamp,
                failed_ob_confirmed=True,
                metadata={
                    "pivot_level": pivot.level,
                    "source_ob_time": candle["time"],
                    "sweep_time": low2.timestamp,
                    "failed_ob_confirmed": True,
                },
            )
        )
        break

    for idx in range(len(highs) - 1, 0, -1):
        high2 = highs[idx]
        high1 = highs[idx - 1]
        if high2.level <= high1.level:
            continue
        lows_between = [s for s in lows if high1.index < s.index < high2.index]
        if not lows_between:
            continue
        pivot = lows_between[-1]
        bos_idx = next((i for i in range(high2.index + 1, n) if lookback[i]["close"] < pivot.level), None)
        if bos_idx is None:
            continue
        candle = next((lookback[i] for i in range(pivot.index, max(pivot.index - 3, -1), -1) if lookback[i]["close"] < lookback[i]["open"]), None)
        if candle is None:
            continue
        zone_low = min(candle["open"], candle["close"])
        zone_high = max(candle["open"], candle["close"])
        retested = zone_low <= current["close"] <= zone_high or zone_low <= current["high"] <= zone_high
        results.append(
            BreakerBlock(
                symbol=symbol,
                timeframe=timeframe,
                direction="bearish",
                timestamp=current["time"],
                origin_time=candle["time"],
                trigger_time=lookback[bos_idx]["time"],
                zone_low=zone_low,
                zone_high=zone_high,
                retested=retested,
                source_order_block_time=candle["time"],
                source_order_block_direction="bullish",
                sweep_time=high2.timestamp,
                failed_ob_confirmed=True,
                metadata={
                    "pivot_level": pivot.level,
                    "source_ob_time": candle["time"],
                    "sweep_time": high2.timestamp,
                    "failed_ob_confirmed": True,
                },
            )
        )
        break

    return results


def _largest_body_run(candles: list[Candle], start_idx: int, bearish: bool) -> Candle | None:
    best = None
    best_body = 0.0
    stop_idx = max(start_idx - 5, -1)
    for idx in range(start_idx, stop_idx, -1):
        candle = candles[idx]
        is_bearish = candle["close"] < candle["open"]
        if bearish != is_bearish:
            break
        body = abs(candle["close"] - candle["open"])
        if body > best_body:
            best = candle
            best_body = body
    return best


__all__ = ["detect_breaker_blocks", "detect_order_blocks"]
