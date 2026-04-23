from __future__ import annotations

from market_primitives.common import FairValueGap, LiquiditySweep, StructureBreak, zone_overlap

from .scoring import score_model_1
from .types import EntrySetup, StrategyContext, default_components


def detect_entry_model_1(context: StrategyContext) -> list[EntrySetup]:
    snapshot = context.primary
    results: list[EntrySetup] = []
    results.extend(_detect_direction(context, side="long"))
    results.extend(_detect_direction(context, side="short"))
    return sorted(results, key=lambda item: item.timestamp, reverse=True)


def _detect_direction(context: StrategyContext, side: str) -> list[EntrySetup]:
    snapshot = context.primary
    sweep_direction = "bullish" if side == "long" else "bearish"
    structure_direction = sweep_direction
    sweeps = sorted(
        [item for item in (snapshot.raids + snapshot.sweeps) if item.direction == sweep_direction],
        key=lambda item: item.timestamp,
        reverse=True,
    )
    structures = sorted(
        [item for item in snapshot.structure_breaks if item.direction == structure_direction],
        key=lambda item: item.timestamp,
        reverse=True,
    )
    fvgs = sorted(
        [item for item in snapshot.fvgs if item.direction == structure_direction and not item.invalidated],
        key=lambda item: item.created_at,
        reverse=True,
    )

    setups: list[EntrySetup] = []
    for sweep in sweeps[:3]:
        structure = next((item for item in structures if item.timestamp >= sweep.timestamp), None)
        if structure is None:
            continue
        fvg = next((item for item in fvgs if item.created_at >= structure.timestamp), None)
        if fvg is None:
            continue
        setup = _build_setup(snapshot.symbol, snapshot.timeframe, side, sweep, structure, fvg, context.higher_timeframe)
        setups.append(setup)
        break
    return setups


def _build_setup(
    symbol: str,
    timeframe: str,
    side: str,
    sweep: LiquiditySweep,
    structure: StructureBreak,
    fvg: FairValueGap,
    higher_snapshot,
) -> EntrySetup:
    current = "triggered" if fvg.mitigated and not fvg.invalidated else "confirmed"
    if not fvg.mitigated:
        current = "watching"

    entry_low = fvg.gap_low
    entry_high = fvg.gap_high
    invalidation = sweep.wick_extreme if side == "long" else sweep.wick_extreme
    target_hint = _target_hint(side, sweep.liquidity_level, structure.broken_level, entry_low, entry_high)

    htf_alignment = 0.0
    if higher_snapshot:
        htf_alignment = 0.3 if any(item.direction == structure.direction for item in higher_snapshot.structure_breaks) else -0.2

    messy_overlap = any(
        zone_overlap(entry_low, entry_high, ob.zone_low, ob.zone_high) > 0.8
        for ob in higher_snapshot.order_blocks
    ) if higher_snapshot else False
    late_mitigation = bool(fvg.mitigated_at and (fvg.mitigated_at - fvg.created_at) > 6 * 60 * 60 * 1000)

    score = score_model_1(
        clean_sweep=sweep.clean,
        structure_strength=structure.strength,
        entry_low=entry_low,
        entry_high=entry_high,
        invalidation=invalidation,
        context_alignment=htf_alignment,
        messy_overlap=messy_overlap,
        late_mitigation=late_mitigation,
    )

    components = default_components()
    components["sweep_detected"] = True
    components["structure_shift_detected"] = True
    components["fvg_detected"] = True

    reason = (
        f"{'SSL' if side == 'long' else 'BSL'} sweep, "
        f"{structure.direction} {structure.break_type}, "
        f"{structure.direction} FVG retest"
    )

    return EntrySetup(
        model_name="Entry Model 1",
        direction="long" if side == "long" else "short",
        symbol=symbol,
        timeframe=timeframe,
        status=current,
        entry_low=entry_low,
        entry_high=entry_high,
        invalidation=invalidation,
        target_hint=target_hint,
        sweep_level=sweep.liquidity_level,
        structure_level=structure.broken_level,
        context_timeframe=None,
        score=score,
        reason=reason,
        components=components,
        timestamp=max(sweep.timestamp, structure.timestamp, fvg.mitigated_at or fvg.created_at),
        metadata={
            "sweep_timestamp": sweep.timestamp,
            "structure_type": structure.break_type,
            "fvg_created_at": fvg.created_at,
            "fvg_mitigated_at": fvg.mitigated_at,
        },
    )


def _target_hint(side: str, sweep_level: float, structure_level: float, entry_low: float, entry_high: float) -> float:
    entry_mid = (entry_low + entry_high) / 2
    risk = abs(entry_mid - sweep_level)
    if side == "long":
        return max(structure_level, entry_high) + risk * 2
    return min(structure_level, entry_low) - risk * 2


__all__ = ["detect_entry_model_1"]
