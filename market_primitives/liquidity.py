from __future__ import annotations

from dataclasses import dataclass

from .common import Candle, LiquiditySweep, SwingPoint, collect_swings


@dataclass(slots=True)
class LiquidityPool:
    symbol: str
    timeframe: str
    direction: str
    level: float
    touches: int
    latest_timestamp: int


def detect_liquidity_pools(
    candles: list[Candle],
    symbol: str,
    timeframe: str,
    tolerance: float = 0.001,
) -> list[LiquidityPool]:
    swing_highs, swing_lows = collect_swings(candles[:-1], symbol, timeframe)
    pools: list[LiquidityPool] = []

    for direction, swings in (("bearish", swing_highs), ("bullish", swing_lows)):
        used: set[int] = set()
        for idx, swing in enumerate(swings):
            if idx in used:
                continue
            matched = [swing]
            for other_idx in range(idx + 1, len(swings)):
                other = swings[other_idx]
                if swing.level > 0 and abs(other.level - swing.level) / swing.level <= tolerance:
                    matched.append(other)
                    used.add(other_idx)
            if len(matched) >= 2:
                level = sum(item.level for item in matched) / len(matched)
                pools.append(
                    LiquidityPool(
                        symbol=symbol,
                        timeframe=timeframe,
                        direction=direction,
                        level=level,
                        touches=len(matched),
                        latest_timestamp=max(item.timestamp for item in matched),
                    )
                )
    return pools


def _build_sweep(
    *,
    symbol: str,
    timeframe: str,
    candle: Candle,
    swing: SwingPoint,
    direction: str,
    wick_extreme: float,
    close_back_inside: float,
    clean: bool,
) -> LiquiditySweep:
    return LiquiditySweep(
        symbol=symbol,
        timeframe=timeframe,
        direction=direction,  # type: ignore[arg-type]
        timestamp=candle["time"],
        liquidity_level=swing.level,
        wick_extreme=wick_extreme,
        close_back_inside=close_back_inside,
        source_swing_index=swing.index,
        clean=clean,
        metadata={
            "swing_time": swing.timestamp,
            "range_size": candle["high"] - candle["low"],
            "volume": candle["volume"],
        },
    )


def detect_sweeps(candles: list[Candle], symbol: str, timeframe: str) -> list[LiquiditySweep]:
    if len(candles) < 25:
        return []

    sweep_candle = candles[-2]
    lookback = candles[-31:-2]
    swing_highs, swing_lows = collect_swings(lookback, symbol, timeframe)
    results: list[LiquiditySweep] = []

    swing = _latest_swept_swing(swing_highs, sweep_candle, side="high")
    if swing is not None:
        if sweep_candle["high"] > swing.level and sweep_candle["close"] < swing.level:
            clean = (sweep_candle["high"] - swing.level) > abs(sweep_candle["close"] - swing.level)
            results.append(
                _build_sweep(
                    symbol=symbol,
                    timeframe=timeframe,
                    candle=sweep_candle,
                    swing=swing,
                    direction="bearish",
                    wick_extreme=sweep_candle["high"],
                    close_back_inside=sweep_candle["close"],
                    clean=clean,
                )
            )

    swing = _latest_swept_swing(swing_lows, sweep_candle, side="low")
    if swing is not None:
        if sweep_candle["low"] < swing.level and sweep_candle["close"] > swing.level:
            clean = (sweep_candle["close"] - swing.level) > abs(sweep_candle["low"] - swing.level)
            results.append(
                _build_sweep(
                    symbol=symbol,
                    timeframe=timeframe,
                    candle=sweep_candle,
                    swing=swing,
                    direction="bullish",
                    wick_extreme=sweep_candle["low"],
                    close_back_inside=sweep_candle["close"],
                    clean=clean,
                )
            )

    return results


def detect_liquidity_raids(candles: list[Candle], symbol: str, timeframe: str) -> list[LiquiditySweep]:
    if len(candles) < 30:
        return []

    sweep_candle = candles[-2]
    lookback = candles[-35:-2]
    swing_highs, swing_lows = collect_swings(lookback, symbol, timeframe)
    if not swing_highs and not swing_lows:
        return []

    avg_range = sum(c["high"] - c["low"] for c in lookback[-20:]) / min(len(lookback), 20)
    avg_volume = sum(c["volume"] for c in lookback[-20:]) / min(len(lookback), 20)
    vol_ratio = (sweep_candle["volume"] / avg_volume) if avg_volume else 1.0
    candle_range = sweep_candle["high"] - sweep_candle["low"]
    displacement = candle_range >= avg_range * 1.1

    results: list[LiquiditySweep] = []
    swing = _latest_swept_swing(swing_highs, sweep_candle, side="high")
    if swing is not None:
        if sweep_candle["high"] > swing.level and sweep_candle["close"] < swing.level and (displacement or vol_ratio >= 1.4):
            results.append(
                _build_sweep(
                    symbol=symbol,
                    timeframe=timeframe,
                    candle=sweep_candle,
                    swing=swing,
                    direction="bearish",
                    wick_extreme=sweep_candle["high"],
                    close_back_inside=sweep_candle["close"],
                    clean=True,
                )
            )
            results[-1].metadata["volume_ratio"] = vol_ratio
            results[-1].metadata["raid"] = True

    swing = _latest_swept_swing(swing_lows, sweep_candle, side="low")
    if swing is not None:
        if sweep_candle["low"] < swing.level and sweep_candle["close"] > swing.level and (displacement or vol_ratio >= 1.4):
            results.append(
                _build_sweep(
                    symbol=symbol,
                    timeframe=timeframe,
                    candle=sweep_candle,
                    swing=swing,
                    direction="bullish",
                    wick_extreme=sweep_candle["low"],
                    close_back_inside=sweep_candle["close"],
                    clean=True,
                )
            )
            results[-1].metadata["volume_ratio"] = vol_ratio
            results[-1].metadata["raid"] = True

    return results


def _latest_swept_swing(swings: list[SwingPoint], candle: Candle, side: str) -> SwingPoint | None:
    for swing in reversed(swings[-4:]):
        if side == "high" and candle["high"] > swing.level and candle["close"] < swing.level:
            return swing
        if side == "low" and candle["low"] < swing.level and candle["close"] > swing.level:
            return swing
    return None


__all__ = [
    "LiquidityPool",
    "detect_liquidity_pools",
    "detect_liquidity_raids",
    "detect_sweeps",
]
