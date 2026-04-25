# Entry Model 3

## Definition

Entry Model 3 is:

Missed Entry -> Full Fill FVG / OB retracement -> LTF pickup.

This is a continuation or re-entry model after the first entry was missed.

## Long Conditions

1. HTF or primary bullish context exists.
2. HTF bias is not neutral in strict mode.
3. Bullish structure already occurred.
4. Initial move displaced upward.
5. Price retraces into old bullish FVG or bullish OB.
6. FVG fill reaches configured threshold when source is FVG.
7. Lower timeframe bullish MSS confirms pickup.
8. Optional LTF FVG forms after pickup MSS.
9. Entry triggers from LTF entry zone.

## Short Conditions

1. HTF or primary bearish context exists.
2. HTF bias is not neutral in strict mode.
3. Bearish structure already occurred.
4. Initial move displaced downward.
5. Price retraces into old bearish FVG or bearish OB.
6. FVG fill reaches configured threshold when source is FVG.
7. Lower timeframe bearish MSS confirms pickup.
8. Optional LTF FVG forms after pickup MSS.
9. Entry triggers from LTF entry zone.

## Fill Depth vs OTE

Keep these separate.

FVG fill depth:

- 25% fill.
- 50% consequent encroachment.
- 100% full fill.

OTE retracement:

- 0.62.
- 0.705.
- 0.79.

Do not treat 50% FVG fill as OTE. Do not treat OTE as FVG lifecycle status.

## Required Context

Model 3 must require:

- HTF context.
- LTF context.
- HTF bias not neutral in strict mode.
- Direction aligned with HTF bias.
- LTF MSS aligned with direction.
- Valid risk.
- Risk above `MIN_RISK_BPS`.
- Source zone not too far from current price.

## Metadata

Include:

- `source_zone_type`: `FVG` or `OB`
- `source_zone_time`
- `fvg_fill_percent`
- `fill_mode`
- `ote_retracement_level`
- `ltf_mss_time`
- `ltf_entry_zone_low`
- `ltf_entry_zone_high`
- `displacement_factor`
- `has_displacement`
- `htf_bias`
- `htf_location`
- `htf_zone_type`
- `htf_objective_type`
- `htf_objective_level`

## Rejection Cases

Reject:

- No HTF context.
- No LTF context.
- Neutral HTF in strict mode.
- LTF MSS contradicts HTF bias.
- Source zone is too old.
- FVG fill threshold is not met.
- Risk is zero or below configured floor.
- Entry zone is too far from current price.
