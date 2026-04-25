# ICT Research Source Summary

## Purpose

This folder is the project knowledge base for ICT-style research rules distilled into developer-ready implementation notes.

The rules here are intended to strengthen the existing trading / ICT analysis bot architecture, not replace it.

## Project Model Semantics

The current project keeps Sayx-style execution models:

- Entry Model 1: Sweep -> BOS/MSS -> post-BOS FVG / imbalance -> retest.
- Entry Model 2: Sweep -> FVG Inversion / IFVG -> retest.
- Entry Model 3: Missed Entry -> Full Fill FVG / retracement -> LTF pickup.

Do not rename these models to match alternate NotebookLM or lecture taxonomies.

## Core Framework

HTF defines context:

- Bias.
- Premium / discount.
- Active POI.
- Liquidity objective.
- Direction permission.

LTF defines execution:

- Sweep.
- MSS/BOS/CHOCH.
- FVG / IFVG / OB pickup.
- Retest and entry zone.

## Non-Goals

Do not add in this refactor:

- Live trading.
- Exchange order execution.
- Break-even or partial exits.
- Full trade management.
- Silver Bullet as a new model.
- DXY SMT as a required filter.
- Killzones as a hard filter.
- Hyperparameter optimization.

## Implementation Stance

Use targeted refactors. Preserve the existing scanner, strategy, primitive, backtesting, alert, and report layers.

Prefer explicit metadata over implicit behavior so backtests can explain why a setup was accepted or rejected.
