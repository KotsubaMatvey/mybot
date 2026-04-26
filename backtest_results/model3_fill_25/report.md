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
- model3_fill_threshold: 0.25
- execution_pairs: {'1m': '15m', '3m': '30m', '5m': '1h', '15m': '4h', '30m': '4h', '1h': '1d'}
- model_3_htf_map: {'1m': '15m', '3m': '30m', '5m': '1h', '15m': '4h', '30m': '4h', '1h': '1d', '4h': '1d'}
- model_3_ltf_map: {'5m': '1m', '15m': '3m', '30m': '5m', '1h': '15m', '4h': '1h'}
- generated_at: 2026-04-25T23:30:52.938006+00:00

This is an event-study backtest. It does not model fees, slippage, partial exits, breakeven, or full execution management.

## 1. Overall summary
- events: 23
- warnings: 0
- skipped_outcome_events: 5

## 2. Summary by model
| model | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 3 | 23 | 18 | 5 | 21 | 2 | 9.083174 | 5.888486 | 7.517218 | 4.51158 | 0.944444 | 0.888889 | 0.722222 | 0.826087 | 0.555556 | 0.5 | 4.217391 | BTCUSDT | 1h |

## 3. Summary by direction
| model | direction | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 3 | long | 21 | 16 | 5 | 21 | 0 | 10.04917 | 6.124485 | 8.198315 | 6.133533 | 0.9375 | 0.875 | 0.8125 | 0.809524 | 0.5625 | 0.5625 | 4.238095 | BTCUSDT | 1h |
| Entry Model 3 | short | 2 | 2 | 0 | 0 | 2 | 1.355203 | 1.355203 | 2.06844 | 2.06844 | 1.0 | 1.0 | 0.0 | 1.0 | 0.5 | 0.0 | 4.0 | BTCUSDT | 5m |

## 4. Summary by timeframe
| model | timeframe | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 3 | 15m | 7 | 6 | 1 | 7 | 0 | 3.475706 | 3.115408 | 12.281973 | 9.467564 | 1.0 | 0.833333 | 0.666667 | 0.857143 | 0.333333 | 0.333333 | 4.714286 | ETHUSDT | 15m |
| Entry Model 3 | 1h | 7 | 4 | 3 | 7 | 0 | 20.220269 | 17.215742 | 4.726829 | 2.870751 | 0.75 | 0.75 | 0.75 | 0.714286 | 0.75 | 0.75 | 3.857143 | BTCUSDT | 1h |
| Entry Model 3 | 30m | 7 | 6 | 1 | 7 | 0 | 9.841901 | 7.709094 | 6.428982 | 6.411544 | 1.0 | 1.0 | 1.0 | 0.857143 | 0.666667 | 0.666667 | 4.142857 | BTCUSDT | 30m |
| Entry Model 3 | 5m | 2 | 2 | 0 | 0 | 2 | 1.355203 | 1.355203 | 2.06844 | 2.06844 | 1.0 | 1.0 | 0.0 | 1.0 | 0.5 | 0.0 | 4.0 | BTCUSDT | 5m |

## 5. Score bucket analysis
| model | score_bucket | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 3 | high | 19 | 17 | 2 | 17 | 2 | 6.897008 | 5.693182 | 7.921101 | 4.818425 | 0.941176 | 0.882353 | 0.705882 | 0.842105 | 0.529412 | 0.470588 | 4.473684 | BTCUSDT | 1h |
| Entry Model 3 | medium | 4 | 1 | 3 | 4 | 0 | 46.24799 | 46.24799 | 0.651206 | 0.651206 | 1.0 | 1.0 | 1.0 | 0.75 | 1.0 | 1.0 | 3.0 | BTCUSDT | 1h |

## 6. HTF Context Analysis
### Events by HTF bias
| model | htf_bias | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 3 | bearish | 2 | 2 | 0 | 0 | 2 | 1.355203 | 1.355203 | 2.06844 | 2.06844 | 1.0 | 1.0 | 0.0 | 1.0 | 0.5 | 0.0 | 4.0 | BTCUSDT | 5m |
| Entry Model 3 | bullish | 21 | 16 | 5 | 21 | 0 | 10.04917 | 6.124485 | 8.198315 | 6.133533 | 0.9375 | 0.875 | 0.8125 | 0.809524 | 0.5625 | 0.5625 | 4.238095 | BTCUSDT | 1h |

### Performance by HTF location
| model | htf_location | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 3 | discount | 2 | 2 | 0 | 0 | 2 | 1.355203 | 1.355203 | 2.06844 | 2.06844 | 1.0 | 1.0 | 0.0 | 1.0 | 0.5 | 0.0 | 4.0 | BTCUSDT | 5m |
| Entry Model 3 | equilibrium | 5 | 5 | 0 | 5 | 0 | 5.668499 | 5.408501 | 6.351643 | 7.448642 | 1.0 | 1.0 | 0.8 | 0.8 | 0.4 | 0.4 | 4.8 | BTCUSDT | 30m |
| Entry Model 3 | premium | 16 | 11 | 5 | 16 | 0 | 12.040384 | 6.16518 | 9.037712 | 4.818425 | 0.909091 | 0.818182 | 0.818182 | 0.8125 | 0.636364 | 0.636364 | 4.0625 | BTCUSDT | 1h |

### Performance by HTF zone type
| model | htf_zone_type | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 3 | Breaker | 6 | 5 | 1 | 6 | 0 | 6.809255 | 6.4453 | 10.453161 | 8.618352 | 1.0 | 1.0 | 1.0 | 1.0 | 0.4 | 0.4 | 4.666667 | BTCUSDT | 30m |
| Entry Model 3 | FVG | 10 | 8 | 2 | 10 | 0 | 15.262868 | 6.269846 | 7.825291 | 3.318868 | 1.0 | 0.875 | 0.875 | 0.7 | 0.75 | 0.75 | 4.1 | BTCUSDT | 1h |
| Entry Model 3 | IFVG | 3 | 1 | 2 | 3 | 0 | 0.201602 | 0.201602 | 4.818425 | 4.818425 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 | 0.0 | 3.333333 | BTCUSDT | 1h |
| Entry Model 3 | PD | 4 | 4 | 0 | 2 | 2 | 1.786576 | 1.711016 | 3.905841 | 2.06844 | 1.0 | 1.0 | 0.25 | 0.75 | 0.5 | 0.25 | 4.5 | BTCUSDT | 15m |

### Performance by HTF alignment
| model | htf_alignment | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 3 | aligned | 23 | 18 | 5 | 21 | 2 | 9.083174 | 5.888486 | 7.517218 | 4.51158 | 0.944444 | 0.888889 | 0.722222 | 0.826087 | 0.555556 | 0.5 | 4.217391 | BTCUSDT | 1h |

### Performance by displacement
| model | displacement | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 3 | has_displacement | 15 | 12 | 3 | 15 | 0 | 4.580708 | 5.550841 | 10.014727 | 8.52509 | 0.916667 | 0.833333 | 0.75 | 0.933333 | 0.416667 | 0.416667 | 4.533333 | ETHUSDT | 30m |
| Entry Model 3 | weak_or_none | 8 | 6 | 2 | 6 | 2 | 18.088105 | 15.415965 | 2.522201 | 1.391771 | 1.0 | 1.0 | 0.666667 | 0.625 | 0.833333 | 0.666667 | 3.625 | BTCUSDT | 1h |

### Performance by FVG status
| model | fvg_status | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 3 | filled | 14 | 13 | 1 | 14 | 0 | 4.918568 | 5.693182 | 9.907313 | 8.618352 | 0.923077 | 0.846154 | 0.769231 | 0.928571 | 0.461538 | 0.461538 | 4.642857 | ETHUSDT | 30m |
| Entry Model 3 | partially_filled | 9 | 5 | 4 | 7 | 2 | 19.911148 | 21.859041 | 1.30297 | 0.923077 | 1.0 | 1.0 | 0.6 | 0.666667 | 0.8 | 0.6 | 3.555556 | BTCUSDT | 1h |

### Model 3 fill variants
| model | fill_mode | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 3 | 25 | 23 | 18 | 5 | 21 | 2 | 9.083174 | 5.888486 | 7.517218 | 4.51158 | 0.944444 | 0.888889 | 0.722222 | 0.826087 | 0.555556 | 0.5 | 4.217391 | BTCUSDT | 1h |

## 7. Warnings / skipped events
- fdf1323995a6b685: invalid risk (risk is not positive; R metrics are skipped)
- 4e75737d7473a0b9: invalid risk (risk is not positive; R metrics are skipped)
- 9168d1c113b9fc1f: invalid risk (risk is not positive; R metrics are skipped)
- ddcb009eb0d2c5f4: invalid risk (risk is not positive; R metrics are skipped)
- d7204617f077d8a1: invalid risk (risk is not positive; R metrics are skipped)

## 8. Interpretation notes
- Replay is bar-by-bar: strategies receive only candles visible at the current bar.
- Forward candles are used only after event detection for outcome measurement.
- `bars_to_*` values are 1-based future bar offsets from the signal bar.
- `*_before_invalidation` uses OHLC bar ordering only; same-bar threshold/invalidation ordering is not modeled.
- HTF-filtered event studies should usually have fewer signals than legacy/off mode.
- If strict signal count does not decrease, HTF gating is too weak.
- If score buckets remain mostly high, scoring is not calibrated enough.
