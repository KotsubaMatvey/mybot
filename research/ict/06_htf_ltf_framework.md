# HTF to LTF Framework

## Principle

HTF chooses direction, location, POI, and liquidity objective.

LTF chooses the precise execution trigger.

Entry models are execution triggers. They are not the full context.

## HTF Responsibilities

HTFContext should provide:

- Bias.
- Dealing range.
- Premium / discount location.
- Active POI.
- Liquidity objective.
- Whether long or short execution is allowed.
- Score modifier and reason.

HTF objective validates target direction. It must not create bias by itself.

## LTF Responsibilities

LTF execution should identify:

- Sweep.
- MSS/BOS/CHOCH.
- Displacement quality.
- FVG/IFVG/OB retest.
- Entry zone.
- Invalidation level.

## HTF Modes

`strict`:

- Require HTF context.
- Require bias alignment.
- Require objective alignment where available.
- Require correct premium/discount or active POI.

`soft`:

- Allow weaker context.
- Penalize missing objective, neutral bias, or poor location.

`off`:

- Bypass HTF gating.
- Preserve legacy comparison behavior.

## Timeframe Maps

Execution to HTF map:

```python
EXECUTION_HTF_MAP = {
    "1m": "15m",
    "3m": "30m",
    "5m": "1h",
    "15m": "4h",
    "30m": "4h",
    "1h": "1d",
}
```

Model 3 HTF map:

```python
MODEL_3_HTF_MAP = {
    "1m": "15m",
    "3m": "30m",
    "5m": "1h",
    "15m": "4h",
    "30m": "4h",
    "1h": "1d",
    "4h": "1d",
}
```

Model 3 LTF refinement map:

```python
MODEL_3_LTF_MAP = {
    "5m": "1m",
    "15m": "3m",
    "30m": "5m",
    "1h": "15m",
    "4h": "1h",
}
```

## Lookahead Rule

Backtests must build HTF and LTF context only from candles visible at the current timestamp.

No future HTF candle, future LTF candle, future FVG state, or future objective can be passed into the current decision.
