# Entry Models Backtest Report

Config:
- symbols: BTCUSDT
- timeframes: 5m, 15m
- models: model1, model2, model3
- warmup_bars: 100
- forward_bars: 20
- cooldown_bars: 5
- start: full history
- end: full history
- htf_mode: strict
- require_displacement: True
- model3_fill_threshold: 0.5
- execution_pairs: {'1m': '15m', '3m': '30m', '5m': '1h', '15m': '4h', '30m': '4h', '1h': '1d'}
- model_3_htf_map: {'1m': '15m', '3m': '30m', '5m': '1h', '15m': '4h', '30m': '4h', '1h': '1d', '4h': '1d'}
- model_3_ltf_map: {'5m': '1m', '15m': '3m', '30m': '5m', '1h': '15m', '4h': '1h'}
- generated_at: 2026-04-25T23:02:48.878477+00:00

This is an event-study backtest. It does not model fees, slippage, partial exits, breakeven, or full execution management.

## 1. Overall summary
- events: 117
- warnings: 0
- skipped_outcome_events: 5

## 2. Summary by model
| model | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | 49 | 49 | 0 | 32 | 17 | 1.53751 | 0.924933 | 3.02902 | 2.076087 | 0.714286 | 0.44898 | 0.326531 | 0.673469 | 0.367347 | 0.244898 | 4.469388 | BTCUSDT | 5m |
| Entry Model 2 | 61 | 57 | 4 | 48 | 13 | 1.660089 | 0.954858 | 2.979461 | 1.793522 | 0.754386 | 0.491228 | 0.315789 | 0.606557 | 0.438596 | 0.280702 | 4.590164 | BTCUSDT | 15m |
| Entry Model 3 | 7 | 6 | 1 | 5 | 2 | 2.410294 | 1.711016 | 8.407682 | 2.814334 | 1.0 | 0.833333 | 0.333333 | 0.857143 | 0.5 | 0.333333 | 4.428571 | BTCUSDT | 15m |

## 3. Summary by direction
| model | direction | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | long | 32 | 32 | 0 | 32 | 0 | 1.178869 | 0.915093 | 3.47607 | 2.206022 | 0.65625 | 0.375 | 0.25 | 0.6875 | 0.34375 | 0.21875 | 4.46875 | BTCUSDT | 15m |
| Entry Model 1 | short | 17 | 17 | 0 | 0 | 17 | 2.212598 | 1.713235 | 2.187514 | 1.959896 | 0.823529 | 0.588235 | 0.470588 | 0.647059 | 0.411765 | 0.294118 | 4.470588 | BTCUSDT | 5m |
| Entry Model 2 | long | 48 | 44 | 4 | 48 | 0 | 1.7271 | 1.043594 | 3.215783 | 2.031189 | 0.795455 | 0.522727 | 0.340909 | 0.645833 | 0.477273 | 0.295455 | 4.604167 | BTCUSDT | 15m |
| Entry Model 2 | short | 13 | 13 | 0 | 0 | 13 | 1.433281 | 0.885057 | 2.179601 | 0.966491 | 0.615385 | 0.384615 | 0.230769 | 0.461538 | 0.307692 | 0.230769 | 4.538462 | BTCUSDT | 5m |
| Entry Model 3 | long | 5 | 4 | 1 | 5 | 0 | 2.937839 | 2.21795 | 11.577303 | 7.41937 | 1.0 | 0.75 | 0.5 | 0.8 | 0.5 | 0.5 | 4.6 | BTCUSDT | 15m |
| Entry Model 3 | short | 2 | 2 | 0 | 0 | 2 | 1.355203 | 1.355203 | 2.06844 | 2.06844 | 1.0 | 1.0 | 0.0 | 1.0 | 0.5 | 0.0 | 4.0 | BTCUSDT | 5m |

## 4. Summary by timeframe
| model | timeframe | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | 15m | 22 | 22 | 0 | 22 | 0 | 1.261956 | 0.915093 | 2.523101 | 1.396592 | 0.636364 | 0.409091 | 0.272727 | 0.590909 | 0.363636 | 0.227273 | 4.363636 | BTCUSDT | 15m |
| Entry Model 1 | 5m | 27 | 27 | 0 | 10 | 17 | 1.762035 | 0.986755 | 3.441251 | 2.331092 | 0.777778 | 0.481481 | 0.37037 | 0.740741 | 0.37037 | 0.259259 | 4.555556 | BTCUSDT | 5m |
| Entry Model 2 | 15m | 37 | 34 | 3 | 37 | 0 | 1.862805 | 1.043594 | 2.626609 | 1.716205 | 0.764706 | 0.529412 | 0.352941 | 0.621622 | 0.470588 | 0.294118 | 4.621622 | BTCUSDT | 15m |
| Entry Model 2 | 5m | 24 | 23 | 1 | 11 | 13 | 1.360421 | 0.885057 | 3.501069 | 2.146506 | 0.73913 | 0.434783 | 0.26087 | 0.583333 | 0.391304 | 0.26087 | 4.541667 | BTCUSDT | 5m |
| Entry Model 3 | 15m | 5 | 4 | 1 | 5 | 0 | 2.937839 | 2.21795 | 11.577303 | 7.41937 | 1.0 | 0.75 | 0.5 | 0.8 | 0.5 | 0.5 | 4.6 | BTCUSDT | 15m |
| Entry Model 3 | 5m | 2 | 2 | 0 | 0 | 2 | 1.355203 | 1.355203 | 2.06844 | 2.06844 | 1.0 | 1.0 | 0.0 | 1.0 | 0.5 | 0.0 | 4.0 | BTCUSDT | 5m |

## 5. Score bucket analysis
| model | score_bucket | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | high | 47 | 47 | 0 | 31 | 16 | 1.484055 | 0.924933 | 3.065352 | 2.076087 | 0.723404 | 0.446809 | 0.319149 | 0.680851 | 0.361702 | 0.234043 | 4.531915 | BTCUSDT | 5m |
| Entry Model 1 | medium | 2 | 2 | 0 | 1 | 1 | 2.793693 | 2.793693 | 2.175231 | 2.175231 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 3.0 | BTCUSDT | 5m |
| Entry Model 2 | high | 61 | 57 | 4 | 48 | 13 | 1.660089 | 0.954858 | 2.979461 | 1.793522 | 0.754386 | 0.491228 | 0.315789 | 0.606557 | 0.438596 | 0.280702 | 4.590164 | BTCUSDT | 15m |
| Entry Model 3 | high | 7 | 6 | 1 | 5 | 2 | 2.410294 | 1.711016 | 8.407682 | 2.814334 | 1.0 | 0.833333 | 0.333333 | 0.857143 | 0.5 | 0.333333 | 4.428571 | BTCUSDT | 15m |

## 6. HTF Context Analysis
### Events by HTF bias
| model | htf_bias | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | bearish | 15 | 15 | 0 | 0 | 15 | 1.968249 | 1.308108 | 2.418688 | 2.076087 | 0.8 | 0.533333 | 0.4 | 0.733333 | 0.333333 | 0.2 | 4.6 | BTCUSDT | 5m |
| Entry Model 1 | bullish | 32 | 32 | 0 | 32 | 0 | 1.178869 | 0.915093 | 3.47607 | 2.206022 | 0.65625 | 0.375 | 0.25 | 0.6875 | 0.34375 | 0.21875 | 4.46875 | BTCUSDT | 15m |
| Entry Model 1 | neutral | 2 | 2 | 0 | 0 | 2 | 4.045222 | 4.045222 | 0.453715 | 0.453715 | 1.0 | 1.0 | 1.0 | 0.0 | 1.0 | 1.0 | 3.5 | BTCUSDT | 5m |
| Entry Model 2 | bearish | 8 | 8 | 0 | 0 | 8 | 0.593668 | 0.192971 | 3.124424 | 2.800773 | 0.375 | 0.25 | 0.125 | 0.75 | 0.125 | 0.125 | 4.875 | BTCUSDT | 5m |
| Entry Model 2 | bullish | 48 | 44 | 4 | 48 | 0 | 1.7271 | 1.043594 | 3.215783 | 2.031189 | 0.795455 | 0.522727 | 0.340909 | 0.645833 | 0.477273 | 0.295455 | 4.604167 | BTCUSDT | 15m |
| Entry Model 2 | neutral | 5 | 5 | 0 | 0 | 5 | 2.776662 | 1.800312 | 0.667885 | 0.867769 | 1.0 | 0.6 | 0.4 | 0.0 | 0.6 | 0.4 | 4.0 | BTCUSDT | 5m |
| Entry Model 3 | bearish | 2 | 2 | 0 | 0 | 2 | 1.355203 | 1.355203 | 2.06844 | 2.06844 | 1.0 | 1.0 | 0.0 | 1.0 | 0.5 | 0.0 | 4.0 | BTCUSDT | 5m |
| Entry Model 3 | bullish | 5 | 4 | 1 | 5 | 0 | 2.937839 | 2.21795 | 11.577303 | 7.41937 | 1.0 | 0.75 | 0.5 | 0.8 | 0.5 | 0.5 | 4.6 | BTCUSDT | 15m |

### Performance by HTF location
| model | htf_location | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | discount | 28 | 28 | 0 | 15 | 13 | 1.220887 | 0.797375 | 3.530103 | 2.424456 | 0.678571 | 0.357143 | 0.25 | 0.785714 | 0.25 | 0.142857 | 4.607143 | BTCUSDT | 5m |
| Entry Model 1 | equilibrium | 6 | 6 | 0 | 5 | 1 | 2.621901 | 2.528902 | 4.017983 | 4.496934 | 0.833333 | 0.833333 | 0.666667 | 0.666667 | 0.833333 | 0.666667 | 4.5 | BTCUSDT | 5m |
| Entry Model 1 | premium | 15 | 15 | 0 | 12 | 3 | 1.694784 | 0.915485 | 1.698081 | 0.90743 | 0.733333 | 0.466667 | 0.333333 | 0.466667 | 0.4 | 0.266667 | 4.2 | BTCUSDT | 5m |
| Entry Model 2 | discount | 22 | 20 | 2 | 16 | 6 | 1.275672 | 0.830479 | 4.322834 | 3.078034 | 0.7 | 0.45 | 0.3 | 0.727273 | 0.35 | 0.25 | 4.681818 | BTCUSDT | 15m |
| Entry Model 2 | equilibrium | 8 | 8 | 0 | 8 | 0 | 1.930848 | 1.944433 | 1.867855 | 1.269057 | 0.625 | 0.625 | 0.5 | 0.5 | 0.625 | 0.5 | 4.75 | BTCUSDT | 15m |
| Entry Model 2 | premium | 31 | 29 | 2 | 24 | 7 | 1.850512 | 0.954858 | 2.359647 | 1.036067 | 0.827586 | 0.482759 | 0.275862 | 0.548387 | 0.448276 | 0.241379 | 4.483871 | BTCUSDT | 5m |
| Entry Model 3 | discount | 2 | 2 | 0 | 0 | 2 | 1.355203 | 1.355203 | 2.06844 | 2.06844 | 1.0 | 1.0 | 0.0 | 1.0 | 0.5 | 0.0 | 4.0 | BTCUSDT | 5m |
| Entry Model 3 | equilibrium | 2 | 2 | 0 | 2 | 0 | 2.21795 | 2.21795 | 5.743243 | 5.743243 | 1.0 | 1.0 | 0.5 | 0.5 | 0.5 | 0.5 | 5.0 | BTCUSDT | 15m |
| Entry Model 3 | premium | 3 | 2 | 1 | 3 | 0 | 3.657729 | 3.657729 | 17.411363 | 17.411363 | 1.0 | 0.5 | 0.5 | 1.0 | 0.5 | 0.5 | 4.333333 | BTCUSDT | 15m |

### Performance by HTF zone type
| model | htf_zone_type | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | Breaker | 12 | 12 | 0 | 9 | 3 | 1.454062 | 0.958741 | 3.654998 | 2.413558 | 0.833333 | 0.416667 | 0.333333 | 0.666667 | 0.416667 | 0.333333 | 4.583333 | BTCUSDT | 5m |
| Entry Model 1 | FVG | 14 | 14 | 0 | 12 | 2 | 1.626468 | 0.581507 | 2.237624 | 1.957415 | 0.5 | 0.357143 | 0.285714 | 0.714286 | 0.214286 | 0.142857 | 4.071429 | BTCUSDT | 5m |
| Entry Model 1 | IFVG | 3 | 3 | 0 | 1 | 2 | 3.383956 | 2.95067 | 0.310488 | 0.024035 | 1.0 | 1.0 | 1.0 | 0.0 | 1.0 | 1.0 | 4.0 | BTCUSDT | 5m |
| Entry Model 1 | OB | 1 | 1 | 0 | 1 | 0 | 1.027078 | 1.027078 | 7.104929 | 7.104929 | 1.0 | 1.0 | 0.0 | 1.0 | 1.0 | 0.0 | 4.0 | BTCUSDT | 15m |
| Entry Model 1 | PD | 19 | 19 | 0 | 9 | 10 | 1.259986 | 0.915093 | 3.431519 | 2.076087 | 0.736842 | 0.421053 | 0.263158 | 0.736842 | 0.315789 | 0.157895 | 4.789474 | BTCUSDT | 15m |
| Entry Model 2 | Breaker | 17 | 16 | 1 | 15 | 2 | 1.567692 | 1.411145 | 3.079767 | 2.162956 | 0.875 | 0.625 | 0.375 | 0.647059 | 0.625 | 0.375 | 4.705882 | BTCUSDT | 15m |
| Entry Model 2 | FVG | 13 | 12 | 1 | 13 | 0 | 2.0974 | 0.919676 | 2.127024 | 1.778657 | 0.666667 | 0.416667 | 0.333333 | 0.692308 | 0.333333 | 0.25 | 4.769231 | BTCUSDT | 15m |
| Entry Model 2 | IFVG | 8 | 6 | 2 | 3 | 5 | 2.697033 | 2.049599 | 1.660042 | 0.91713 | 1.0 | 0.666667 | 0.5 | 0.375 | 0.5 | 0.333333 | 4.0 | BTCUSDT | 5m |
| Entry Model 2 | OB | 1 | 1 | 0 | 1 | 0 | 3.393398 | 3.393398 | 14.231545 | 14.231545 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 5.0 | BTCUSDT | 15m |
| Entry Model 2 | PD | 22 | 22 | 0 | 16 | 6 | 1.127163 | 0.694192 | 3.21986 | 1.792245 | 0.636364 | 0.363636 | 0.181818 | 0.590909 | 0.318182 | 0.181818 | 4.590909 | BTCUSDT | 15m |
| Entry Model 3 | FVG | 3 | 2 | 1 | 3 | 0 | 3.657729 | 3.657729 | 17.411363 | 17.411363 | 1.0 | 0.5 | 0.5 | 1.0 | 0.5 | 0.5 | 4.333333 | BTCUSDT | 15m |
| Entry Model 3 | PD | 4 | 4 | 0 | 2 | 2 | 1.786576 | 1.711016 | 3.905841 | 2.06844 | 1.0 | 1.0 | 0.25 | 0.75 | 0.5 | 0.25 | 4.5 | BTCUSDT | 15m |

### Performance by HTF alignment
| model | htf_alignment | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | aligned | 47 | 47 | 0 | 32 | 15 | 1.430799 | 0.915485 | 3.138608 | 2.102747 | 0.702128 | 0.425532 | 0.297872 | 0.702128 | 0.340426 | 0.212766 | 4.510638 | BTCUSDT | 5m |
| Entry Model 1 | neutral | 2 | 2 | 0 | 0 | 2 | 4.045222 | 4.045222 | 0.453715 | 0.453715 | 1.0 | 1.0 | 1.0 | 0.0 | 1.0 | 1.0 | 3.5 | BTCUSDT | 5m |
| Entry Model 2 | aligned | 56 | 52 | 4 | 48 | 8 | 1.552726 | 0.94795 | 3.201728 | 2.146506 | 0.730769 | 0.480769 | 0.307692 | 0.660714 | 0.423077 | 0.269231 | 4.642857 | BTCUSDT | 15m |
| Entry Model 2 | neutral | 5 | 5 | 0 | 0 | 5 | 2.776662 | 1.800312 | 0.667885 | 0.867769 | 1.0 | 0.6 | 0.4 | 0.0 | 0.6 | 0.4 | 4.0 | BTCUSDT | 5m |
| Entry Model 3 | aligned | 7 | 6 | 1 | 5 | 2 | 2.410294 | 1.711016 | 8.407682 | 2.814334 | 1.0 | 0.833333 | 0.333333 | 0.857143 | 0.5 | 0.333333 | 4.428571 | BTCUSDT | 15m |

### Performance by displacement
| model | displacement | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | has_displacement | 26 | 26 | 0 | 17 | 9 | 1.332132 | 0.915289 | 2.996218 | 1.684923 | 0.730769 | 0.346154 | 0.307692 | 0.576923 | 0.346154 | 0.307692 | 4.846154 | BTCUSDT | 15m |
| Entry Model 1 | weak_or_none | 23 | 23 | 0 | 15 | 8 | 1.769677 | 1.181107 | 3.066101 | 2.590666 | 0.695652 | 0.565217 | 0.347826 | 0.782609 | 0.391304 | 0.173913 | 4.043478 | BTCUSDT | 5m |
| Entry Model 2 | has_displacement | 61 | 57 | 4 | 48 | 13 | 1.660089 | 0.954858 | 2.979461 | 1.793522 | 0.754386 | 0.491228 | 0.315789 | 0.606557 | 0.438596 | 0.280702 | 4.590164 | BTCUSDT | 15m |
| Entry Model 3 | has_displacement | 5 | 4 | 1 | 5 | 0 | 2.937839 | 2.21795 | 11.577303 | 7.41937 | 1.0 | 0.75 | 0.5 | 0.8 | 0.5 | 0.5 | 4.6 | BTCUSDT | 15m |
| Entry Model 3 | weak_or_none | 2 | 2 | 0 | 0 | 2 | 1.355203 | 1.355203 | 2.06844 | 2.06844 | 1.0 | 1.0 | 0.0 | 1.0 | 0.5 | 0.0 | 4.0 | BTCUSDT | 5m |

### Performance by FVG status
| model | fvg_status | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | filled | 6 | 6 | 0 | 5 | 1 | 1.801959 | 0.581429 | 3.787314 | 3.354065 | 0.5 | 0.333333 | 0.333333 | 1.0 | 0.166667 | 0.166667 | 4.333333 | BTCUSDT | 5m |
| Entry Model 1 | open | 33 | 33 | 0 | 22 | 11 | 1.585457 | 0.930727 | 2.210629 | 1.557763 | 0.757576 | 0.454545 | 0.333333 | 0.575758 | 0.393939 | 0.272727 | 4.393939 | BTCUSDT | 5m |
| Entry Model 1 | partially_filled | 10 | 10 | 0 | 5 | 5 | 1.220615 | 0.971086 | 5.274735 | 3.552583 | 0.7 | 0.5 | 0.3 | 0.8 | 0.4 | 0.2 | 4.8 | BTCUSDT | 15m |
| Entry Model 2 | unknown | 61 | 57 | 4 | 48 | 13 | 1.660089 | 0.954858 | 2.979461 | 1.793522 | 0.754386 | 0.491228 | 0.315789 | 0.606557 | 0.438596 | 0.280702 | 4.590164 | BTCUSDT | 15m |
| Entry Model 3 | filled | 4 | 4 | 0 | 4 | 0 | 2.937839 | 2.21795 | 11.577303 | 7.41937 | 1.0 | 0.75 | 0.5 | 0.75 | 0.5 | 0.5 | 4.75 | BTCUSDT | 15m |
| Entry Model 3 | partially_filled | 3 | 2 | 1 | 1 | 2 | 1.355203 | 1.355203 | 2.06844 | 2.06844 | 1.0 | 1.0 | 0.0 | 1.0 | 0.5 | 0.0 | 4.0 | BTCUSDT | 5m |

### Model 3 fill variants
| model | fill_mode | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | none | 49 | 49 | 0 | 32 | 17 | 1.53751 | 0.924933 | 3.02902 | 2.076087 | 0.714286 | 0.44898 | 0.326531 | 0.673469 | 0.367347 | 0.244898 | 4.469388 | BTCUSDT | 5m |
| Entry Model 2 | none | 61 | 57 | 4 | 48 | 13 | 1.660089 | 0.954858 | 2.979461 | 1.793522 | 0.754386 | 0.491228 | 0.315789 | 0.606557 | 0.438596 | 0.280702 | 4.590164 | BTCUSDT | 15m |
| Entry Model 3 | 50 | 7 | 6 | 1 | 5 | 2 | 2.410294 | 1.711016 | 8.407682 | 2.814334 | 1.0 | 0.833333 | 0.333333 | 0.857143 | 0.5 | 0.333333 | 4.428571 | BTCUSDT | 15m |

## 7. Warnings / skipped events
- d64de26f9700a25c: invalid risk (risk is not positive; R metrics are skipped)
- 340e1e9d1b0bb21c: invalid risk (risk is not positive; R metrics are skipped)
- 06860f7b51ff5f0a: invalid risk (risk is not positive; R metrics are skipped)
- 4759871c5dac9c6d: invalid risk (risk is not positive; R metrics are skipped)
- d7204617f077d8a1: invalid risk (risk is not positive; R metrics are skipped)

## 8. Interpretation notes
- Replay is bar-by-bar: strategies receive only candles visible at the current bar.
- Forward candles are used only after event detection for outcome measurement.
- `bars_to_*` values are 1-based future bar offsets from the signal bar.
- `*_before_invalidation` uses OHLC bar ordering only; same-bar threshold/invalidation ordering is not modeled.
- HTF-filtered event studies should usually have fewer signals than legacy/off mode.
- If strict signal count does not decrease, HTF gating is too weak.
- If score buckets remain mostly high, scoring is not calibrated enough.
