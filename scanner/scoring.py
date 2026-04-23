from __future__ import annotations

from strategies.types import PrimitiveSnapshot

_PATTERN_WEIGHTS = {
    "CHoCH": 1.0,
    "BOS": 0.9,
    "SMT": 0.9,
    "IFVG": 0.8,
    "Breaker": 0.8,
    "OB": 0.7,
    "EQH": 0.7,
    "EQL": 0.7,
    "Liquidity": 0.8,
    "KL": 0.6,
    "FVG": 0.6,
    "Sweeps": 0.6,
    "Volume": 0.4,
    "VP": 0.4,
    "PD": 0.4,
    "Swings": 0.3,
}
_TF_WEIGHT = {"1m": 0.4, "5m": 0.5, "15m": 0.6, "30m": 0.7, "1h": 0.8, "4h": 0.9, "1d": 1.0}


def score_primitive_bundle(pattern_names: dict[str, str], timeframe: str, snapshot: PrimitiveSnapshot | None) -> int:
    if not pattern_names:
        return 1
    raw = sum(_PATTERN_WEIGHTS.get(name, 0.3) for name in pattern_names)
    tf_weight = _TF_WEIGHT.get(timeframe, 0.6)
    agreement = _directional_agreement(snapshot)
    confidence = raw * tf_weight * agreement
    if confidence < 0.4:
        return 1
    if confidence < 0.8:
        return 2
    if confidence < 1.3:
        return 3
    if confidence < 2.0:
        return 4
    return 5


def _directional_agreement(snapshot: PrimitiveSnapshot | None) -> float:
    if snapshot is None:
        return 0.75
    directions = [item.direction for item in snapshot.structure_breaks]
    directions += [item.direction for item in snapshot.sweeps]
    directions += [item.direction for item in snapshot.raids]
    if not directions:
        return 0.75
    bullish = sum(1 for item in directions if item == "bullish")
    bearish = sum(1 for item in directions if item == "bearish")
    total = bullish + bearish
    if total == 0:
        return 0.75
    return max(0.5, max(bullish, bearish) / total)


__all__ = ["score_primitive_bundle"]
