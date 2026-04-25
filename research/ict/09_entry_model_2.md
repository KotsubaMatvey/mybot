# Entry Model 2

## Definition

Entry Model 2 is:

Sweep -> FVG Inversion / IFVG -> retest.

Pure IFVG without sweep is not this model. It can be a future separate strategy.

## Long Conditions

1. HTF allows long, unless `htf_mode=off`.
2. LTF sell-side sweep occurs.
3. Existing bearish FVG exists before inversion.
4. Price breaches above bearish FVG high by body close.
5. Breach has displacement.
6. Bearish FVG becomes bullish IFVG support.
7. Price retests IFVG after breach.
8. Setup triggers.

## Short Conditions

1. HTF allows short, unless `htf_mode=off`.
2. LTF buy-side sweep occurs.
3. Existing bullish FVG exists before inversion.
4. Price breaches below bullish FVG low by body close.
5. Breach has displacement.
6. Bullish FVG becomes bearish IFVG resistance.
7. Price retests IFVG after breach.
8. Setup triggers.

## Required Ordering

Long and short:

`T_sweep < T_breach < T_retest`

Source FVG must exist before `T_breach`.

## Invalidation

Use IFVG mean threshold as conservative invalidation reference.

Long IFVG invalidation:

- Close below IFVG mean threshold, or full failure through the lower side.

Short IFVG invalidation:

- Close above IFVG mean threshold, or full failure through the upper side.

## Metadata

Include:

- `sweep_time`
- `source_fvg_direction`
- `source_fvg_time`
- `breach_time`
- `breach_displacement_factor`
- `has_displacement`
- `ifvg_mean_threshold`
- `retest_time`
- `fvg_status`
- `htf_bias`
- `htf_location`
- `htf_zone_type`
- `htf_objective_type`
- `htf_objective_level`

## Rejection Cases

Reject:

- No sweep.
- Breach before sweep.
- Wick-only breach.
- No opposite-direction source FVG.
- Retest before breach.
- Candidate older than configured maximum age.
- Missing displacement when displacement is required.
- HTF opposite direction in strict mode.
