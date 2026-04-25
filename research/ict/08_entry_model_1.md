# Entry Model 1

## Definition

Entry Model 1 is:

Sweep -> displacement BOS/MSS -> post-BOS FVG / imbalance -> retest.

It remains an execution model. HTFContext provides direction and location permission.

## Long Conditions

1. HTF allows long, unless `htf_mode=off`.
2. LTF sell-side liquidity sweep occurs.
3. Bullish MSS/BOS occurs after the sweep.
4. Structure break has displacement or creates a post-break bullish FVG.
5. Bullish FVG forms after structure break.
6. Price returns into the FVG.
7. Setup triggers on retest.

Required ordering:

`T_sweep < T_structure < T_fvg < T_entry`

## Short Conditions

1. HTF allows short, unless `htf_mode=off`.
2. LTF buy-side liquidity sweep occurs.
3. Bearish MSS/BOS occurs after the sweep.
4. Structure break has displacement or creates a post-break bearish FVG.
5. Bearish FVG forms after structure break.
6. Price returns into the FVG.
7. Setup triggers on retest.

Required ordering:

`T_sweep < T_structure < T_fvg < T_entry`

## Invalidation

Long invalidation:

- Sweep low / wick extreme.

Short invalidation:

- Sweep high / wick extreme.

Reject if risk is zero or below configured minimum floor.

## Metadata

Include:

- `sweep_time`
- `sweep_level`
- `structure_time`
- `structure_type`
- `structure_level`
- `displacement_factor`
- `has_displacement`
- `body_ratio`
- `range_expansion`
- `fvg_time`
- `fvg_status`
- `fvg_fill_percent`
- `htf_bias`
- `htf_location`
- `htf_zone_type`
- `htf_objective_type`
- `htf_objective_level`

## Reason Format

Example:

`HTF bullish discount/OB context - LTF SSL sweep, displacement MSS, post-BOS FVG retest`

## Rejection Cases

Reject:

- No HTF permission in strict mode.
- No sweep.
- Structure before sweep.
- FVG before structure.
- Retest before FVG creation.
- Structure break without displacement and without post-break FVG.
- FVG invalidated before retest.
