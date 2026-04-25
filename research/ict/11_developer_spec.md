# Developer Spec

## Refactor Sequence

Step 1:

- Create this research knowledge base only.

Step 2:

- Implement displacement quality.
- Implement swing significance.

Step 3:

- Improve FVG lifecycle.
- Improve IFVG direction and body-breach validation.
- Improve OB mean-threshold validation.
- Improve Breaker as failed OB.

Step 4:

- Update HTFContext with stricter bias, POI, premium/discount, and objective behavior.

Step 5:

- Update Entry Model 1, 2, and 3 using the strengthened primitives and HTFContext.

Step 6:

- Update backtesting, reports, and smoke tests.

## Config Constants

Expected config values:

```python
REQUIRE_HTF_CONTEXT_FOR_ENTRY_MODELS = True
ENTRY_MODEL_HTF_MODE = "strict"

DISPLACEMENT_MIN_BODY_RATIO = 0.55
DISPLACEMENT_MIN_RANGE_EXPANSION = 1.2

SWING_INTERMEDIATE_RANGE_MULT = 1.1
SWING_LONG_MIN_AGE_BARS = 20

MIN_RISK_BPS = 5
MAX_SETUP_AGE_BARS = 30
MAX_INVERSION_AGE_BARS = 40

MODEL3_FILL_THRESHOLD = 0.5
```

## Data Structures

Extend existing dataclasses where safe. Avoid turning setup objects into execution order objects.

Important object families:

- `SwingPoint`
- `LiquiditySweep`
- `StructureBreak`
- `FairValueGap`
- `InvertedFVG`
- `OrderBlock`
- `BreakerBlock`
- `HTFContext`
- `EntrySetup`

## EntrySetup Boundary

EntrySetup remains scanner-friendly:

- Model name.
- Direction.
- Symbol.
- Timeframe.
- Status.
- Entry zone.
- Invalidation.
- Target hint.
- Sweep and structure levels.
- Score.
- Reason.
- Components.
- Timestamp.
- Metadata.

Do not add mandatory position sizing, order routing, exchange execution, or full trade management.

## Safety Rules

Avoid:

- Big rewrite.
- Duplicating strategy logic inside backtesting.
- Silent broad `except pass`.
- Hardcoded magic numbers in multiple files.
- Introducing large dependencies.
