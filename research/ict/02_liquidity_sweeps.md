# Liquidity Sweep Rules

## Definition

A liquidity sweep takes a prior swing or equal-high/equal-low level and then closes back inside or rejects the level.

Suggested metadata:

- `timestamp`
- `direction`
- `liquidity_level`
- `wick_extreme`
- `close_back_inside`
- `wick_length`
- `clean`
- `source_swing_index`
- `source_swing_significance`

## Direction Mapping

For long setups:

- Prefer sell-side liquidity sweep.
- Price takes prior low / equal lows / SSL.
- Candle should close back above the swept level or show clear rejection.

For short setups:

- Prefer buy-side liquidity sweep.
- Price takes prior high / equal highs / BSL.
- Candle should close back below the swept level or show clear rejection.

## Clean Sweep

A sweep is cleaner when:

- It targets an `intermediate` or `long` swing.
- It has a meaningful wick beyond the liquidity level.
- It closes back inside the prior range.
- It is followed by displacement in the opposite direction.

## Execution Ordering

Sweep should occur before execution confirmation.

For Entry Model 1:

`T_sweep < T_structure < T_fvg < T_entry`

For Entry Model 2:

`T_sweep < T_ifvg_breach < T_retest`

For Entry Model 3:

The original move may already exist, but LTF pickup confirmation must occur after the retracement into the source zone.

## Rejection Cases

Reject or heavily penalize:

- Sweep after structure confirmation.
- Sweep of insignificant noise when better HTF context is unavailable.
- Wick-only liquidity event without close-back-inside or follow-through.
- Sweep against strict HTF permission.
