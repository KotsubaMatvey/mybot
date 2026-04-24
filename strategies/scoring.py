from __future__ import annotations

from market_primitives.common import normalized_zone_width

from .types import EntrySetup


def clamp_score(value: float) -> int:
    return max(1, min(5, int(round(value))))


def score_model_1(
    *,
    clean_sweep: bool,
    structure_strength: float,
    entry_low: float,
    entry_high: float,
    invalidation: float,
    context_alignment: float = 0.0,
    htf_modifier: float = 0.0,
    messy_overlap: bool = False,
    late_mitigation: bool = False,
) -> int:
    score = 2.6
    if clean_sweep:
        score += 0.5
    score += min(0.6, structure_strength * 0.7)
    zone_width = normalized_zone_width(entry_low, entry_high)
    if zone_width <= 0.002:
        score += 0.4
    elif zone_width > 0.007:
        score -= 0.5
    if invalidation > 0:
        invalidation_width = abs(((entry_low + entry_high) / 2) - invalidation) / invalidation
        if invalidation_width > 0.01:
            score -= 0.4
    score += context_alignment + htf_modifier
    if messy_overlap:
        score -= 0.4
    if late_mitigation:
        score -= 0.3
    return clamp_score(score)


def score_model_2(
    *,
    clean_sweep: bool,
    inversion_confidence: float,
    entry_low: float,
    entry_high: float,
    invalidation: float,
    htf_modifier: float = 0.0,
    messy_overlap: bool = False,
) -> int:
    score = 2.8
    if clean_sweep:
        score += 0.5
    score += min(0.8, inversion_confidence)
    zone_width = normalized_zone_width(entry_low, entry_high)
    if zone_width <= 0.002:
        score += 0.3
    elif zone_width > 0.008:
        score -= 0.6
    if invalidation > 0 and abs(((entry_low + entry_high) / 2) - invalidation) / invalidation > 0.012:
        score -= 0.4
    if messy_overlap:
        score -= 0.5
    score += htf_modifier
    return clamp_score(score)


def score_model_3(
    *,
    htf_alignment: float,
    ltf_strength: float,
    entry_low: float,
    entry_high: float,
    invalidation: float,
    missed_primary_penalty: float = 0.0,
    htf_modifier: float = 0.0,
) -> int:
    score = 2.3 + min(0.9, htf_alignment) + min(0.7, ltf_strength) - missed_primary_penalty
    zone_width = normalized_zone_width(entry_low, entry_high)
    if zone_width <= 0.0015:
        score += 0.4
    elif zone_width > 0.006:
        score -= 0.5
    if invalidation > 0 and abs(((entry_low + entry_high) / 2) - invalidation) / invalidation > 0.009:
        score -= 0.4
    score += htf_modifier
    return clamp_score(score)


def score_setup(setup: EntrySetup) -> int:
    return clamp_score(float(setup.score))


__all__ = [
    "score_model_1",
    "score_model_2",
    "score_model_3",
    "score_setup",
]
