from __future__ import annotations

from market_primitives.common import InvertedFVG, LiquiditySweep, zone_overlap

from .scoring import score_model_2
from .types import EntrySetup, StrategyContext, default_components


def detect_entry_model_2(context: StrategyContext) -> list[EntrySetup]:
    results: list[EntrySetup] = []
    results.extend(_detect_direction(context, side="long"))
    results.extend(_detect_direction(context, side="short"))
    return sorted(results, key=lambda item: item.timestamp, reverse=True)


def _detect_direction(context: StrategyContext, side: str) -> list[EntrySetup]:
    snapshot = context.primary
    expected_direction = "bullish" if side == "long" else "bearish"
    sweeps = sorted(
        [item for item in (snapshot.raids + snapshot.sweeps) if item.direction == expected_direction],
        key=lambda item: item.timestamp,
        reverse=True,
    )
    inversions = sorted(
        [item for item in snapshot.ifvgs if item.direction == expected_direction],
        key=lambda item: item.timestamp,
        reverse=True,
    )
    results: list[EntrySetup] = []

    for sweep in sweeps[:3]:
        inversion = next((item for item in inversions if item.invalidated_at >= sweep.timestamp), None)
        if inversion is None:
            continue
        results.append(_build_setup(snapshot.symbol, snapshot.timeframe, side, sweep, inversion, context.higher_timeframe))
        break
    return results


def _build_setup(
    symbol: str,
    timeframe: str,
    side: str,
    sweep: LiquiditySweep,
    inversion: InvertedFVG,
    higher_snapshot,
) -> EntrySetup:
    entry_low = inversion.zone_low
    entry_high = inversion.zone_high
    invalidation = sweep.wick_extreme
    target_hint = _target_hint(side, entry_low, entry_high, invalidation)
    messy_overlap = any(
        zone_overlap(entry_low, entry_high, block.zone_low, block.zone_high) > 0.9
        for block in (higher_snapshot.breaker_blocks if higher_snapshot else [])
    )
    score = score_model_2(
        clean_sweep=sweep.clean,
        inversion_confidence=inversion.confidence,
        entry_low=entry_low,
        entry_high=entry_high,
        invalidation=invalidation,
        messy_overlap=messy_overlap,
    )

    components = default_components()
    components["sweep_detected"] = True
    components["inversion_detected"] = True

    return EntrySetup(
        model_name="Entry Model 2",
        direction="long" if side == "long" else "short",
        symbol=symbol,
        timeframe=timeframe,
        status="triggered",
        entry_low=entry_low,
        entry_high=entry_high,
        invalidation=invalidation,
        target_hint=target_hint,
        sweep_level=sweep.liquidity_level,
        structure_level=None,
        context_timeframe=None,
        score=score,
        reason=f"{'SSL' if side == 'long' else 'BSL'} sweep, {inversion.direction} inversion confirmed",
        components=components,
        timestamp=max(sweep.timestamp, inversion.retest_at),
        metadata={
            "source_direction": inversion.source_direction,
            "invalidated_at": inversion.invalidated_at,
            "retest_at": inversion.retest_at,
        },
    )


def _target_hint(side: str, entry_low: float, entry_high: float, invalidation: float) -> float:
    entry_mid = (entry_low + entry_high) / 2
    risk = abs(entry_mid - invalidation)
    if side == "long":
        return entry_high + risk * 2.5
    return entry_low - risk * 2.5


__all__ = ["detect_entry_model_2"]
