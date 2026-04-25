# Backtest Rules

## Purpose

Backtests are event studies for model quality and context quality.

They are not full execution simulations.

## Scope

Keep:

- Forward-bar event study.
- Hit 1R before invalidation.
- Hit 2R before invalidation.
- Invalidation rate.
- MFE / MAE style metrics if already present.
- Score distribution.

Do not add:

- Fees.
- Slippage.
- Break-even.
- Partial exits.
- Full position management.

## Required Modes

`--htf-mode strict`:

- Require HTF context and allowed direction.

`--htf-mode soft`:

- Allow weaker context but penalize score.

`--htf-mode off`:

- Legacy comparison behavior.

## Research Variants

Add when implementation reaches Step 6:

- `--require-displacement true|false`
- `--model3-fill-threshold 0.25|0.5|1.0`
- `--entry-mode near_edge|midpoint|full_fill`
- `--same-bar-policy conservative|neutral|optimistic`

If scope is constrained, prioritize:

- `--require-displacement`
- `--model3-fill-threshold`

## Event Columns

Common columns:

- `displacement_factor`
- `has_displacement`
- `swing_significance`
- `fvg_status`
- `fvg_fill_percent`
- `htf_bias`
- `htf_location`
- `htf_zone_type`
- `htf_objective_type`
- `htf_objective_level`

Model 2 columns:

- `source_fvg_direction`
- `breach_time`
- `breach_displacement_factor`
- `ifvg_mean_threshold`

Model 3 columns:

- `source_zone_type`
- `source_zone_time`
- `fill_percent`
- `fill_mode`
- `ltf_mss_time`

## Report Sections

Add summaries:

- `summary_by_htf_bias`
- `summary_by_htf_location`
- `summary_by_htf_zone`
- `summary_by_displacement`
- `summary_by_model3_fill_threshold`
- `summary_by_fvg_status`

## Interpretation Notes

HTF strict should reduce signal count versus legacy.

If strict mode does not reduce signals, gating is too weak.

If nearly every signal scores high, scoring is not calibrated.

If strict quality worsens badly, HTFContext may be too crude or objective/location rules may be misweighted.

## Lookahead Rule

All primitive snapshots, HTF context, LTF context, FVG lifecycle state, and objective state must be sliced to the current replay timestamp.

No future candles may influence current setup creation.
