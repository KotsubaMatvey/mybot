from __future__ import annotations

from .common import Candle, InvertedFVG, in_zone
from .displacement import evaluate_displacement
from .fvg import detect_fvg


def detect_ifvg(candles: list[Candle], symbol: str, timeframe: str) -> list[InvertedFVG]:
    if len(candles) < 5:
        return []

    closed = candles[:-1] if len(candles) > 1 else candles
    gaps = detect_fvg(candles, symbol, timeframe)
    results: list[InvertedFVG] = []

    for gap in gaps:
        if not gap.invalidated or gap.invalidated_at is None:
            continue

        breach_idx = next((idx for idx, candle in enumerate(closed) if candle["time"] == gap.invalidated_at), None)
        if breach_idx is None:
            continue
        breach_candle = closed[breach_idx]
        if gap.direction == "bearish":
            body_breached = float(breach_candle["close"]) > gap.gap_high
            direction = "bullish"
        else:
            body_breached = float(breach_candle["close"]) < gap.gap_low
            direction = "bearish"
        if not body_breached:
            continue

        displacement = evaluate_displacement(
            closed,
            breach_idx,
            direction=direction,
            structure_level=gap.gap_high if direction == "bullish" else gap.gap_low,
        )
        if not displacement.has_displacement:
            continue

        retest_at = None
        for candle in closed[breach_idx + 1 :]:
            if in_zone(candle, gap.gap_low, gap.gap_high):
                retest_at = candle["time"]
                break

        mean_threshold = (gap.gap_low + gap.gap_high) / 2
        confidence = 0.55 + min(0.25, displacement.displacement_factor * 0.25) + min(0.15, (gap.fill_ratio or 0.0) * 0.2)
        results.append(
            InvertedFVG(
                symbol=symbol,
                timeframe=timeframe,
                direction=direction,  # type: ignore[arg-type]
                timestamp=retest_at or gap.invalidated_at,
                source_direction=gap.direction,
                zone_low=gap.gap_low,
                zone_high=gap.gap_high,
                invalidated_at=gap.invalidated_at,
                retest_at=retest_at,
                confidence=min(confidence, 0.95),
                source_fvg_time=gap.created_at,
                breach_displacement_factor=displacement.displacement_factor,
                mean_threshold=mean_threshold,
                metadata={
                    "created_at": gap.created_at,
                    "source_fvg_time": gap.created_at,
                    "fill_ratio": gap.fill_ratio,
                    "fill_percent": gap.fill_percent,
                    "breach_time": gap.invalidated_at,
                    "breach_displacement_factor": displacement.displacement_factor,
                    "body_ratio": displacement.body_ratio,
                    "range_expansion": displacement.range_expansion,
                    "mean_threshold": mean_threshold,
                },
            )
        )

    return results


__all__ = ["detect_ifvg"]
