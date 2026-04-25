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
    htf_bias: str | None = None
    htf_confidence: float | None = None
    htf_zone_type: str | None = None
    htf_zone_low: float | None = None
    htf_zone_high: float | None = None
    htf_location: str | None = None
    htf_allows_long: bool | None = None
    htf_allows_short: bool | None = None
    htf_objective_type: str | None = None
    htf_objective_level: float | None = None
    displacement_factor: float | None = None
    has_displacement: bool | None = None
    swing_significance: str | None = None
    fvg_status: str | None = None
    fvg_fill_percent: float | None = None
    source_fvg_direction: str | None = None
    breach_time: int | None = None
    breach_displacement_factor: float | None = None
    ifvg_mean_threshold: float | None = None
    source_zone_type: str | None = None
    source_zone_time: int | None = None
    fill_percent: float | None = None
    fill_mode: str | None = None
    ltf_mss_time: int | None = None


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
