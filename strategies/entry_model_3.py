from __future__ import annotations

from market_primitives.common import FairValueGap, StructureBreak

from .scoring import score_model_3
from .types import EntrySetup, PrimitiveSnapshot, StrategyContext, default_components


def detect_entry_model_3(context: StrategyContext) -> list[EntrySetup]:
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

    direction = "bullish" if side == "long" else "bearish"
    htf_structure = next((item for item in sorted(htf.structure_breaks, key=lambda x: x.timestamp, reverse=True) if item.direction == direction), None)
    if htf_structure is None:
        return []

    ltf_structure = next((item for item in sorted(ltf.structure_breaks, key=lambda x: x.timestamp, reverse=True) if item.direction == direction), None)
    ltf_fvg = next((item for item in sorted(ltf.fvgs, key=lambda x: x.created_at, reverse=True) if item.direction == direction and item.mitigated and not item.invalidated), None)
    if ltf_structure is None or ltf_fvg is None:
        return []

    if ltf_structure.timestamp < htf_structure.timestamp:
        return []

    return [_build_setup(context.primary, htf, ltf, side, htf_structure, ltf_structure, ltf_fvg)]


def _build_setup(
    primary: PrimitiveSnapshot,
    htf: PrimitiveSnapshot,
    ltf: PrimitiveSnapshot,
    side: str,
    htf_structure: StructureBreak,
    ltf_structure: StructureBreak,
    ltf_fvg: FairValueGap,
) -> EntrySetup:
    entry_low = ltf_fvg.gap_low
    entry_high = ltf_fvg.gap_high
    invalidation = min(c["low"] for c in ltf.candles[-5:]) if side == "long" else max(c["high"] for c in ltf.candles[-5:])
    htf_alignment = 0.8 if htf_structure.break_type in ("BOS", "CHOCH") else 0.4
    ltf_strength = min(1.0, ltf_structure.strength + (0.2 if ltf_fvg.mitigated else 0.0))
    score = score_model_3(
        htf_alignment=htf_alignment,
        ltf_strength=ltf_strength,
        entry_low=entry_low,
        entry_high=entry_high,
        invalidation=invalidation,
        missed_primary_penalty=0.15,
    )
    components = default_components()
    components["structure_shift_detected"] = True
    components["fvg_detected"] = True
    components["ltf_refinement_detected"] = True

    return EntrySetup(
        model_name="Entry Model 3",
        direction="long" if side == "long" else "short",
        symbol=primary.symbol,
        timeframe=primary.timeframe,
        status="triggered",
        entry_low=entry_low,
        entry_high=entry_high,
        invalidation=invalidation,
        target_hint=_target_hint(side, entry_low, entry_high, invalidation),
        sweep_level=None,
        structure_level=ltf_structure.broken_level,
        context_timeframe=htf.timeframe,
        score=score,
        reason=(
            f"HTF {htf_structure.direction} context, "
            f"LTF {ltf_structure.direction} reclaim after FVG mitigation"
        ),
        components=components,
        timestamp=max(htf_structure.timestamp, ltf_structure.timestamp, ltf_fvg.mitigated_at or ltf_fvg.created_at),
        metadata={
            "htf_timeframe": htf.timeframe,
            "ltf_timeframe": ltf.timeframe,
            "htf_structure_type": htf_structure.break_type,
            "ltf_structure_type": ltf_structure.break_type,
        },
    )


def _target_hint(side: str, entry_low: float, entry_high: float, invalidation: float) -> float:
    entry_mid = (entry_low + entry_high) / 2
    risk = abs(entry_mid - invalidation)
    if side == "long":
        return entry_high + risk * 2
    return entry_low - risk * 2


__all__ = ["detect_entry_model_3"]
