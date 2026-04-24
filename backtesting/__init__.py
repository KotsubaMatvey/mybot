from __future__ import annotations

from dataclasses import dataclass

Candle = dict[str, float | int]


@dataclass(slots=True)
class BacktestEvent:
    event_id: str
    model_name: str
    symbol: str
    timeframe: str
    direction: str
    detected_at: int
    status: str
    entry_low: float | None
    entry_high: float | None
    entry_price: float | None
    invalidation: float | None
    risk: float | None
    score: int | None
    reason: str
    components_json: str
    warning: str | None = None
    skipped_reason: str | None = None


@dataclass(slots=True)
class BacktestOutcome:
    event_id: str
    forward_bars: int
    mfe: float | None
    mae: float | None
    mfe_r: float | None
    mae_r: float | None
    hit_0_5r: bool
    hit_1r: bool
    hit_2r: bool
    invalidated: bool
    bars_to_0_5r: int | None
    bars_to_1r: int | None
    bars_to_2r: int | None
    bars_to_invalidation: int | None
    future_high: float | None
    future_low: float | None
    hit_1r_before_invalidation: bool
    hit_2r_before_invalidation: bool


@dataclass(slots=True)
class BacktestResult:
    event: BacktestEvent
    outcome: BacktestOutcome


__all__ = [
    "BacktestEvent",
    "BacktestOutcome",
    "BacktestResult",
    "Candle",
]
