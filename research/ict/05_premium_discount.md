# Premium and Discount

## Dealing Range

Build dealing range from recent significant swing high and swing low.

Preferred sources:

- HTF `intermediate` swing high and low.
- HTF `long` swing high and low.
- Most recent durable range when both sides are available.

Suggested metadata:

- `range_low`
- `range_high`
- `equilibrium`
- `location`: `discount`, `premium`, `equilibrium`, `unknown`

## Location

Equilibrium is midpoint of the dealing range.

Use a small buffer around midpoint to avoid noisy classification.

Suggested buffer:

- 5% of range, or
- ATR-like approximation if available.

Location rules:

- Price below equilibrium minus buffer: `discount`.
- Price above equilibrium plus buffer: `premium`.
- Otherwise: `equilibrium`.

## Direction Preference

For longs:

- Discount is preferred.
- Premium is worse unless a very strong bullish POI and objective are present.

For shorts:

- Premium is preferred.
- Discount is worse unless a very strong bearish POI and objective are present.

## OTE

OTE retracement levels are separate from FVG fill depth.

Common OTE zone:

- 0.62
- 0.705
- 0.79

Do not use OTE as a substitute for FVG lifecycle state.

## Bias Discipline

Premium / discount modifies context. It should not fully replace structure bias.

Example:

- Bullish structure in discount is stronger.
- Bullish structure deep in premium may still be bullish, but lower quality for fresh long execution.
