# Entry Models Backtest Report

Config:
- symbols: BTCUSDT, ETHUSDT, SOLUSDT
- timeframes: 5m, 15m, 30m, 1h, 4h
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
- generated_at: 2026-04-25T23:26:32.699169+00:00

This is an event-study backtest. It does not model fees, slippage, partial exits, breakeven, or full execution management.

## 1. Overall summary
- events: 704
- warnings: 0
- skipped_outcome_events: 56

## 2. Summary by model
| model | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | 324 | 308 | 16 | 268 | 56 | 2.246167 | 1.242285 | 2.109156 | 0.843201 | 0.756494 | 0.577922 | 0.38961 | 0.481481 | 0.49026 | 0.327922 | 4.052469 | ETHUSDT | 30m |
| Entry Model 2 | 342 | 306 | 36 | 297 | 45 | 2.644277 | 1.524155 | 2.074949 | 0.960209 | 0.830065 | 0.643791 | 0.388889 | 0.54386 | 0.51634 | 0.30719 | 4.304094 | SOLUSDT | 30m |
| Entry Model 3 | 38 | 34 | 4 | 34 | 4 | 8.8909 | 5.550841 | 11.385294 | 8.409176 | 0.823529 | 0.794118 | 0.647059 | 0.842105 | 0.529412 | 0.470588 | 4.263158 | BTCUSDT | 1h |

## 3. Summary by direction
| model | direction | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | long | 268 | 254 | 14 | 268 | 0 | 2.104296 | 1.254884 | 1.639151 | 0.838474 | 0.755906 | 0.57874 | 0.377953 | 0.485075 | 0.492126 | 0.318898 | 4.126866 | ETHUSDT | 30m |
| Entry Model 1 | short | 56 | 54 | 2 | 0 | 56 | 2.913488 | 1.18081 | 4.319921 | 0.918485 | 0.759259 | 0.574074 | 0.444444 | 0.464286 | 0.481481 | 0.37037 | 3.696429 | ETHUSDT | 1h |
| Entry Model 2 | long | 297 | 262 | 35 | 297 | 0 | 2.700117 | 1.563237 | 2.050167 | 0.995392 | 0.839695 | 0.656489 | 0.408397 | 0.558923 | 0.522901 | 0.316794 | 4.350168 | SOLUSDT | 30m |
| Entry Model 2 | short | 45 | 44 | 1 | 0 | 45 | 2.311773 | 1.354475 | 2.222516 | 0.951867 | 0.772727 | 0.568182 | 0.272727 | 0.444444 | 0.477273 | 0.25 | 4.0 | ETHUSDT | 4h |
| Entry Model 3 | long | 34 | 30 | 4 | 34 | 0 | 9.602485 | 5.721591 | 11.961628 | 9.109945 | 0.8 | 0.766667 | 0.666667 | 0.823529 | 0.5 | 0.466667 | 4.323529 | BTCUSDT | 1h |
| Entry Model 3 | short | 4 | 4 | 0 | 0 | 4 | 3.554019 | 2.614644 | 7.06279 | 3.205792 | 1.0 | 1.0 | 0.5 | 1.0 | 0.75 | 0.5 | 3.75 | ETHUSDT | 4h |

## 4. Summary by timeframe
| model | timeframe | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | 15m | 72 | 69 | 3 | 72 | 0 | 2.031731 | 1.4 | 1.72182 | 1.0 | 0.768116 | 0.594203 | 0.391304 | 0.527778 | 0.507246 | 0.333333 | 4.347222 | ETHUSDT | 15m |
| Entry Model 1 | 1h | 42 | 40 | 2 | 32 | 10 | 2.152318 | 0.823263 | 3.811675 | 0.801718 | 0.575 | 0.325 | 0.175 | 0.452381 | 0.225 | 0.125 | 3.642857 | ETHUSDT | 1h |
| Entry Model 1 | 30m | 65 | 57 | 8 | 65 | 0 | 2.874419 | 1.403132 | 1.089129 | 0.727857 | 0.807018 | 0.631579 | 0.403509 | 0.4 | 0.578947 | 0.350877 | 4.184615 | ETHUSDT | 30m |
| Entry Model 1 | 4h | 63 | 61 | 2 | 39 | 24 | 2.409584 | 2.037476 | 2.244474 | 0.639867 | 0.819672 | 0.737705 | 0.508197 | 0.301587 | 0.688525 | 0.47541 | 3.47619 | ETHUSDT | 4h |
| Entry Model 1 | 5m | 82 | 81 | 1 | 60 | 22 | 1.910011 | 1.148148 | 2.214251 | 1.624352 | 0.753086 | 0.530864 | 0.395062 | 0.658537 | 0.395062 | 0.296296 | 4.341463 | ETHUSDT | 5m |
| Entry Model 2 | 15m | 86 | 79 | 7 | 86 | 0 | 2.073462 | 1.043594 | 2.053004 | 1.316131 | 0.78481 | 0.544304 | 0.35443 | 0.651163 | 0.455696 | 0.278481 | 4.465116 | SOLUSDT | 15m |
| Entry Model 2 | 1h | 42 | 38 | 4 | 35 | 7 | 3.277415 | 1.75034 | 1.511027 | 0.70605 | 0.894737 | 0.789474 | 0.421053 | 0.428571 | 0.657895 | 0.315789 | 4.0 | SOLUSDT | 1h |
| Entry Model 2 | 30m | 64 | 56 | 8 | 64 | 0 | 4.364796 | 2.188122 | 1.293477 | 0.924756 | 0.928571 | 0.821429 | 0.535714 | 0.546875 | 0.535714 | 0.392857 | 4.421875 | SOLUSDT | 30m |
| Entry Model 2 | 4h | 46 | 44 | 2 | 25 | 21 | 2.73807 | 1.379815 | 2.814448 | 0.797457 | 0.772727 | 0.613636 | 0.386364 | 0.413043 | 0.522727 | 0.340909 | 3.76087 | BTCUSDT | 4h |
| Entry Model 2 | 5m | 104 | 89 | 15 | 87 | 17 | 1.751684 | 1.285714 | 2.461323 | 0.966491 | 0.808989 | 0.573034 | 0.314607 | 0.557692 | 0.494382 | 0.258427 | 4.461538 | SOLUSDT | 5m |
| Entry Model 3 | 15m | 9 | 7 | 2 | 9 | 0 | 2.979176 | 2.53644 | 15.641691 | 11.486486 | 0.857143 | 0.714286 | 0.571429 | 0.888889 | 0.285714 | 0.285714 | 4.777778 | ETHUSDT | 15m |
| Entry Model 3 | 1h | 7 | 6 | 1 | 7 | 0 | 13.777402 | 3.513258 | 7.295664 | 6.509212 | 0.666667 | 0.666667 | 0.5 | 0.714286 | 0.666667 | 0.5 | 4.285714 | BTCUSDT | 1h |

_Showing 12 of 15 rows._

## 5. Score bucket analysis
| model | score_bucket | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | high | 256 | 243 | 13 | 226 | 30 | 2.175694 | 1.260493 | 1.753366 | 0.929539 | 0.761317 | 0.576132 | 0.382716 | 0.507812 | 0.485597 | 0.316872 | 4.335938 | ETHUSDT | 30m |
| Entry Model 1 | low | 1 | 1 | 0 | 1 | 0 | 1.467583 | 1.467583 | 1.051081 | 1.051081 | 1.0 | 1.0 | 0.0 | 1.0 | 0.0 | 0.0 | 2.0 | SOLUSDT | 4h |
| Entry Model 1 | medium | 67 | 64 | 3 | 41 | 26 | 2.525911 | 1.180474 | 3.476581 | 0.742636 | 0.734375 | 0.578125 | 0.421875 | 0.373134 | 0.515625 | 0.375 | 3.0 | ETHUSDT | 1h |
| Entry Model 2 | high | 320 | 286 | 34 | 283 | 37 | 2.66539 | 1.524155 | 2.085065 | 1.029929 | 0.818182 | 0.629371 | 0.391608 | 0.565625 | 0.5 | 0.304196 | 4.396875 | SOLUSDT | 30m |
| Entry Model 2 | low | 1 | 0 | 1 | 1 | 0 |  |  |  |  |  |  |  | 1.0 |  |  | 2.0 |  |  |
| Entry Model 2 | medium | 21 | 20 | 1 | 13 | 8 | 2.342361 | 1.637966 | 1.930301 | 0.330763 | 1.0 | 0.85 | 0.35 | 0.190476 | 0.75 | 0.35 | 3.0 | ETHUSDT | 5m |
| Entry Model 3 | high | 35 | 32 | 3 | 32 | 3 | 7.885497 | 5.550841 | 11.947301 | 9.109945 | 0.8125 | 0.78125 | 0.625 | 0.857143 | 0.5 | 0.4375 | 4.371429 | BTCUSDT | 4h |
| Entry Model 3 | medium | 3 | 2 | 1 | 2 | 1 | 24.977353 | 24.977353 | 2.393187 | 2.393187 | 1.0 | 1.0 | 1.0 | 0.666667 | 1.0 | 1.0 | 3.0 | BTCUSDT | 1h |

## 6. HTF Context Analysis
### Events by HTF bias
| model | htf_bias | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | bearish | 38 | 37 | 1 | 0 | 38 | 2.219663 | 1.713235 | 1.797231 | 0.943143 | 0.810811 | 0.621622 | 0.486486 | 0.473684 | 0.513514 | 0.378378 | 3.947368 | ETHUSDT | 4h |
| Entry Model 1 | bullish | 218 | 204 | 14 | 218 | 0 | 2.22268 | 1.247894 | 1.713978 | 0.830667 | 0.75 | 0.568627 | 0.382353 | 0.472477 | 0.5 | 0.338235 | 4.293578 | ETHUSDT | 30m |
| Entry Model 1 | neutral | 68 | 67 | 1 | 50 | 18 | 2.332317 | 1.152859 | 3.484644 | 1.0 | 0.746269 | 0.58209 | 0.358209 | 0.514706 | 0.447761 | 0.268657 | 3.338235 | ETHUSDT | 1h |
| Entry Model 2 | bearish | 32 | 31 | 1 | 0 | 32 | 2.400268 | 0.929135 | 2.480409 | 0.950346 | 0.677419 | 0.483871 | 0.290323 | 0.46875 | 0.419355 | 0.258065 | 4.09375 | ETHUSDT | 4h |
| Entry Model 2 | bullish | 244 | 218 | 26 | 244 | 0 | 2.71117 | 1.541731 | 2.116475 | 1.048147 | 0.816514 | 0.619266 | 0.40367 | 0.577869 | 0.490826 | 0.307339 | 4.487705 | SOLUSDT | 30m |
| Entry Model 2 | neutral | 66 | 57 | 9 | 53 | 13 | 2.521146 | 1.526316 | 1.69562 | 0.583333 | 0.964912 | 0.824561 | 0.385965 | 0.454545 | 0.666667 | 0.333333 | 3.727273 | BTCUSDT | 30m |
| Entry Model 3 | bearish | 4 | 4 | 0 | 0 | 4 | 3.554019 | 2.614644 | 7.06279 | 3.205792 | 1.0 | 1.0 | 0.5 | 1.0 | 0.75 | 0.5 | 3.75 | ETHUSDT | 4h |
| Entry Model 3 | bullish | 34 | 30 | 4 | 34 | 0 | 9.602485 | 5.721591 | 11.961628 | 9.109945 | 0.8 | 0.766667 | 0.666667 | 0.823529 | 0.5 | 0.466667 | 4.323529 | BTCUSDT | 1h |

### Performance by HTF location
| model | htf_location | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | discount | 144 | 132 | 12 | 112 | 32 | 1.908828 | 1.273104 | 1.768523 | 0.952027 | 0.787879 | 0.583333 | 0.371212 | 0.534722 | 0.507576 | 0.310606 | 4.104167 | ETHUSDT | 4h |
| Entry Model 1 | equilibrium | 59 | 58 | 1 | 48 | 11 | 2.055869 | 1.215191 | 2.069101 | 0.967547 | 0.775862 | 0.568966 | 0.448276 | 0.508475 | 0.431034 | 0.344828 | 3.830508 | BTCUSDT | 30m |
| Entry Model 1 | premium | 121 | 118 | 3 | 108 | 13 | 2.717067 | 1.232151 | 2.509892 | 0.813275 | 0.711864 | 0.576271 | 0.381356 | 0.404959 | 0.5 | 0.338983 | 4.099174 | ETHUSDT | 30m |
| Entry Model 2 | discount | 137 | 121 | 16 | 114 | 23 | 2.678825 | 1.543779 | 2.510059 | 1.164559 | 0.826446 | 0.61157 | 0.413223 | 0.583942 | 0.471074 | 0.305785 | 4.313869 | SOLUSDT | 4h |
| Entry Model 2 | equilibrium | 69 | 60 | 9 | 61 | 8 | 2.449166 | 1.521994 | 1.159779 | 0.596886 | 0.883333 | 0.766667 | 0.383333 | 0.449275 | 0.683333 | 0.35 | 4.101449 | BTCUSDT | 30m |
| Entry Model 2 | premium | 136 | 125 | 11 | 122 | 14 | 2.704488 | 1.485577 | 2.093045 | 1.025974 | 0.808 | 0.616 | 0.368 | 0.551471 | 0.48 | 0.288 | 4.397059 | SOLUSDT | 30m |
| Entry Model 3 | discount | 8 | 7 | 1 | 5 | 3 | 10.035139 | 1.59084 | 11.081877 | 4.135169 | 0.857143 | 0.857143 | 0.428571 | 0.875 | 0.428571 | 0.285714 | 4.0 | BTCUSDT | 4h |
| Entry Model 3 | equilibrium | 7 | 7 | 0 | 6 | 1 | 5.163065 | 5.408501 | 11.475081 | 8.618352 | 0.857143 | 0.857143 | 0.714286 | 0.857143 | 0.428571 | 0.428571 | 4.571429 | ETHUSDT | 30m |
| Entry Model 3 | premium | 23 | 20 | 3 | 23 | 0 | 9.79516 | 5.916895 | 11.460065 | 8.900768 | 0.8 | 0.75 | 0.7 | 0.826087 | 0.6 | 0.55 | 4.26087 | BTCUSDT | 1h |

### Performance by HTF zone type
| model | htf_zone_type | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | Breaker | 70 | 70 | 0 | 67 | 3 | 1.891507 | 1.273104 | 1.686735 | 0.942882 | 0.742857 | 0.542857 | 0.385714 | 0.5 | 0.428571 | 0.285714 | 4.257143 | ETHUSDT | 30m |
| Entry Model 1 | FVG | 82 | 73 | 9 | 72 | 10 | 2.070595 | 1.519889 | 1.847856 | 1.062992 | 0.726027 | 0.60274 | 0.424658 | 0.573171 | 0.493151 | 0.342466 | 4.195122 | ETHUSDT | 5m |
| Entry Model 1 | IFVG | 85 | 81 | 4 | 59 | 26 | 2.624642 | 1.420076 | 3.073567 | 0.734694 | 0.802469 | 0.654321 | 0.444444 | 0.435294 | 0.567901 | 0.395062 | 3.541176 | ETHUSDT | 1h |
| Entry Model 1 | OB | 8 | 7 | 1 | 8 | 0 | 0.603633 | 0.678798 | 2.829485 | 1.627451 | 0.571429 | 0.142857 | 0.0 | 0.625 | 0.142857 | 0.0 | 3.875 | BTCUSDT | 15m |
| Entry Model 1 | PD | 79 | 77 | 2 | 62 | 17 | 2.486223 | 1.167224 | 1.660908 | 0.801969 | 0.766234 | 0.545455 | 0.337662 | 0.405063 | 0.493506 | 0.311688 | 4.291139 | ETHUSDT | 30m |
| Entry Model 2 | Breaker | 77 | 68 | 9 | 75 | 2 | 2.35376 | 1.702158 | 2.125774 | 1.238555 | 0.882353 | 0.661765 | 0.441176 | 0.623377 | 0.470588 | 0.294118 | 4.402597 | BTCUSDT | 1h |
| Entry Model 2 | FVG | 91 | 75 | 16 | 82 | 9 | 2.470392 | 1.582694 | 2.10819 | 1.379822 | 0.786667 | 0.68 | 0.36 | 0.692308 | 0.506667 | 0.28 | 4.395604 | ETHUSDT | 4h |
| Entry Model 2 | IFVG | 91 | 81 | 10 | 71 | 20 | 2.776239 | 1.359223 | 2.262569 | 0.761905 | 0.82716 | 0.62963 | 0.358025 | 0.483516 | 0.530864 | 0.283951 | 4.054945 | BTCUSDT | 30m |
| Entry Model 2 | Liquidity | 1 | 1 | 0 | 1 | 0 | 2.416396 | 2.416396 | 2.024507 | 2.024507 | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 5.0 | BTCUSDT | 30m |
| Entry Model 2 | OB | 4 | 4 | 0 | 4 | 0 | 2.70049 | 2.489689 | 5.032836 | 2.949899 | 1.0 | 1.0 | 0.5 | 0.5 | 1.0 | 0.5 | 4.75 | BTCUSDT | 15m |
| Entry Model 2 | PD | 78 | 77 | 1 | 64 | 14 | 2.931428 | 1.386905 | 1.64732 | 0.774922 | 0.818182 | 0.584416 | 0.38961 | 0.358974 | 0.532468 | 0.363636 | 4.358974 | ETHUSDT | 30m |
| Entry Model 3 | Breaker | 8 | 7 | 1 | 8 | 0 | 5.118515 | 5.408501 | 11.018925 | 8.618352 | 0.857143 | 0.857143 | 0.714286 | 1.0 | 0.428571 | 0.285714 | 4.625 | BTCUSDT | 30m |

_Showing 12 of 16 rows._

### Performance by HTF alignment
| model | htf_alignment | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | aligned | 256 | 241 | 15 | 218 | 38 | 2.222217 | 1.285714 | 1.726759 | 0.830667 | 0.759336 | 0.576763 | 0.39834 | 0.472656 | 0.502075 | 0.344398 | 4.242188 | ETHUSDT | 30m |
| Entry Model 1 | neutral | 68 | 67 | 1 | 50 | 18 | 2.332317 | 1.152859 | 3.484644 | 1.0 | 0.746269 | 0.58209 | 0.358209 | 0.514706 | 0.447761 | 0.268657 | 3.338235 | ETHUSDT | 1h |
| Entry Model 2 | aligned | 276 | 249 | 27 | 244 | 32 | 2.672464 | 1.485577 | 2.161784 | 1.036067 | 0.799197 | 0.60241 | 0.389558 | 0.565217 | 0.481928 | 0.301205 | 4.442029 | SOLUSDT | 30m |
| Entry Model 2 | neutral | 66 | 57 | 9 | 53 | 13 | 2.521146 | 1.526316 | 1.69562 | 0.583333 | 0.964912 | 0.824561 | 0.385965 | 0.454545 | 0.666667 | 0.333333 | 3.727273 | BTCUSDT | 30m |
| Entry Model 3 | aligned | 38 | 34 | 4 | 34 | 4 | 8.8909 | 5.550841 | 11.385294 | 8.409176 | 0.823529 | 0.794118 | 0.647059 | 0.842105 | 0.529412 | 0.470588 | 4.263158 | BTCUSDT | 1h |

### Performance by displacement
| model | displacement | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | has_displacement | 206 | 200 | 6 | 173 | 33 | 2.464038 | 1.401566 | 2.275382 | 0.754096 | 0.79 | 0.62 | 0.405 | 0.402913 | 0.555 | 0.365 | 4.218447 | ETHUSDT | 30m |
| Entry Model 1 | weak_or_none | 118 | 108 | 10 | 95 | 23 | 1.842703 | 0.99616 | 1.801332 | 1.232975 | 0.694444 | 0.5 | 0.361111 | 0.618644 | 0.37037 | 0.259259 | 3.762712 | BTCUSDT | 4h |
| Entry Model 2 | has_displacement | 342 | 306 | 36 | 297 | 45 | 2.644277 | 1.524155 | 2.074949 | 0.960209 | 0.830065 | 0.643791 | 0.388889 | 0.54386 | 0.51634 | 0.30719 | 4.304094 | SOLUSDT | 30m |
| Entry Model 3 | has_displacement | 28 | 25 | 3 | 27 | 1 | 7.598663 | 5.693182 | 13.255928 | 10.290493 | 0.84 | 0.8 | 0.68 | 0.892857 | 0.48 | 0.44 | 4.464286 | BTCUSDT | 4h |
| Entry Model 3 | weak_or_none | 10 | 9 | 1 | 7 | 3 | 12.48045 | 3.706717 | 6.189088 | 2.276414 | 0.777778 | 0.777778 | 0.555556 | 0.7 | 0.666667 | 0.555556 | 3.7 | BTCUSDT | 1h |

### Performance by FVG status
| model | fvg_status | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | filled | 43 | 42 | 1 | 37 | 6 | 1.66327 | 1.232151 | 2.120249 | 0.942882 | 0.666667 | 0.571429 | 0.404762 | 0.511628 | 0.452381 | 0.333333 | 4.0 | SOLUSDT | 5m |
| Entry Model 1 | open | 193 | 179 | 14 | 161 | 32 | 2.520059 | 1.507937 | 2.287301 | 0.827345 | 0.804469 | 0.608939 | 0.424581 | 0.471503 | 0.547486 | 0.363128 | 4.103627 | ETHUSDT | 1h |
| Entry Model 1 | partially_filled | 88 | 87 | 1 | 70 | 18 | 1.964043 | 1.032129 | 1.737275 | 0.873805 | 0.701149 | 0.517241 | 0.310345 | 0.488636 | 0.390805 | 0.252874 | 3.965909 | ETHUSDT | 30m |
| Entry Model 2 | unknown | 342 | 306 | 36 | 297 | 45 | 2.644277 | 1.524155 | 2.074949 | 0.960209 | 0.830065 | 0.643791 | 0.388889 | 0.54386 | 0.51634 | 0.30719 | 4.304094 | SOLUSDT | 30m |
| Entry Model 3 | filled | 23 | 21 | 2 | 22 | 1 | 4.139848 | 3.706717 | 10.71637 | 8.2 | 0.714286 | 0.666667 | 0.619048 | 0.913043 | 0.380952 | 0.380952 | 4.521739 | ETHUSDT | 30m |
| Entry Model 3 | partially_filled | 15 | 13 | 2 | 12 | 3 | 16.565678 | 7.798956 | 12.465865 | 10.054054 | 1.0 | 1.0 | 0.692308 | 0.733333 | 0.769231 | 0.615385 | 3.866667 | BTCUSDT | 1h |

### Model 3 fill variants
| model | fill_mode | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | none | 324 | 308 | 16 | 268 | 56 | 2.246167 | 1.242285 | 2.109156 | 0.843201 | 0.756494 | 0.577922 | 0.38961 | 0.481481 | 0.49026 | 0.327922 | 4.052469 | ETHUSDT | 30m |
| Entry Model 2 | none | 342 | 306 | 36 | 297 | 45 | 2.644277 | 1.524155 | 2.074949 | 0.960209 | 0.830065 | 0.643791 | 0.388889 | 0.54386 | 0.51634 | 0.30719 | 4.304094 | SOLUSDT | 30m |
| Entry Model 3 | 50 | 38 | 34 | 4 | 34 | 4 | 8.8909 | 5.550841 | 11.385294 | 8.409176 | 0.823529 | 0.794118 | 0.647059 | 0.842105 | 0.529412 | 0.470588 | 4.263158 | BTCUSDT | 1h |

## 7. Warnings / skipped events
- 917dc1b537485181: invalid risk (risk is not positive; R metrics are skipped)
- 479d219d563d55b2: invalid risk (risk is not positive; R metrics are skipped)
- ce2533422034cb90: invalid risk (risk is not positive; R metrics are skipped)
- fdf1323995a6b685: invalid risk (risk is not positive; R metrics are skipped)
- 518afc53a0dcda4f: invalid risk (risk is not positive; R metrics are skipped)
- 8e975dd5f45ac963: invalid risk (risk is not positive; R metrics are skipped)
- db2e20c81b720f6a: invalid risk (risk is not positive; R metrics are skipped)
- c0f43ca80b72d0e8: invalid risk (risk is not positive; R metrics are skipped)
- ed38165a11b270be: invalid risk (risk is not positive; R metrics are skipped)
- d64de26f9700a25c: invalid risk (risk is not positive; R metrics are skipped)
- 340e1e9d1b0bb21c: invalid risk (risk is not positive; R metrics are skipped)
- 06860f7b51ff5f0a: invalid risk (risk is not positive; R metrics are skipped)
- ddcb009eb0d2c5f4: invalid risk (risk is not positive; R metrics are skipped)
- 4759871c5dac9c6d: invalid risk (risk is not positive; R metrics are skipped)
- d7204617f077d8a1: invalid risk (risk is not positive; R metrics are skipped)
- 2f21a7ed990b9fd2: invalid risk (risk is not positive; R metrics are skipped)
- d285e3c7a007f459: invalid risk (risk is not positive; R metrics are skipped)
- 01d7537118f9856f: invalid risk (risk is not positive; R metrics are skipped)
- 82028fe72e863f45: invalid risk (risk is not positive; R metrics are skipped)
- eb1eac624c96c95d: invalid risk (risk is not positive; R metrics are skipped)
- 2ab51e347ee4df41: invalid risk (risk is not positive; R metrics are skipped)
- 67d186eb9d03e6eb: invalid risk (risk is not positive; R metrics are skipped)
- ec42764d0b171114: invalid risk (risk is not positive; R metrics are skipped)
- b1c410e40bae21ff: invalid risk (risk is not positive; R metrics are skipped)
- 3abde9622224138e: invalid risk (risk is not positive; R metrics are skipped)
- 36fae33f7e0d6eeb: invalid risk (risk is not positive; R metrics are skipped)
- edc4c8ba31d4961e: invalid risk (risk is not positive; R metrics are skipped)
- 4967bff51eea0b12: invalid risk (risk is not positive; R metrics are skipped)
- da978be822fa5209: invalid risk (risk is not positive; R metrics are skipped)
- 655fb7daa73c1dea: invalid risk (risk is not positive; R metrics are skipped)
- 309a8885517352b6: invalid risk (risk is not positive; R metrics are skipped)
- faf6a96ff5d91835: invalid risk (risk is not positive; R metrics are skipped)
- 04607441452e9f34: invalid risk (risk is not positive; R metrics are skipped)
- bf0f77290ffaf13f: invalid risk (risk is not positive; R metrics are skipped)
- 3d24de278676cd2f: invalid risk (risk is not positive; R metrics are skipped)
- 49f1fdfc7b0948a3: invalid risk (risk is not positive; R metrics are skipped)
- 0fea612819ffb9bd: invalid risk (risk is not positive; R metrics are skipped)
- d1a4b1868e626b60: invalid risk (risk is not positive; R metrics are skipped)
- c55ef56032c093f9: invalid risk (risk is not positive; R metrics are skipped)
- 6151470382c39fa6: invalid risk (risk is not positive; R metrics are skipped)
- 77cf767ecf0bfeff: invalid risk (risk is not positive; R metrics are skipped)
- 95eaa0bae40360eb: invalid risk (risk is not positive; R metrics are skipped)
- 6c4eefcb916c7c6c: invalid risk (risk is not positive; R metrics are skipped)
- 5612da6c213877d5: invalid risk (risk is not positive; R metrics are skipped)
- a40f3f44fe561848: invalid risk (risk is not positive; R metrics are skipped)
- 0da0555c2f99420d: invalid risk (risk is not positive; R metrics are skipped)
- 84dae0026407750f: invalid risk (risk is not positive; R metrics are skipped)
- 7ae092a18dc8300f: invalid risk (risk is not positive; R metrics are skipped)
- 0d73a56f97c32c00: invalid risk (risk is not positive; R metrics are skipped)
- f1debc565de0e518: invalid risk (risk is not positive; R metrics are skipped)

## 8. Interpretation notes
- Replay is bar-by-bar: strategies receive only candles visible at the current bar.
- Forward candles are used only after event detection for outcome measurement.
- `bars_to_*` values are 1-based future bar offsets from the signal bar.
- `*_before_invalidation` uses OHLC bar ordering only; same-bar threshold/invalidation ordering is not modeled.
- HTF-filtered event studies should usually have fewer signals than legacy/off mode.
- If strict signal count does not decrease, HTF gating is too weak.
- If score buckets remain mostly high, scoring is not calibrated enough.
