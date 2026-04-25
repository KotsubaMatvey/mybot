# Open Questions

## 1. Naming Conflict

NotebookLM sometimes uses a different Model 1/2/3 taxonomy:

- Model 1 = OB retest.
- Model 2 = FVG entry.
- Model 3 = Turtle Soup + SMT.

The current project does not use that taxonomy.

Do not rename or replace the current models:

- Current Entry Model 1 = Sweep -> BOS/MSS -> post-BOS FVG / imbalance.
- Current Entry Model 2 = Sweep -> FVG Inversion / IFVG.
- Current Entry Model 3 = Missed Entry -> Full Fill FVG / retracement -> LTF pickup.

## 2. IFVG Direction

Correct rule:

- Long IFVG: old bearish FVG is breached upward by body close, then retested as support.
- Short IFVG: old bullish FVG is breached downward by body close, then retested as resistance.

Wick-only breach should not create IFVG.

## 3. Displacement Metric

Needs objective heuristic and calibration.

Initial proposal:

- Body ratio.
- Range expansion versus rolling average.
- Close beyond structure level.
- Bonus if FVG forms after break.

Open question:

- Should displacement thresholds differ by timeframe or asset volatility?

## 4. Swing Significance

Needs objective significance tiers.

Initial proposal:

- `short`: 3-candle fractal.
- `intermediate`: range expansion or survives N bars.
- `long`: HTF swing, survives larger N bars, or high strength.

Open question:

- Should swing strength include volume or only candle structure?

## 5. Killzones

Future module only.

Needs:

- NY timezone.
- DST-safe implementation.
- Exchange/session calendar awareness.
- Soft scoring first, not hard filtering.

Do not add killzones as a hard filter in the current refactor.

## 6. DXY SMT

Future research only.

For crypto, the current project can explore crypto-native SMT pairs:

- BTC / ETH.
- ETH / SOL.
- BTC / SOL.

Do not make DXY SMT a required dependency for current models.

## 7. Model 3 Fill vs OTE

Keep FVG fill depth separate from OTE retracement.

FVG fill:

- 25%.
- 50%.
- 100%.

OTE retracement:

- 0.62.
- 0.705.
- 0.79.

Open question:

- Should Model 3 variants be compared by FVG fill threshold first, then OTE confluence second?

## 8. Sponsorship

Sponsorship is useful as research language but needs a precise implementation definition before coding.

Possible future definition:

- HTF displacement leg.
- Protected swing.
- Active POI.
- Objective in same direction.

Do not block current implementation on sponsorship.

## 9. Same-Bar Policy

Backtests need explicit handling when entry, target, and invalidation occur in the same candle.

Possible policies:

- `conservative`: invalidation first.
- `neutral`: ambiguous event excluded or marked.
- `optimistic`: target first.

Default should be conservative unless project already uses a different explicit policy.
