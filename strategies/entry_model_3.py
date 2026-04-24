from __future__ import annotations

from market_primitives.common import FairValueGap, StructureBreak

from config import MIN_RISK_BPS
from .htf_context import htf_allows_side, htf_metadata, htf_score_modifier
from .scoring import score_model_3
from .setup_utils import classify_zone_status, current_price, primitive_direction
from .types import EntrySetup, PrimitiveSnapshot, StrategyContext, default_components


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

    htf_structure = next(
        (item for item in sorted(htf.structure_breaks, key=lambda item: item.timestamp, reverse=True) if item.direction == direction),
        None,
    )
    if htf_structure is None:
        return []

    ltf_structure = next(
        (
            item
            for item in sorted(ltf.structure_breaks, key=lambda item: item.timestamp, reverse=True)
            if item.direction == direction and item.timestamp > htf_structure.timestamp and item.strength >= 0.2
        ),
        None,
    )
    if ltf_structure is None:
        return []

    continuation_fvg = next(
        (
            item
            for item in sorted(ltf.fvgs, key=lambda item: item.created_at, reverse=True)
            if item.direction == direction and item.created_at > ltf_structure.timestamp and not item.invalidated
        ),
        None,
    )
    if continuation_fvg is None:
        return []

    setup = _build_setup(context, htf, ltf, side, htf_structure, ltf_structure, continuation_fvg)
    return [setup] if setup is not None else []


def _build_setup(
    context: StrategyContext,
    htf: PrimitiveSnapshot,
    ltf: PrimitiveSnapshot,
    side: str,
    htf_structure: StructureBreak,
    ltf_structure: StructureBreak,
    ltf_fvg: FairValueGap,
) -> EntrySetup | None:
    status_info = classify_zone_status(
        ltf,
        zone_low=ltf_fvg.gap_low,
        zone_high=ltf_fvg.gap_high,
        armed_time=max(ltf_structure.timestamp, ltf_fvg.created_at),
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
    entry_mid = (ltf_fvg.gap_low + ltf_fvg.gap_high) / 2
    risk = abs(entry_mid - invalidation)
    risk_floor = (price or entry_mid) * (MIN_RISK_BPS / 10_000)
    if risk < risk_floor:
        return None
    zone_width = max(abs(ltf_fvg.gap_high - ltf_fvg.gap_low), risk_floor)
    if price is not None:
        distance = 0.0 if ltf_fvg.gap_low <= price <= ltf_fvg.gap_high else min(abs(price - ltf_fvg.gap_low), abs(price - ltf_fvg.gap_high))
        if distance > max(zone_width * 2.0, price * 0.004):
            return None

    score = score_model_3(
        htf_alignment=0.8 if htf_structure.break_type in {"BOS", "CHOCH"} else 0.5,
        ltf_strength=min(1.0, ltf_structure.strength + 0.15),
        entry_low=ltf_fvg.gap_low,
        entry_high=ltf_fvg.gap_high,
        invalidation=invalidation,
        missed_primary_penalty=0.3,
        htf_modifier=htf_score_modifier(context.htf_context, side, context.htf_mode),
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
        entry_low=ltf_fvg.gap_low,
        entry_high=ltf_fvg.gap_high,
        invalidation=invalidation,
        target_hint=_target_hint(side, ltf_fvg.gap_low, ltf_fvg.gap_high, invalidation),
        sweep_level=None,
        structure_level=ltf_structure.broken_level,
        context_timeframe=htf.timeframe,
        score=score,
        reason=f"HTF {htf_structure.direction} context, continuation FVG pullback",
        components=components,
        timestamp=max(status_time, htf_structure.timestamp, ltf_structure.timestamp, ltf_fvg.created_at),
        metadata={
            "primary_timeframe": context.primary.timeframe,
            "htf_timeframe": htf.timeframe,
            "ltf_timeframe": ltf.timeframe,
            "htf_structure_type": htf_structure.break_type,
            "ltf_structure_type": ltf_structure.break_type,
            **htf_metadata(context.htf_context),
        },
    )


def _target_hint(side: str, entry_low: float, entry_high: float, invalidation: float) -> float:
    entry_mid = (entry_low + entry_high) / 2
    risk = abs(entry_mid - invalidation)
    if side == "long":
        return entry_high + risk * 2
    return entry_low - risk * 2


__all__ = ["detect_entry_model_3"]
