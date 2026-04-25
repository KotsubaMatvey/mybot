from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal, TypedDict

from market_primitives.common import (
    BreakerBlock,
    EqualLiquidityLevel,
    FairValueGap,
    InvertedFVG,
    KeyLevel,
    LiquiditySweep,
    OrderBlock,
    PDZone,
    SMTDivergence,
    StructureBreak,
    SwingPoint,
    VolumeSignal,
)

if TYPE_CHECKING:
    from strategies.htf_context import HTFContext

SetupDirection = Literal["long", "short"]
SetupStatus = Literal["watching", "confirmed", "triggered"]


class SetupComponents(TypedDict):
    sweep_detected: bool
    structure_shift_detected: bool
    fvg_detected: bool
    inversion_detected: bool
    ltf_refinement_detected: bool


@dataclass(slots=True)
class PrimitiveSnapshot:
    symbol: str
    timeframe: str
    candles: list[dict[str, float | int]]
    swings: list[SwingPoint] = field(default_factory=list)
    sweeps: list[LiquiditySweep] = field(default_factory=list)
    raids: list[LiquiditySweep] = field(default_factory=list)
    structure_breaks: list[StructureBreak] = field(default_factory=list)
    fvgs: list[FairValueGap] = field(default_factory=list)
    ifvgs: list[InvertedFVG] = field(default_factory=list)
    order_blocks: list[OrderBlock] = field(default_factory=list)
    breaker_blocks: list[BreakerBlock] = field(default_factory=list)
    equal_highs: list[EqualLiquidityLevel] = field(default_factory=list)
    equal_lows: list[EqualLiquidityLevel] = field(default_factory=list)
    key_levels: list[KeyLevel] = field(default_factory=list)
    volume_signals: list[VolumeSignal] = field(default_factory=list)
    pd_zones: list[PDZone] = field(default_factory=list)
    smt_divergences: list[SMTDivergence] = field(default_factory=list)


@dataclass(slots=True)
class EntrySetup:
    model_name: str
    direction: SetupDirection
    symbol: str
    timeframe: str
    status: SetupStatus
    entry_low: float
    entry_high: float
    invalidation: float
    target_hint: float | None
    sweep_level: float | None
    structure_level: float | None
    context_timeframe: str | None
    score: int
    reason: str
    components: SetupComponents
    timestamp: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class StrategyContext:
    primary: PrimitiveSnapshot
    higher_timeframe: PrimitiveSnapshot | None = None
    lower_timeframe: PrimitiveSnapshot | None = None
    htf_context: "HTFContext | None" = None
    htf_timeframe: str | None = None
    execution_timeframe: str | None = None
    htf_mode: str = "strict"
    require_displacement: bool = True
    model3_fill_threshold: float = 0.5


def default_components() -> SetupComponents:
    return {
        "sweep_detected": False,
        "structure_shift_detected": False,
        "fvg_detected": False,
        "inversion_detected": False,
        "ltf_refinement_detected": False,
    }


__all__ = [
    "EntrySetup",
    "PrimitiveSnapshot",
    "SetupComponents",
    "StrategyContext",
    "default_components",
]
