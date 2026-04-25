from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from strategies.setup_utils import current_price, timeframe_to_ms
from strategies.types import PrimitiveSnapshot

HTFDirection = Literal["bullish", "bearish", "neutral"]
HTFLocation = Literal["discount", "premium", "equilibrium", "unknown"]


@dataclass(slots=True)
class HTFBias:
    direction: HTFDirection
    confidence: float
    reason: str


@dataclass(slots=True)
class HTFZone:
    zone_type: str
    direction: HTFDirection
    low: float | None
    high: float | None
    origin_time: int | None
    strength: float
    reason: str


@dataclass(slots=True)
class HTFDealingRange:
    range_low: float | None
    range_high: float | None
    equilibrium: float | None
    location: HTFLocation


@dataclass(slots=True)
class HTFObjective:
    direction: Literal["up", "down", "none"]
    target_level: float | None
    target_type: str
    reason: str


@dataclass(slots=True)
class HTFContext:
    timeframe: str
    bias: HTFBias
    zone: HTFZone
    dealing_range: HTFDealingRange
    objective: HTFObjective
    inside_zone: bool
    approaching_zone: bool
    allows_long: bool
    allows_short: bool
    score_modifier: float
    reason: str


def build_htf_context(snapshot: PrimitiveSnapshot, current_price_value: float | None = None) -> HTFContext:
    price = current_price_value if current_price_value is not None else current_price(snapshot)
    dealing_range = _build_dealing_range(snapshot, price)
    zone = _select_active_zone(snapshot, price)
    objective = _build_objective(snapshot, price)
    inside_zone = _current_candle_inside_zone(snapshot, zone) or _price_inside_zone(price, zone)
    approaching_zone = _price_approaching_zone(price, zone)
    bias_score, bias_reason = _bias_score(snapshot, price, dealing_range, zone, objective, inside_zone)
    if bias_score >= 0.6:
        direction: HTFDirection = "bullish"
    elif bias_score <= -0.6:
        direction = "bearish"
    else:
        direction = "neutral"
    bias = HTFBias(direction=direction, confidence=min(1.0, abs(bias_score) / 2.0), reason=bias_reason)

    strong_bullish_zone = zone.direction == "bullish" and zone.strength >= 0.65 and (inside_zone or approaching_zone)
    strong_bearish_zone = zone.direction == "bearish" and zone.strength >= 0.65 and (inside_zone or approaching_zone)
    long_location = dealing_range.location == "discount"
    short_location = dealing_range.location == "premium"
    long_poi = zone.direction == "bullish" and (inside_zone or approaching_zone)
    short_poi = zone.direction == "bearish" and (inside_zone or approaching_zone)
    long_objective = objective.direction == "up"
    short_objective = objective.direction == "down"
    allows_long = bias.direction == "bullish" and long_objective and (long_poi or long_location)
    allows_short = bias.direction == "bearish" and short_objective and (short_poi or short_location)
    if bias.direction == "neutral":
        allows_long = strong_bullish_zone and long_objective
        allows_short = strong_bearish_zone and short_objective

    score_modifier = 0.0
    if bias.direction == "neutral":
        score_modifier -= 0.3
    if zone.zone_type != "None" and inside_zone:
        score_modifier += 0.1
    elif zone.zone_type != "None" and approaching_zone:
        score_modifier += 0.05
    else:
        score_modifier -= 0.2

    reason = (
        f"HTF {bias.direction} {dealing_range.location} {zone.direction} {zone.zone_type}; "
        f"{objective.target_type} {objective.direction}"
    )
    return HTFContext(
        timeframe=snapshot.timeframe,
        bias=bias,
        zone=zone,
        dealing_range=dealing_range,
        objective=objective,
        inside_zone=inside_zone,
        approaching_zone=approaching_zone,
        allows_long=allows_long,
        allows_short=allows_short,
        score_modifier=score_modifier,
        reason=reason,
    )


def htf_allows_side(context: HTFContext | None, side: str, htf_mode: str) -> bool:
    mode = htf_mode.lower()
    if mode == "off":
        return True
    if context is None:
        return mode == "soft"
    if mode == "strict":
        return context.allows_long if side == "long" else context.allows_short
    if mode == "soft":
        direction = "bullish" if side == "long" else "bearish"
        if context.bias.direction == direction:
            return True
        if context.bias.direction == "neutral":
            return context.zone.direction == direction and (context.inside_zone or context.approaching_zone)
        return False
    return False


def htf_score_modifier(context: HTFContext | None, side: str, htf_mode: str) -> float:
    mode = htf_mode.lower()
    if mode == "off":
        return 0.0
    if context is None:
        return -0.8 if mode == "soft" else -1.0
    modifier = context.score_modifier
    direction = "bullish" if side == "long" else "bearish"
    if context.bias.direction == direction:
        modifier += 0.25
    elif context.bias.direction == "neutral":
        modifier -= 0.3
    else:
        modifier -= 1.0
    if context.inside_zone and context.zone.direction == direction:
        modifier += 0.2
    elif context.approaching_zone and context.zone.direction == direction:
        modifier += 0.1
    if side == "long" and context.dealing_range.location == "discount":
        modifier += 0.15
    if side == "short" and context.dealing_range.location == "premium":
        modifier += 0.15
    if _objective_aligns(context, side):
        modifier += 0.1
    elif context.objective.direction == "none":
        modifier -= 0.2
    else:
        modifier -= 0.5
    if not context.inside_zone and not context.approaching_zone:
        modifier -= 0.4
    return modifier


def htf_metadata(context: HTFContext | None) -> dict[str, object]:
    if context is None:
        return {
            "htf_bias": "none",
            "htf_confidence": None,
            "htf_zone_type": "None",
            "htf_zone_low": None,
            "htf_zone_high": None,
            "htf_location": "unknown",
            "htf_allows_long": False,
            "htf_allows_short": False,
            "htf_objective_type": "none",
            "htf_objective_level": None,
            "htf_reason": "no HTF context",
        }
    return {
        "htf_bias": context.bias.direction,
        "htf_confidence": round(context.bias.confidence, 4),
        "htf_zone_type": context.zone.zone_type,
        "htf_zone_low": context.zone.low,
        "htf_zone_high": context.zone.high,
        "htf_location": context.dealing_range.location,
        "htf_allows_long": context.allows_long,
        "htf_allows_short": context.allows_short,
        "htf_objective_type": context.objective.target_type,
        "htf_objective_level": context.objective.target_level,
        "htf_reason": context.reason,
    }


def _build_dealing_range(snapshot: PrimitiveSnapshot, price: float | None) -> HTFDealingRange:
    significant = [item for item in snapshot.swings if item.significance in {"intermediate", "long"}]
    highs = sorted(significant or snapshot.swings, key=lambda item: item.timestamp)
    last_high = next((item for item in reversed(highs) if item.direction == "high"), None)
    last_low = next((item for item in reversed(highs) if item.direction == "low"), None)
    if last_high is None or last_low is None:
        return HTFDealingRange(None, None, None, "unknown")
    range_high = max(last_high.level, last_low.level)
    range_low = min(last_high.level, last_low.level)
    if range_high <= range_low:
        return HTFDealingRange(range_low, range_high, None, "unknown")
    equilibrium = (range_high + range_low) / 2
    if price is None:
        location: HTFLocation = "unknown"
    else:
        buffer = max((range_high - range_low) * 0.05, equilibrium * 0.001)
        if price < equilibrium - buffer:
            location = "discount"
        elif price > equilibrium + buffer:
            location = "premium"
        else:
            location = "equilibrium"
    return HTFDealingRange(range_low, range_high, equilibrium, location)


def _select_active_zone(snapshot: PrimitiveSnapshot, price: float | None) -> HTFZone:
    candidates: list[HTFZone] = []
    current_ts = int(snapshot.candles[-1]["time"]) if snapshot.candles else None
    for item in snapshot.ifvgs:
        candidates.append(HTFZone("IFVG", item.direction, item.zone_low, item.zone_high, item.invalidated_at, item.confidence, "active IFVG"))
    for item in snapshot.breaker_blocks:
        candidates.append(HTFZone("Breaker", item.direction, item.zone_low, item.zone_high, item.trigger_time, 0.72 if item.retested else 0.62, "breaker block"))
    for item in snapshot.order_blocks:
        if not item.invalidated:
            candidates.append(HTFZone("OB", item.direction, item.zone_low, item.zone_high, item.origin_time, 0.66 if item.mitigated else 0.58, "order block"))
    for item in snapshot.fvgs:
        if not item.invalidated:
            candidates.append(HTFZone("FVG", item.direction, item.gap_low, item.gap_high, item.created_at, 0.55 if item.mitigated else 0.5, "fair value gap"))
    for item in snapshot.pd_zones:
        direction: HTFDirection = "bullish" if "discount" in item.kind else "bearish" if "premium" in item.kind else "neutral"
        candidates.append(HTFZone("PD", direction, item.zone_low, item.zone_high, item.timestamp, 0.45, item.kind))
    for item in snapshot.equal_highs:
        candidates.append(HTFZone("Liquidity", "bearish", item.level, item.level, item.timestamp, 0.35, "equal highs"))
    for item in snapshot.equal_lows:
        candidates.append(HTFZone("Liquidity", "bullish", item.level, item.level, item.timestamp, 0.35, "equal lows"))
    if not candidates:
        return HTFZone("None", "neutral", None, None, None, 0.0, "no active HTF zone")
    candidates = [item for item in candidates if not _zone_is_stale(item, snapshot.timeframe, current_ts)]
    if not candidates:
        return HTFZone("None", "neutral", None, None, None, 0.0, "no fresh HTF zone")

    ordered = sorted(
        candidates,
        key=lambda item: (
            _zone_distance(price, item),
            -item.strength,
            -int(item.origin_time or 0),
        ),
    )
    return ordered[0]


def _build_objective(snapshot: PrimitiveSnapshot, price: float | None) -> HTFObjective:
    if price is None:
        return HTFObjective("none", None, "none", "no current price")
    swings = [item for item in snapshot.swings if item.significance in {"intermediate", "long"}] or snapshot.swings
    highs = [item for item in swings if item.direction == "high" and item.level > price]
    lows = [item for item in swings if item.direction == "low" and item.level < price]
    eqh = [item for item in snapshot.equal_highs if item.level > price]
    eql = [item for item in snapshot.equal_lows if item.level < price]
    if eqh:
        target = min(eqh, key=lambda item: item.level)
        return HTFObjective("up", target.level, "equal_highs", "nearest equal highs above")
    if eql:
        target = max(eql, key=lambda item: item.level)
        return HTFObjective("down", target.level, "equal_lows", "nearest equal lows below")
    if highs:
        target = min(highs, key=lambda item: item.level)
        return HTFObjective("up", target.level, "swing_high", "nearest swing high above")
    if lows:
        target = max(lows, key=lambda item: item.level)
        return HTFObjective("down", target.level, "swing_low", "nearest swing low below")
    return HTFObjective("none", None, "none", "no clear external liquidity")


def _bias_score(
    snapshot: PrimitiveSnapshot,
    price: float | None,
    dealing_range: HTFDealingRange,
    zone: HTFZone,
    objective: HTFObjective,
    inside_zone: bool,
) -> tuple[float, str]:
    score = 0.0
    reasons: list[str] = []
    recent_structures = sorted(snapshot.structure_breaks, key=lambda item: item.timestamp, reverse=True)
    structure = next(
        (item for item in recent_structures if item.has_displacement or item.strength >= 0.35),
        recent_structures[0] if recent_structures else None,
    )
    structure_direction: str | None = None
    if structure is not None:
        structure_direction = structure.direction
        if structure.direction == "bullish":
            score += 1.0
        else:
            score -= 1.0
        reasons.append(f"last structure {structure.direction} {structure.break_type}")
    if dealing_range.location == "discount":
        score += 0.35
        reasons.append("discount")
    elif dealing_range.location == "premium":
        score -= 0.35
        reasons.append("premium")
    if inside_zone and zone.direction == "bullish":
        score += 0.5
        reasons.append(f"inside bullish {zone.zone_type}")
    elif inside_zone and zone.direction == "bearish":
        score -= 0.5
        reasons.append(f"inside bearish {zone.zone_type}")
    if objective.direction == "up" and (structure_direction == "bullish" or (inside_zone and zone.direction == "bullish")):
        score += 0.25
        reasons.append("objective above")
    elif objective.direction == "down" and (structure_direction == "bearish" or (inside_zone and zone.direction == "bearish")):
        score -= 0.25
        reasons.append("objective below")
    return score, ", ".join(reasons) if reasons else "no decisive HTF inputs"


def _price_inside_zone(price: float | None, zone: HTFZone) -> bool:
    if price is None or zone.low is None or zone.high is None:
        return False
    low, high = sorted((zone.low, zone.high))
    return low <= price <= high


def _current_candle_inside_zone(snapshot: PrimitiveSnapshot, zone: HTFZone) -> bool:
    if not snapshot.candles or zone.low is None or zone.high is None:
        return False
    candle = snapshot.candles[-1]
    low, high = sorted((zone.low, zone.high))
    return float(candle["low"]) <= high and float(candle["high"]) >= low


def _price_approaching_zone(price: float | None, zone: HTFZone) -> bool:
    if price is None or zone.low is None or zone.high is None:
        return False
    low, high = sorted((zone.low, zone.high))
    width = max(high - low, price * 0.001, 1e-9)
    distance = 0.0 if low <= price <= high else min(abs(price - low), abs(price - high))
    return distance <= max(width * 1.5, price * 0.0025)


def _zone_distance(price: float | None, zone: HTFZone) -> float:
    if price is None or zone.low is None or zone.high is None:
        return float("inf")
    low, high = sorted((zone.low, zone.high))
    if low <= price <= high:
        return 0.0
    return min(abs(price - low), abs(price - high)) / max(price, 1e-9)


def _objective_aligns(context: HTFContext, side: str) -> bool:
    return (side == "long" and context.objective.direction == "up") or (
        side == "short" and context.objective.direction == "down"
    )


def _zone_is_stale(zone: HTFZone, timeframe: str, current_ts: int | None) -> bool:
    if current_ts is None or zone.origin_time is None:
        return False
    tf_ms = timeframe_to_ms(timeframe)
    if tf_ms is None:
        return False
    return current_ts - zone.origin_time > tf_ms * 120


__all__ = [
    "HTFBias",
    "HTFContext",
    "HTFDealingRange",
    "HTFObjective",
    "HTFZone",
    "build_htf_context",
    "htf_allows_side",
    "htf_metadata",
    "htf_score_modifier",
]
