from __future__ import annotations

from .common import Candle, StructureBreak, SwingPoint, collect_swings
from .displacement import evaluate_displacement


def detect_structure_breaks(candles: list[Candle], symbol: str, timeframe: str) -> list[StructureBreak]:
    if len(candles) < 30:
        return []

    closed = candles[:-1]
    lookback = closed[-50:]
    swing_highs, swing_lows = collect_swings(lookback, symbol, timeframe)
    if len(swing_highs) < 1 or len(swing_lows) < 1:
        return []

    last = closed[-1]
    results: list[StructureBreak] = []

    last_high = next((item for item in reversed(swing_highs) if last["close"] > item.level), swing_highs[-1])
    if last["close"] > last_high.level:
        last_idx = len(closed) - 1
        created_fvg = _created_fvg_after_break(closed, last_idx, "bullish")
        displacement = evaluate_displacement(
            closed,
            last_idx,
            direction="bullish",
            structure_level=last_high.level,
            created_fvg_after_break=created_fvg,
        )
        results.append(
            StructureBreak(
                symbol=symbol,
                timeframe=timeframe,
                break_type="BOS",
                direction="bullish",
                timestamp=last["time"],
                broken_level=last_high.level,
                close_price=last["close"],
                source_swing_index=last_high.index,
                strength=max(_break_strength(last, last_high.level), displacement.displacement_factor),
                displacement_factor=displacement.displacement_factor,
                has_displacement=displacement.has_displacement,
                body_ratio=displacement.body_ratio,
                range_expansion=displacement.range_expansion,
                created_fvg_after_break=created_fvg,
                metadata={
                    "swing_time": last_high.timestamp,
                    "swing_significance": last_high.significance,
                    "created_fvg_after_break": created_fvg,
                },
            )
        )

    last_low = next((item for item in reversed(swing_lows) if last["close"] < item.level), swing_lows[-1])
    if last["close"] < last_low.level:
        last_idx = len(closed) - 1
        created_fvg = _created_fvg_after_break(closed, last_idx, "bearish")
        displacement = evaluate_displacement(
            closed,
            last_idx,
            direction="bearish",
            structure_level=last_low.level,
            created_fvg_after_break=created_fvg,
        )
        results.append(
            StructureBreak(
                symbol=symbol,
                timeframe=timeframe,
                break_type="BOS",
                direction="bearish",
                timestamp=last["time"],
                broken_level=last_low.level,
                close_price=last["close"],
                source_swing_index=last_low.index,
                strength=max(_break_strength(last, last_low.level), displacement.displacement_factor),
                displacement_factor=displacement.displacement_factor,
                has_displacement=displacement.has_displacement,
                body_ratio=displacement.body_ratio,
                range_expansion=displacement.range_expansion,
                created_fvg_after_break=created_fvg,
                metadata={
                    "swing_time": last_low.timestamp,
                    "swing_significance": last_low.significance,
                    "created_fvg_after_break": created_fvg,
                },
            )
        )

    if len(swing_highs) >= 2 and len(swing_lows) >= 2:
        uptrend = swing_highs[-1].level > swing_highs[-2].level
        downtrend = swing_lows[-1].level < swing_lows[-2].level

        choch_low = next((item for item in reversed(swing_lows) if last["close"] < item.level), last_low)
        choch_high = next((item for item in reversed(swing_highs) if last["close"] > item.level), last_high)

        if uptrend and last["close"] < choch_low.level:
            last_idx = len(closed) - 1
            created_fvg = _created_fvg_after_break(closed, last_idx, "bearish")
            displacement = evaluate_displacement(
                closed,
                last_idx,
                direction="bearish",
                structure_level=choch_low.level,
                created_fvg_after_break=created_fvg,
            )
            results.append(
                StructureBreak(
                    symbol=symbol,
                    timeframe=timeframe,
                    break_type="CHOCH",
                    direction="bearish",
                    timestamp=last["time"],
                    broken_level=choch_low.level,
                    close_price=last["close"],
                    source_swing_index=choch_low.index,
                    strength=max(_break_strength(last, choch_low.level), displacement.displacement_factor),
                    displacement_factor=displacement.displacement_factor,
                    has_displacement=displacement.has_displacement,
                    body_ratio=displacement.body_ratio,
                    range_expansion=displacement.range_expansion,
                    created_fvg_after_break=created_fvg,
                    metadata={
                        "trend": "uptrend",
                        "previous_high": swing_highs[-2].level,
                        "swing_time": choch_low.timestamp,
                        "swing_significance": choch_low.significance,
                        "created_fvg_after_break": created_fvg,
                    },
                )
            )
        if downtrend and last["close"] > choch_high.level:
            last_idx = len(closed) - 1
            created_fvg = _created_fvg_after_break(closed, last_idx, "bullish")
            displacement = evaluate_displacement(
                closed,
                last_idx,
                direction="bullish",
                structure_level=choch_high.level,
                created_fvg_after_break=created_fvg,
            )
            results.append(
                StructureBreak(
                    symbol=symbol,
                    timeframe=timeframe,
                    break_type="CHOCH",
                    direction="bullish",
                    timestamp=last["time"],
                    broken_level=choch_high.level,
                    close_price=last["close"],
                    source_swing_index=choch_high.index,
                    strength=max(_break_strength(last, choch_high.level), displacement.displacement_factor),
                    displacement_factor=displacement.displacement_factor,
                    has_displacement=displacement.has_displacement,
                    body_ratio=displacement.body_ratio,
                    range_expansion=displacement.range_expansion,
                    created_fvg_after_break=created_fvg,
                    metadata={
                        "trend": "downtrend",
                        "previous_low": swing_lows[-2].level,
                        "swing_time": choch_high.timestamp,
                        "swing_significance": choch_high.significance,
                        "created_fvg_after_break": created_fvg,
                    },
                )
            )
    return results


def detect_bos(candles: list[Candle], symbol: str, timeframe: str) -> list[StructureBreak]:
    return [item for item in detect_structure_breaks(candles, symbol, timeframe) if item.break_type == "BOS"]


def detect_choch(candles: list[Candle], symbol: str, timeframe: str) -> list[StructureBreak]:
    return [item for item in detect_structure_breaks(candles, symbol, timeframe) if item.break_type == "CHOCH"]


def detect_swings(candles: list[Candle], symbol: str, timeframe: str) -> list[SwingPoint]:
    closed = candles[:-1] if len(candles) > 1 else candles
    highs, lows = collect_swings(closed[-31:], symbol, timeframe)
    latest: list[SwingPoint] = []
    if highs:
        latest.append(highs[-1])
    if lows:
        latest.append(lows[-1])
    return sorted(latest, key=lambda item: item.timestamp)


def _break_strength(candle: Candle, level: float) -> float:
    body = abs(candle["close"] - candle["open"])
    if level == 0:
        return 0.0
    extension = abs(candle["close"] - level) / level
    return min(1.0, body / max(candle["high"] - candle["low"], 1e-9) + extension * 20)


def _created_fvg_after_break(candles: list[Candle], index: int, direction: str) -> bool:
    if index < 2:
        return False
    c0 = candles[index - 2]
    c2 = candles[index]
    if direction == "bullish":
        return float(c0["high"]) < float(c2["low"])
    if direction == "bearish":
        return float(c0["low"]) > float(c2["high"])
    return False


__all__ = [
    "detect_bos",
    "detect_choch",
    "detect_structure_breaks",
    "detect_swings",
]
