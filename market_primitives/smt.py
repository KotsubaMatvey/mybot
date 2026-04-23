from __future__ import annotations

from .common import Candle, SMTDivergence, collect_swings


def detect_smt(
    candles_a: list[Candle],
    candles_b: list[Candle],
    symbol_a: str,
    symbol_b: str,
    timeframe: str,
) -> list[SMTDivergence]:
    if len(candles_a) < 10 or len(candles_b) < 10:
        return []

    candles_b_by_time = {c["time"]: c for c in candles_b[-41:-1]}
    aligned_a: list[Candle] = []
    aligned_b: list[Candle] = []
    for candle in candles_a[-41:-1]:
        other = candles_b_by_time.get(candle["time"])
        if other is None:
            continue
        aligned_a.append(candle)
        aligned_b.append(other)

    if len(aligned_a) < 10:
        return []

    swing_highs, swing_lows = collect_swings(aligned_a, symbol_a, timeframe, left=1, right=1)
    results: list[SMTDivergence] = []

    if len(swing_highs) >= 2:
        first, second = swing_highs[-2], swing_highs[-1]
        if second.level > first.level:
            other_first = aligned_b[first.index]["high"]
            other_second = aligned_b[second.index]["high"]
            if other_second < other_first and len(aligned_a) - 1 - second.index <= 8:
                strength = abs(second.level - first.level) / max(second.level, 1e-9)
                results.append(
                    SMTDivergence(
                        symbol=symbol_a,
                        timeframe=timeframe,
                        direction="bearish",
                        timestamp=second.timestamp,
                        primary_level=second.level,
                        secondary_symbol=symbol_b,
                        secondary_level=other_second,
                        strength=strength,
                    )
                )

    if len(swing_lows) >= 2:
        first, second = swing_lows[-2], swing_lows[-1]
        if second.level < first.level:
            other_first = aligned_b[first.index]["low"]
            other_second = aligned_b[second.index]["low"]
            if other_second > other_first and len(aligned_a) - 1 - second.index <= 8:
                strength = abs(second.level - first.level) / max(abs(second.level), 1e-9)
                results.append(
                    SMTDivergence(
                        symbol=symbol_a,
                        timeframe=timeframe,
                        direction="bullish",
                        timestamp=second.timestamp,
                        primary_level=second.level,
                        secondary_symbol=symbol_b,
                        secondary_level=other_second,
                        strength=strength,
                    )
                )
    return results


__all__ = ["detect_smt"]
