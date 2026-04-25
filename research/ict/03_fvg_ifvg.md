# FVG and IFVG Rules

## Fair Value Gap Creation

FVGs are created only after the third candle closes.

Bullish FVG:

- `low[i] > high[i - 2]`
- Zone: `high[i - 2]` to `low[i]`
- Direction: `bullish`

Bearish FVG:

- `high[i] < low[i - 2]`
- Zone: `high[i]` to `low[i - 2]`
- Direction: `bearish`

Suggested metadata:

- `direction`
- `gap_low`
- `gap_high`
- `created_at`
- `mitigated_at`
- `invalidated`
- `status`
- `fill_percent`
- `consequent_encroachment`

## Lifecycle

Statuses:

- `open`
- `partially_filled`
- `filled`
- `inverted`
- `invalidated`

Wick touch can mark partial fill or mitigation. Body close through the opposite boundary can mark full fill, invalidation, or inversion depending on direction and context.

## Fill Percent

Track fill as a percent of the gap:

- 25% fill: shallow return.
- 50% fill: consequent encroachment.
- 100% fill: full fill.

FVG fill depth is separate from OTE retracement levels.

## Inverted FVG

Correct IFVG direction:

Long IFVG:

- Source is an old bearish FVG.
- Price breaches above the bearish FVG high by body close.
- Breach should show displacement.
- The old bearish FVG becomes bullish support.
- Entry requires retest as support.

Short IFVG:

- Source is an old bullish FVG.
- Price breaches below the bullish FVG low by body close.
- Breach should show displacement.
- The old bullish FVG becomes bearish resistance.
- Entry requires retest as resistance.

Do not create IFVG from wick-only breach.

Suggested IFVG metadata:

- `source_fvg_time`
- `source_direction`
- `direction`
- `zone_low`
- `zone_high`
- `invalidated_at`
- `retest_at`
- `confidence`
- `breach_displacement_factor`
- `mean_threshold`

## Rejection Cases

Reject or penalize:

- Ancient FVG/IFVG without configured age limit.
- Wick-only inversion.
- IFVG breach before required sweep in Entry Model 2.
- Retest before breach.
- FVG invalidated before entry retest.
