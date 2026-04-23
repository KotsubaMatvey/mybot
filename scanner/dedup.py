from __future__ import annotations

from collections import OrderedDict

from presentation.types import AlertPayload

_sent: OrderedDict[tuple[object, ...], bool] = OrderedDict()
_MAX_KEYS = 5000


def should_skip_duplicate(alert: AlertPayload) -> bool:
    key = _dedup_key(alert)
    if key in _sent:
        return True
    _sent[key] = True
    while len(_sent) > _MAX_KEYS:
        _sent.popitem(last=False)
    return False


def _dedup_key(alert: AlertPayload) -> tuple[object, ...]:
    zone_key = (
        _rounded(alert.entry_low),
        _rounded(alert.entry_high),
        _rounded(alert.gap_low),
        _rounded(alert.gap_high),
        _rounded(alert.ob_low),
        _rounded(alert.ob_high),
        _rounded(alert.level),
        _rounded(alert.invalidation),
        _rounded(alert.sweep_level),
        _rounded(alert.structure_level),
    )
    return (
        alert.symbol,
        alert.timeframe,
        alert.pattern,
        alert.alert_kind,
        alert.trade_direction,
        alert.direction,
        alert.timestamp,
        zone_key,
        alert.context_timeframe,
        alert.status,
    )


def _rounded(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 6)


__all__ = ["should_skip_duplicate"]
