from __future__ import annotations

from .common import Candle, FVGStatus, FairValueGap, in_zone


def detect_fvg(candles: list[Candle], symbol: str, timeframe: str, scan_back: int = 50) -> list[FairValueGap]:
    if len(candles) < 3:
        return []

    closed = candles[:-1] if len(candles) > 1 else candles
    start = max(2, len(closed) - scan_back)
    results: list[FairValueGap] = []

    for idx in range(start, len(closed)):
        c0 = closed[idx - 2]
        c2 = closed[idx]

        if c0["high"] < c2["low"]:
            gap_low = c0["high"]
            gap_high = c2["low"]
            results.append(_build_gap(closed, idx, symbol, timeframe, "bullish", gap_low, gap_high))
        elif c0["low"] > c2["high"]:
            gap_low = c2["high"]
            gap_high = c0["low"]
            results.append(_build_gap(closed, idx, symbol, timeframe, "bearish", gap_low, gap_high))

    return results


def active_fvgs(candles: list[Candle], symbol: str, timeframe: str) -> list[FairValueGap]:
    return [gap for gap in detect_fvg(candles, symbol, timeframe) if not gap.invalidated]


def _build_gap(
    candles: list[Candle],
    idx: int,
    symbol: str,
    timeframe: str,
    direction: str,
    gap_low: float,
    gap_high: float,
) -> FairValueGap:
    mitigated = False
    invalidated = False
    mitigated_at = None
    invalidated_at = None
    fill_ratio = 0.0
    status: FVGStatus = "open"
    consequent_encroachment = (gap_low + gap_high) / 2

    for candle in candles[idx + 1 :]:
        if in_zone(candle, gap_low, gap_high):
            mitigated = True
            fill_ratio = max(fill_ratio, _gap_fill_ratio(candle, gap_low, gap_high))
            if mitigated_at is None:
                mitigated_at = candle["time"]
            status = "filled" if fill_ratio >= 0.999 else "partially_filled"
        if direction == "bullish" and candle["close"] < gap_low:
            invalidated = True
            invalidated_at = candle["time"]
            status = "invalidated"
            break
        if direction == "bearish" and candle["close"] > gap_high:
            invalidated = True
            invalidated_at = candle["time"]
            status = "invalidated"
            break

    fill_percent = min(fill_ratio, 1.0)
    return FairValueGap(
        symbol=symbol,
        timeframe=timeframe,
        direction=direction,  # type: ignore[arg-type]
        created_at=candles[idx]["time"],
        gap_low=gap_low,
        gap_high=gap_high,
        mitigated=mitigated,
        invalidated=invalidated,
        mitigated_at=mitigated_at,
        invalidated_at=invalidated_at,
        fill_ratio=fill_percent,
        status=status,
        fill_percent=round(fill_percent * 100, 4),
        consequent_encroachment=consequent_encroachment,
        metadata={
            "anchor_index": idx,
            "start_time": candles[idx - 2]["time"],
            "status": status,
            "fill_percent": round(fill_percent * 100, 4),
            "consequent_encroachment": consequent_encroachment,
        },
    )


def _gap_fill_ratio(candle: Candle, gap_low: float, gap_high: float) -> float:
    gap_size = max(gap_high - gap_low, 1e-9)
    overlap = max(0.0, min(candle["high"], gap_high) - max(candle["low"], gap_low))
    return overlap / gap_size


__all__ = ["active_fvgs", "detect_fvg"]
