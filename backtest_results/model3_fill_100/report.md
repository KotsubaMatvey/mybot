# Entry Models Backtest Report

Config:
- symbols: BTCUSDT, ETHUSDT
- timeframes: 5m, 15m, 30m, 1h
- models: model3
- warmup_bars: 100
- forward_bars: 20
- cooldown_bars: 5
- start: full history
- end: full history
- htf_mode: strict
- require_displacement: True
- model3_fill_threshold: 1.0
- execution_pairs: {'1m': '15m', '3m': '30m', '5m': '1h', '15m': '4h', '30m': '4h', '1h': '1d'}
- model_3_htf_map: {'1m': '15m', '3m': '30m', '5m': '1h', '15m': '4h', '30m': '4h', '1h': '1d', '4h': '1d'}
- model_3_ltf_map: {'5m': '1m', '15m': '3m', '30m': '5m', '1h': '15m', '4h': '1h'}
- generated_at: 2026-04-25T23:39:29.386091+00:00

This is an event-study backtest. It does not model fees, slippage, partial exits, breakeven, or full execution management.

## 1. Overall summary
- events: 14
- warnings: 0
- skipped_outcome_events: 1

## 2. Summary by model
| model | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 3 | 14 | 13 | 1 | 14 | 0 | 4.918568 | 5.693182 | 9.907313 | 8.618352 | 0.923077 | 0.846154 | 0.769231 | 0.928571 | 0.461538 | 0.461538 | 4.642857 | ETHUSDT | 30m |

## 3. Summary by direction
| model | direction | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 3 | long | 14 | 13 | 1 | 14 | 0 | 4.918568 | 5.693182 | 9.907313 | 8.618352 | 0.923077 | 0.846154 | 0.769231 | 0.928571 | 0.461538 | 0.461538 | 4.642857 | ETHUSDT | 30m |

## 4. Summary by timeframe
| model | timeframe | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 3 | 15m | 6 | 6 | 0 | 6 | 0 | 3.475706 | 3.115408 | 12.281973 | 9.467564 | 1.0 | 0.833333 | 0.666667 | 0.833333 | 0.333333 | 0.333333 | 4.833333 | ETHUSDT | 15m |
| Entry Model 3 | 1h | 3 | 2 | 1 | 3 | 0 | 2.947392 | 2.947392 | 8.666517 | 8.666517 | 0.5 | 0.5 | 0.5 | 1.0 | 0.5 | 0.5 | 4.666667 | BTCUSDT | 1h |
| Entry Model 3 | 30m | 5 | 5 | 0 | 5 | 0 | 7.438474 | 6.4453 | 7.55404 | 8.618352 | 1.0 | 1.0 | 1.0 | 1.0 | 0.6 | 0.6 | 4.4 | BTCUSDT | 30m |

## 5. Score bucket analysis
| model | score_bucket | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 3 | high | 14 | 13 | 1 | 14 | 0 | 4.918568 | 5.693182 | 9.907313 | 8.618352 | 0.923077 | 0.846154 | 0.769231 | 0.928571 | 0.461538 | 0.461538 | 4.642857 | ETHUSDT | 30m |

## 6. HTF Context Analysis
### Events by HTF bias
| model | htf_bias | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 3 | bullish | 14 | 13 | 1 | 14 | 0 | 4.918568 | 5.693182 | 9.907313 | 8.618352 | 0.923077 | 0.846154 | 0.769231 | 0.928571 | 0.461538 | 0.461538 | 4.642857 | ETHUSDT | 30m |

### Performance by HTF location
| model | htf_location | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 3 | equilibrium | 5 | 5 | 0 | 5 | 0 | 5.668499 | 5.408501 | 6.351643 | 7.448642 | 1.0 | 1.0 | 0.8 | 0.8 | 0.4 | 0.4 | 4.8 | BTCUSDT | 30m |
| Entry Model 3 | premium | 9 | 8 | 1 | 9 | 0 | 4.449861 | 5.888486 | 12.129607 | 10.830815 | 0.875 | 0.75 | 0.75 | 1.0 | 0.5 | 0.5 | 4.555556 | ETHUSDT | 30m |

### Performance by HTF zone type
| model | htf_zone_type | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 3 | Breaker | 6 | 5 | 1 | 6 | 0 | 6.809255 | 6.4453 | 10.453161 | 8.618352 | 1.0 | 1.0 | 1.0 | 1.0 | 0.4 | 0.4 | 4.666667 | BTCUSDT | 30m |
| Entry Model 3 | FVG | 5 | 5 | 0 | 5 | 0 | 5.051522 | 6.083791 | 12.044871 | 9.601537 | 1.0 | 0.8 | 0.8 | 1.0 | 0.6 | 0.6 | 4.6 | BTCUSDT | 30m |
| Entry Model 3 | IFVG | 1 | 1 | 0 | 1 | 0 | 0.201602 | 0.201602 | 4.818425 | 4.818425 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | 0.0 | 4.0 | BTCUSDT | 1h |
| Entry Model 3 | PD | 2 | 2 | 0 | 2 | 0 | 2.21795 | 2.21795 | 5.743243 | 5.743243 | 1.0 | 1.0 | 0.5 | 0.5 | 0.5 | 0.5 | 5.0 | BTCUSDT | 15m |

### Performance by HTF alignment
| model | htf_alignment | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 3 | aligned | 14 | 13 | 1 | 14 | 0 | 4.918568 | 5.693182 | 9.907313 | 8.618352 | 0.923077 | 0.846154 | 0.769231 | 0.928571 | 0.461538 | 0.461538 | 4.642857 | ETHUSDT | 30m |

### Performance by displacement
| model | displacement | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 3 | has_displacement | 13 | 12 | 1 | 13 | 0 | 4.580708 | 5.550841 | 10.014727 | 8.52509 | 0.916667 | 0.833333 | 0.75 | 0.923077 | 0.416667 | 0.416667 | 4.692308 | ETHUSDT | 30m |
| Entry Model 3 | weak_or_none | 1 | 1 | 0 | 1 | 0 | 8.972888 | 8.972888 | 8.618352 | 8.618352 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 4.0 | BTCUSDT | 30m |

### Performance by FVG status
| model | fvg_status | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 3 | filled | 14 | 13 | 1 | 14 | 0 | 4.918568 | 5.693182 | 9.907313 | 8.618352 | 0.923077 | 0.846154 | 0.769231 | 0.928571 | 0.461538 | 0.461538 | 4.642857 | ETHUSDT | 30m |

### Model 3 fill variants
| model | fill_mode | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 3 | 100 | 14 | 13 | 1 | 14 | 0 | 4.918568 | 5.693182 | 9.907313 | 8.618352 | 0.923077 | 0.846154 | 0.769231 | 0.928571 | 0.461538 | 0.461538 | 4.642857 | ETHUSDT | 30m |

## 7. Warnings / skipped events
- fdf1323995a6b685: invalid risk (risk is not positive; R metrics are skipped)

## 8. Interpretation notes
- Replay is bar-by-bar: strategies receive only candles visible at the current bar.
- Forward candles are used only after event detection for outcome measurement.
- `bars_to_*` values are 1-based future bar offsets from the signal bar.
- `*_before_invalidation` uses OHLC bar ordering only; same-bar threshold/invalidation ordering is not modeled.
- HTF-filtered event studies should usually have fewer signals than legacy/off mode.
- If strict signal count does not decrease, HTF gating is too weak.
- If score buckets remain mostly high, scoring is not calibrated enough.
