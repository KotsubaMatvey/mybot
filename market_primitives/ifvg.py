from __future__ import annotations

from .common import Candle, InvertedFVG, in_zone
from .fvg import detect_fvg


def detect_ifvg(candles: list[Candle], symbol: str, timeframe: str) -> list[InvertedFVG]:
    if len(candles) < 25:
        return []

    closed = candles[:-1] if len(candles) > 1 else candles
    gaps = detect_fvg(candles, symbol, timeframe)
    results: list[InvertedFVG] = []

    for gap in gaps:
        if not gap.invalidated or gap.invalidated_at is None:
            continue

        invalidation_idx = next((idx for idx, candle in enumerate(closed) if candle["time"] == gap.invalidated_at), None)
        if invalidation_idx is None:
            continue

        retest_at = None
        for candle in closed[invalidation_idx + 1 :]:
            if in_zone(candle, gap.gap_low, gap.gap_high):
                retest_at = candle["time"]
                break
        if retest_at is None:
            continue

        direction = "bullish" if gap.direction == "bearish" else "bearish"
        confidence = 0.55 + min(0.35, (gap.fill_ratio or 0.0) * 0.45)
        results.append(
            InvertedFVG(
                symbol=symbol,
                timeframe=timeframe,
                direction=direction,  # type: ignore[arg-type]
                timestamp=retest_at,
                source_direction=gap.direction,
                zone_low=gap.gap_low,
                zone_high=gap.gap_high,
                invalidated_at=gap.invalidated_at,
                retest_at=retest_at,
                confidence=min(confidence, 0.95),
                metadata={"created_at": gap.created_at},
            )
        )

    return results


__all__ = ["detect_ifvg"]
