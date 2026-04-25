from __future__ import annotations

from dataclasses import dataclass

from config import DISPLACEMENT_FVG_BONUS, DISPLACEMENT_MIN_BODY_RATIO, DISPLACEMENT_MIN_RANGE_EXPANSION

from .common import Candle, average_range, candle_range


@dataclass(slots=True)
class DisplacementQuality:
    body_ratio: float
    range_expansion: float
    displacement_factor: float
    has_displacement: bool


def evaluate_displacement(
    candles: list[Candle],
    index: int,
    *,
    direction: str,
    structure_level: float | None = None,
    created_fvg_after_break: bool = False,
    lookback: int = 20,
) -> DisplacementQuality:
    if index < 0 or index >= len(candles):
        return DisplacementQuality(0.0, 0.0, 0.0, False)

    candle = candles[index]
    current_range = candle_range(candle)
    body = abs(float(candle["close"]) - float(candle["open"]))
    body_ratio = body / max(current_range, 1e-9)
    start = max(0, index - lookback)
    avg_range = average_range(candles[start:index])
    range_expansion = current_range / max(avg_range, 1e-9) if avg_range else 1.0
    close_beyond = True
    if structure_level is not None:
        if direction == "bullish":
            close_beyond = float(candle["close"]) > structure_level
        elif direction == "bearish":
            close_beyond = float(candle["close"]) < structure_level

    factor = min(1.0, body_ratio * 0.55 + min(range_expansion / 2.0, 1.0) * 0.45)
    if created_fvg_after_break:
        factor = min(1.0, factor + DISPLACEMENT_FVG_BONUS)
    has_displacement = (
        body_ratio >= DISPLACEMENT_MIN_BODY_RATIO
        and range_expansion >= DISPLACEMENT_MIN_RANGE_EXPANSION
        and close_beyond
    )
    return DisplacementQuality(
        body_ratio=body_ratio,
        range_expansion=range_expansion,
        displacement_factor=factor,
        has_displacement=has_displacement,
    )


__all__ = ["DisplacementQuality", "evaluate_displacement"]
