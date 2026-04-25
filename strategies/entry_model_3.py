from __future__ import annotations

from dataclasses import dataclass

from market_primitives.common import FairValueGap, OrderBlock, StructureBreak

from config import MIN_RISK_BPS, MODEL3_FILL_THRESHOLD
from .htf_context import htf_allows_side, htf_metadata, htf_score_modifier
from .scoring import score_model_3
from .setup_utils import classify_zone_status, current_price, primitive_direction
from .types import EntrySetup, PrimitiveSnapshot, StrategyContext, default_components


@dataclass(slots=True)
class _SourceZone:
    zone_type: str
    direction: str
    low: float
    high: float
    origin_time: int
    fill_ratio: float
    fill_mode: str
    displacement_factor: float
    has_displacement: bool
    metadata: dict[str, object]


def detect_entry_model_3(context: StrategyContext) -> list[EntrySetup]:
    if context.htf_mode != "off" and context.htf_context is None:
        return []
    if context.higher_timeframe is None or context.lower_timeframe is None:
        return []

    results: list[EntrySetup] = []
    results.extend(_detect_direction(context, side="long"))
    results.extend(_detect_direction(context, side="short"))
    return sorted(results, key=lambda item: item.timestamp, reverse=True)


def _detect_direction(context: StrategyContext, side: str) -> list[EntrySetup]:
    htf = context.higher_timeframe
    ltf = context.lower_timeframe
    if htf is None or ltf is None:
        return []
    if not htf_allows_side(context.htf_context, side, context.htf_mode):
        return []

    direction = primitive_direction(side)  # type: ignore[arg-type]
    if context.htf_context is not None and context.htf_context.bias.direction not in {direction, "neutral"}:
        return []
    if context.htf_context is not None and context.htf_context.bias.direction == "neutral":
        return []

    primary_structure = next(
        (
            item
            for item in sorted(context.primary.structure_breaks, key=lambda item: item.timestamp, reverse=True)
            if item.direction == direction and (item.has_displacement or item.created_fvg_after_break or not context.require_displacement)
        ),
        None,
    )
    if primary_structure is None:
        return []

    source_zone = _select_source_zone(context.primary, direction, primary_structure, context.model3_fill_threshold)
    if source_zone is None:
        return []

    ltf_structure = next(
        (
            item
            for item in sorted(ltf.structure_breaks, key=lambda item: item.timestamp, reverse=True)
            if item.direction == direction
            and item.timestamp > source_zone.origin_time
            and item.strength >= 0.2
            and (item.has_displacement or item.created_fvg_after_break or not context.require_displacement)
        ),
        None,
    )
    if ltf_structure is None:
        return []

    ltf_fvg = next(
        (
            item
            for item in sorted(ltf.fvgs, key=lambda item: item.created_at, reverse=True)
            if item.direction == direction and item.created_at > ltf_structure.timestamp and not item.invalidated
        ),
        None,
    )

    setup = _build_setup(context, htf, ltf, side, primary_structure, source_zone, ltf_structure, ltf_fvg)
    return [setup] if setup is not None else []


def _build_setup(
    context: StrategyContext,
    htf: PrimitiveSnapshot,
    ltf: PrimitiveSnapshot,
    side: str,
    primary_structure: StructureBreak,
    source_zone: _SourceZone,
    ltf_structure: StructureBreak,
    ltf_fvg: FairValueGap | None,
) -> EntrySetup | None:
    entry_low = ltf_fvg.gap_low if ltf_fvg is not None else source_zone.low
    entry_high = ltf_fvg.gap_high if ltf_fvg is not None else source_zone.high
    armed_time = max(ltf_structure.timestamp, ltf_fvg.created_at if ltf_fvg is not None else source_zone.origin_time)
    status_info = classify_zone_status(
        ltf,
        zone_low=entry_low,
        zone_high=entry_high,
        armed_time=armed_time,
    )
    if status_info is None:
        return None
    status, status_time = status_info

    closed_ltf = ltf.candles[:-1] if len(ltf.candles) > 1 else ltf.candles
    recent_slice = closed_ltf[-5:] if len(closed_ltf) >= 5 else closed_ltf
    if not recent_slice:
        return None
    invalidation = (
        min(candle["low"] for candle in recent_slice)
        if side == "long"
        else max(candle["high"] for candle in recent_slice)
    )
    price = current_price(ltf)
    entry_mid = (entry_low + entry_high) / 2
    risk = abs(entry_mid - invalidation)
    risk_floor = (price or entry_mid) * (MIN_RISK_BPS / 10_000)
    if risk < risk_floor:
        return None
    zone_width = max(abs(entry_high - entry_low), risk_floor)
    if price is not None:
        distance = 0.0 if entry_low <= price <= entry_high else min(abs(price - entry_low), abs(price - entry_high))
        if distance > max(zone_width * 2.0, price * 0.004):
            return None

    score = score_model_3(
        htf_alignment=0.8 if primary_structure.break_type in {"BOS", "CHOCH", "MSS"} else 0.5,
        ltf_strength=min(1.0, ltf_structure.strength + 0.15),
        entry_low=entry_low,
        entry_high=entry_high,
        invalidation=invalidation,
        missed_primary_penalty=0.3,
        htf_modifier=htf_score_modifier(context.htf_context, side, context.htf_mode),
        fill_quality=source_zone.fill_ratio,
        has_displacement=primary_structure.has_displacement or ltf_structure.has_displacement,
    )

    components = default_components()
    components["structure_shift_detected"] = True
    components["fvg_detected"] = True
    components["ltf_refinement_detected"] = True

    return EntrySetup(
        model_name="Entry Model 3",
        direction="long" if side == "long" else "short",
        symbol=context.primary.symbol,
        timeframe=ltf.timeframe,
        status=status,
        entry_low=entry_low,
        entry_high=entry_high,
        invalidation=invalidation,
        target_hint=_target_hint(side, entry_low, entry_high, invalidation),
        sweep_level=None,
        structure_level=ltf_structure.broken_level,
        context_timeframe=htf.timeframe,
        score=score,
        reason=_reason(context, side, source_zone, ltf_fvg),
        components=components,
        timestamp=max(status_time, primary_structure.timestamp, ltf_structure.timestamp, armed_time),
        metadata={
            "primary_timeframe": context.primary.timeframe,
            "htf_timeframe": htf.timeframe,
            "ltf_timeframe": ltf.timeframe,
            "primary_structure_time": primary_structure.timestamp,
            "primary_structure_type": primary_structure.break_type,
            "displacement_factor": round(max(primary_structure.displacement_factor, ltf_structure.displacement_factor), 6),
            "has_displacement": primary_structure.has_displacement or ltf_structure.has_displacement,
            "ltf_structure_type": ltf_structure.break_type,
            "ltf_mss_time": ltf_structure.timestamp,
            "source_zone_type": source_zone.zone_type,
            "source_zone_time": source_zone.origin_time,
            "fill_percent": round(source_zone.fill_ratio * 100, 4),
            "fvg_fill_percent": round(source_zone.fill_ratio * 100, 4),
            "fill_mode": source_zone.fill_mode,
            "ltf_entry_zone_low": entry_low,
            "ltf_entry_zone_high": entry_high,
            **source_zone.metadata,
            **htf_metadata(context.htf_context),
        },
    )


def _select_source_zone(
    snapshot: PrimitiveSnapshot,
    direction: str,
    structure: StructureBreak,
    fill_threshold: float,
) -> _SourceZone | None:
    zones: list[_SourceZone] = []
    for fvg in snapshot.fvgs:
        if fvg.direction != direction or fvg.invalidated or fvg.created_at < structure.timestamp:
            continue
        if fvg.fill_ratio < fill_threshold:
            continue
        zones.append(
            _SourceZone(
                zone_type="FVG",
                direction=fvg.direction,
                low=fvg.gap_low,
                high=fvg.gap_high,
                origin_time=fvg.created_at,
                fill_ratio=fvg.fill_ratio,
                fill_mode=_fill_mode(fill_threshold),
                displacement_factor=structure.displacement_factor,
                has_displacement=structure.has_displacement,
                metadata={
                    "source_fvg_status": fvg.status,
                    "source_fvg_fill_percent": fvg.fill_percent,
                    "ote_retracement_level": None,
                },
            )
        )
    for block in snapshot.order_blocks:
        if block.direction != direction or block.invalidated or block.origin_time < structure.timestamp:
            continue
        if not block.mitigated:
            continue
        zones.append(
            _SourceZone(
                zone_type="OB",
                direction=block.direction,
                low=block.zone_low,
                high=block.zone_high,
                origin_time=block.origin_time,
                fill_ratio=1.0,
                fill_mode="ob_retest",
                displacement_factor=structure.displacement_factor,
                has_displacement=structure.has_displacement,
                metadata={
                    "ifvg_mean_threshold": block.mean_threshold,
                    "ote_retracement_level": None,
                },
            )
        )
    return next(iter(sorted(zones, key=lambda item: item.origin_time, reverse=True)), None)


def _fill_mode(threshold: float) -> str:
    if threshold >= 1.0:
        return "100"
    if threshold >= 0.5:
        return "50"
    return "25"


def _reason(context: StrategyContext, side: str, source_zone: _SourceZone, ltf_fvg: FairValueGap | None) -> str:
    htf = context.htf_context
    pullback = f"{source_zone.fill_mode}% FF FVG" if source_zone.zone_type == "FVG" else "OB retracement"
    entry = "LTF FVG pickup" if ltf_fvg is not None else "LTF MSS pickup"
    if htf is None:
        return f"Missed entry pullback: {pullback} -> {entry}"
    return (
        f"HTF {htf.bias.direction} {htf.dealing_range.location}/{htf.zone.zone_type} context -> "
        f"{pullback}, {entry}"
    )


def _target_hint(side: str, entry_low: float, entry_high: float, invalidation: float) -> float:
    entry_mid = (entry_low + entry_high) / 2
    risk = abs(entry_mid - invalidation)
    if side == "long":
        return entry_high + risk * 2
    return entry_low - risk * 2


__all__ = ["detect_entry_model_3"]
