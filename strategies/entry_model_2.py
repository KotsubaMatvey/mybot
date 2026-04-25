from __future__ import annotations

from dataclasses import dataclass

from market_primitives.common import BreakerBlock, InvertedFVG, LiquiditySweep, zone_overlap

from config import MAX_INVERSION_AGE_BARS, MIN_RISK_BPS, REQUIRE_HTF_CONTEXT_FOR_ENTRY_MODELS
from .htf_context import htf_allows_side, htf_metadata, htf_score_modifier
from .scoring import score_model_2
from .setup_utils import classify_zone_status, is_recent_enough, primitive_direction, sweep_label
from .types import EntrySetup, PrimitiveSnapshot, StrategyContext, default_components


@dataclass(slots=True)
class _InversionCandidate:
    kind: str
    direction: str
    zone_low: float
    zone_high: float
    armed_time: int
    timestamp: int
    confidence: float
    metadata: dict


def detect_entry_model_2(context: StrategyContext) -> list[EntrySetup]:
    results: list[EntrySetup] = []
    results.extend(_detect_direction(context, side="long"))
    results.extend(_detect_direction(context, side="short"))
    return sorted(results, key=lambda item: item.timestamp, reverse=True)


def _detect_direction(context: StrategyContext, side: str) -> list[EntrySetup]:
    htf_mode = context.htf_mode if REQUIRE_HTF_CONTEXT_FOR_ENTRY_MODELS else "off"
    if REQUIRE_HTF_CONTEXT_FOR_ENTRY_MODELS and not htf_allows_side(context.htf_context, side, htf_mode):
        return []

    snapshot = context.primary
    direction = primitive_direction(side)  # type: ignore[arg-type]
    sweeps = sorted(
        [item for item in (snapshot.raids + snapshot.sweeps) if item.direction == direction],
        key=lambda item: item.timestamp,
        reverse=True,
    )
    candidates = sorted(_build_candidates(snapshot, direction), key=lambda item: item.armed_time)
    current_timestamp = int(snapshot.candles[-1]["time"]) if snapshot.candles else 0

    for sweep in sweeps[:4]:
        candidate = next(
            (
                item
                for item in candidates
                if item.armed_time > sweep.timestamp
                and item.timestamp > sweep.timestamp
                and is_recent_enough(current_timestamp, item.armed_time, snapshot.timeframe, MAX_INVERSION_AGE_BARS)
            ),
            None,
        )
        if candidate is None:
            continue
        setup = _build_setup(snapshot, side, sweep, candidate, context, htf_mode)
        if setup is not None:
            return [setup]
    return []


def _build_candidates(snapshot: PrimitiveSnapshot, direction: str) -> list[_InversionCandidate]:
    candidates: list[_InversionCandidate] = []
    for inversion in snapshot.ifvgs:
        if inversion.direction != direction:
            continue
        candidates.append(_from_ifvg(inversion))
    return candidates


def _from_ifvg(inversion: InvertedFVG) -> _InversionCandidate:
    return _InversionCandidate(
        kind="IFVG",
        direction=inversion.direction,
        zone_low=inversion.zone_low,
        zone_high=inversion.zone_high,
        armed_time=inversion.invalidated_at,
        timestamp=inversion.retest_at or inversion.invalidated_at,
        confidence=inversion.confidence,
        metadata={
            "source_direction": inversion.source_direction,
            "source_fvg_direction": inversion.source_direction,
            "source_fvg_time": inversion.source_fvg_time,
            "invalidated_at": inversion.invalidated_at,
            "breach_time": inversion.invalidated_at,
            "retest_at": inversion.retest_at,
            "breach_displacement_factor": inversion.breach_displacement_factor,
            "has_displacement": inversion.breach_displacement_factor > 0,
            "ifvg_mean_threshold": inversion.mean_threshold,
        },
    )


def _from_breaker(breaker: BreakerBlock) -> _InversionCandidate:
    return _InversionCandidate(
        kind="Breaker",
        direction=breaker.direction,
        zone_low=breaker.zone_low,
        zone_high=breaker.zone_high,
        armed_time=breaker.trigger_time,
        timestamp=breaker.timestamp,
        confidence=0.7 if breaker.retested else 0.58,
        metadata={
            "origin_time": breaker.origin_time,
            "trigger_time": breaker.trigger_time,
            "retested": breaker.retested,
        },
    )


def _build_setup(
    snapshot: PrimitiveSnapshot,
    side: str,
    sweep: LiquiditySweep,
    candidate: _InversionCandidate,
    context: StrategyContext,
    htf_mode: str,
) -> EntrySetup | None:
    higher_snapshot = context.higher_timeframe
    status_info = classify_zone_status(
        snapshot,
        zone_low=candidate.zone_low,
        zone_high=candidate.zone_high,
        armed_time=candidate.armed_time,
    )
    if status_info is None:
        return None
    status, status_time = status_info
    if status != "watching" and status_time <= candidate.armed_time:
        return None
    if context.require_displacement and candidate.metadata.get("has_displacement") is False:
        return None

    entry_mid = (candidate.zone_low + candidate.zone_high) / 2
    risk = abs(entry_mid - sweep.wick_extreme)
    risk_floor = entry_mid * (MIN_RISK_BPS / 10_000)
    if risk <= 0 or risk < risk_floor:
        return None

    messy_overlap = any(
        zone_overlap(candidate.zone_low, candidate.zone_high, block.zone_low, block.zone_high) > 0.9
        for block in (higher_snapshot.breaker_blocks if higher_snapshot else [])
    )
    score = score_model_2(
        clean_sweep=sweep.clean,
        inversion_confidence=candidate.confidence,
        entry_low=candidate.zone_low,
        entry_high=candidate.zone_high,
        invalidation=sweep.wick_extreme,
        htf_modifier=htf_score_modifier(context.htf_context, side, htf_mode),
        messy_overlap=messy_overlap,
        breach_displacement_factor=float(candidate.metadata.get("breach_displacement_factor") or 0.0),
        has_displacement=bool(candidate.metadata.get("has_displacement")),
    )

    components = default_components()
    components["sweep_detected"] = True
    components["inversion_detected"] = True

    return EntrySetup(
        model_name="Entry Model 2",
        direction="long" if side == "long" else "short",
        symbol=snapshot.symbol,
        timeframe=snapshot.timeframe,
        status=status,
        entry_low=candidate.zone_low,
        entry_high=candidate.zone_high,
        invalidation=sweep.wick_extreme,
        target_hint=_target_hint(side, candidate.zone_low, candidate.zone_high, sweep.wick_extreme),
        sweep_level=sweep.liquidity_level,
        structure_level=None,
        context_timeframe=context.htf_timeframe,
        score=score,
        reason=_reason(context, side, candidate),
        components=components,
        timestamp=max(status_time, sweep.timestamp, candidate.timestamp),
        metadata={
            "candidate_kind": candidate.kind,
            "sweep_time": sweep.timestamp,
            "swing_significance": sweep.source_swing_significance,
            **candidate.metadata,
            **htf_metadata(context.htf_context),
        },
    )


def _reason(context: StrategyContext, side: str, candidate: _InversionCandidate) -> str:
    htf = context.htf_context
    if htf is None:
        return f"{sweep_label(side)} sweep, {candidate.kind} inversion armed"
    return (
        f"HTF {htf.bias.direction} {htf.dealing_range.location}/{htf.zone.zone_type} context -> "
        f"LTF {sweep_label(side)} sweep, {candidate.kind} inversion retest"
    )


def _target_hint(side: str, entry_low: float, entry_high: float, invalidation: float) -> float:
    entry_mid = (entry_low + entry_high) / 2
    risk = abs(entry_mid - invalidation)
    if side == "long":
        return entry_high + risk * 2.5
    return entry_low - risk * 2.5


__all__ = ["detect_entry_model_2"]
