# Market Structure Rules

## Swings

Swing points are the base units for structure, liquidity, premium / discount, and objectives.

Minimum swing tiers:

- `short`: ordinary 3-candle fractal.
- `intermediate`: fractal with above-average candle range or level that remains unbroken for a configured number of bars.
- `long`: HTF swing, old protected swing, or swing with high computed strength.

Suggested metadata:

- `timestamp`
- `level` / `price`
- `direction`: `high` or `low`
- `significance`: `short`, `intermediate`, `long`
- `strength`

HTFContext should prefer `intermediate` and `long` swings. LTF execution can use `short` and `intermediate` swings.

## Structure Breaks

Structure breaks should distinguish:

- `BOS`: continuation break in the current order-flow direction.
- `CHOCH`: change of character against the prior local structure.
- `MSS`: market structure shift with displacement after liquidity is taken.

Suggested metadata:

- `timestamp`
- `direction`: `bullish` or `bearish`
- `break_type`: `BOS`, `CHOCH`, `MSS`
- `broken_level`
- `strength`
- `displacement_factor`
- `has_displacement`
- `body_ratio`
- `range_expansion`
- `created_fvg_after_break`

## Displacement

A valid execution break should usually show displacement.

Initial heuristic:

- Body ratio is at least configured minimum.
- Candle range expands versus rolling average range.
- Close is beyond the broken structure level.
- Optional FVG after the break increases confidence.

Suggested defaults:

- `DISPLACEMENT_MIN_BODY_RATIO = 0.55`
- `DISPLACEMENT_MIN_RANGE_EXPANSION = 1.2`

## Bias Discipline

Do not infer bullish bias only because there is a swing high above.

Liquidity objectives validate target direction. They do not create bias by themselves.

Structure has the highest weight. Premium / discount, POI, and objective should modify or confirm the context.
