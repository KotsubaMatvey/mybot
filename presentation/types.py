from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Mapping

AlertKind = Literal["primitive", "strategy"]


@dataclass(slots=True)
class AlertPayload:
    symbol: str
    timeframe: str
    pattern: str
    alert_kind: AlertKind
    detail: str
    direction: str | None
    timestamp: int
    score: int | None = None
    level: float | None = None
    gap_low: float | None = None
    gap_high: float | None = None
    ob_low: float | None = None
    ob_high: float | None = None
    entry_low: float | None = None
    entry_high: float | None = None
    invalidation: float | None = None
    sweep_level: float | None = None
    structure_level: float | None = None
    context_timeframe: str | None = None
    trade_direction: str | None = None
    status: str | None = None
    reason: str | None = None
    components: Mapping[str, bool] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def type(self) -> str:
        return self.pattern


__all__ = ["AlertPayload", "AlertKind"]
