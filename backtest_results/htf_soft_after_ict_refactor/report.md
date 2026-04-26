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
- htf_mode: soft
- require_displacement: True
- model3_fill_threshold: 0.5
- execution_pairs: {'1m': '15m', '3m': '30m', '5m': '1h', '15m': '4h', '30m': '4h', '1h': '1d'}
- model_3_htf_map: {'1m': '15m', '3m': '30m', '5m': '1h', '15m': '4h', '30m': '4h', '1h': '1d', '4h': '1d'}
- model_3_ltf_map: {'5m': '1m', '15m': '3m', '30m': '5m', '1h': '15m', '4h': '1h'}
- generated_at: 2026-04-25T23:19:55.352446+00:00

This is an event-study backtest. It does not model fees, slippage, partial exits, breakeven, or full execution management.

## 1. Overall summary
- events: 1440
- warnings: 0
- skipped_outcome_events: 138

## 2. Summary by model
| model | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | 667 | 618 | 49 | 382 | 285 | 2.151696 | 1.221309 | 1.950258 | 0.921141 | 0.752427 | 0.566343 | 0.331715 | 0.517241 | 0.475728 | 0.268608 | 3.670165 | ETHUSDT | 30m |
| Entry Model 2 | 685 | 604 | 81 | 410 | 275 | 2.673317 | 1.403879 | 2.077933 | 1.036769 | 0.80298 | 0.60596 | 0.377483 | 0.582482 | 0.478477 | 0.266556 | 3.875912 | SOLUSDT | 30m |
| Entry Model 3 | 88 | 80 | 8 | 47 | 41 | 9.254832 | 5.619318 | 10.742852 | 7.152893 | 0.8375 | 0.7875 | 0.6875 | 0.886364 | 0.5125 | 0.425 | 3.852273 | ETHUSDT | 1h |

## 3. Summary by direction
| model | direction | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | long | 382 | 360 | 22 | 382 | 0 | 2.077507 | 1.293247 | 1.649264 | 0.832572 | 0.769444 | 0.586111 | 0.344444 | 0.486911 | 0.491667 | 0.280556 | 3.908377 | ETHUSDT | 30m |
| Entry Model 1 | short | 285 | 258 | 27 | 0 | 285 | 2.255216 | 1.126726 | 2.370248 | 1.066968 | 0.728682 | 0.53876 | 0.313953 | 0.557895 | 0.453488 | 0.251938 | 3.350877 | ETHUSDT | 4h |
| Entry Model 2 | long | 410 | 360 | 50 | 410 | 0 | 2.590914 | 1.556648 | 1.853871 | 0.917895 | 0.836111 | 0.644444 | 0.394444 | 0.543902 | 0.522222 | 0.294444 | 4.141463 | SOLUSDT | 30m |
| Entry Model 2 | short | 275 | 244 | 31 | 0 | 275 | 2.794895 | 1.278035 | 2.408517 | 1.314291 | 0.754098 | 0.54918 | 0.352459 | 0.64 | 0.413934 | 0.22541 | 3.48 | SOLUSDT | 4h |
| Entry Model 3 | long | 47 | 43 | 4 | 47 | 0 | 11.733497 | 5.75 | 12.630792 | 8.618352 | 0.837209 | 0.767442 | 0.697674 | 0.851064 | 0.511628 | 0.465116 | 4.06383 | ETHUSDT | 1h |
| Entry Model 3 | short | 41 | 37 | 4 | 0 | 41 | 6.374221 | 4.0 | 8.54876 | 5.465364 | 0.837838 | 0.810811 | 0.675676 | 0.926829 | 0.513514 | 0.378378 | 3.609756 | SOLUSDT | 1h |

## 4. Summary by timeframe
| model | timeframe | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | 15m | 136 | 126 | 10 | 88 | 48 | 1.954169 | 1.456113 | 1.658653 | 1.007692 | 0.801587 | 0.611111 | 0.373016 | 0.544118 | 0.507937 | 0.293651 | 4.029412 | ETHUSDT | 15m |
| Entry Model 1 | 1h | 105 | 90 | 15 | 56 | 49 | 1.932651 | 0.860674 | 2.536091 | 0.853863 | 0.666667 | 0.411111 | 0.188889 | 0.552381 | 0.355556 | 0.166667 | 3.304762 | ETHUSDT | 1h |
| Entry Model 1 | 30m | 126 | 110 | 16 | 78 | 48 | 2.439014 | 1.415852 | 1.922681 | 0.880533 | 0.790909 | 0.609091 | 0.363636 | 0.531746 | 0.518182 | 0.290909 | 3.81746 | ETHUSDT | 30m |
| Entry Model 1 | 4h | 168 | 164 | 4 | 77 | 91 | 2.431518 | 1.263467 | 1.861208 | 0.74045 | 0.756098 | 0.609756 | 0.347561 | 0.410714 | 0.530488 | 0.29878 | 3.107143 | SOLUSDT | 4h |
| Entry Model 1 | 5m | 132 | 128 | 4 | 83 | 49 | 1.894717 | 1.13771 | 1.963186 | 1.374183 | 0.726562 | 0.539062 | 0.34375 | 0.583333 | 0.421875 | 0.257812 | 4.166667 | BTCUSDT | 5m |
| Entry Model 2 | 15m | 145 | 133 | 12 | 101 | 44 | 2.412851 | 1.609962 | 2.180108 | 1.379822 | 0.81203 | 0.609023 | 0.458647 | 0.668966 | 0.466165 | 0.308271 | 4.144828 | SOLUSDT | 15m |
| Entry Model 2 | 1h | 108 | 90 | 18 | 61 | 47 | 2.638808 | 1.650663 | 1.6068 | 0.821794 | 0.833333 | 0.7 | 0.388889 | 0.555556 | 0.6 | 0.288889 | 3.601852 | SOLUSDT | 1h |
| Entry Model 2 | 30m | 128 | 115 | 13 | 76 | 52 | 3.361447 | 1.604545 | 1.797998 | 1.164559 | 0.86087 | 0.669565 | 0.426087 | 0.617188 | 0.469565 | 0.278261 | 4.039062 | SOLUSDT | 30m |
| Entry Model 2 | 4h | 137 | 128 | 9 | 52 | 85 | 3.327584 | 1.056604 | 2.431302 | 0.920905 | 0.734375 | 0.507812 | 0.304688 | 0.489051 | 0.40625 | 0.21875 | 3.262774 | SOLUSDT | 4h |
| Entry Model 2 | 5m | 167 | 138 | 29 | 120 | 47 | 1.766552 | 1.304147 | 2.192238 | 0.951996 | 0.789855 | 0.57971 | 0.318841 | 0.57485 | 0.485507 | 0.246377 | 4.197605 | SOLUSDT | 5m |
| Entry Model 3 | 15m | 17 | 14 | 3 | 9 | 8 | 4.980223 | 3.471457 | 10.305777 | 5.161863 | 0.928571 | 0.785714 | 0.642857 | 0.941176 | 0.357143 | 0.285714 | 4.352941 | SOLUSDT | 15m |
| Entry Model 3 | 1h | 23 | 21 | 2 | 14 | 9 | 14.221348 | 8.52381 | 8.959549 | 5.547368 | 0.857143 | 0.809524 | 0.761905 | 0.826087 | 0.619048 | 0.47619 | 3.913043 | ETHUSDT | 1h |

_Showing 12 of 15 rows._

## 5. Score bucket analysis
| model | score_bucket | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | high | 400 | 375 | 25 | 281 | 119 | 2.140067 | 1.352852 | 1.779244 | 0.984428 | 0.773333 | 0.594667 | 0.36 | 0.5275 | 0.488 | 0.28 | 4.2325 | ETHUSDT | 30m |
| Entry Model 1 | low | 46 | 38 | 8 | 12 | 34 | 1.82612 | 1.176569 | 1.104424 | 0.908582 | 0.657895 | 0.526316 | 0.263158 | 0.565217 | 0.447368 | 0.236842 | 2.0 | SOLUSDT | 30m |
| Entry Model 1 | medium | 221 | 205 | 16 | 89 | 132 | 2.23332 | 1.095756 | 2.419876 | 0.782037 | 0.731707 | 0.521951 | 0.292683 | 0.488688 | 0.458537 | 0.253659 | 3.0 | SOLUSDT | 4h |
| Entry Model 2 | high | 502 | 446 | 56 | 358 | 144 | 2.420458 | 1.403879 | 2.074502 | 1.150733 | 0.804933 | 0.607623 | 0.369955 | 0.593625 | 0.473094 | 0.264574 | 4.252988 | SOLUSDT | 30m |
| Entry Model 2 | low | 25 | 20 | 5 | 8 | 17 | 2.441372 | 0.976378 | 1.311144 | 1.024242 | 0.8 | 0.4 | 0.4 | 0.64 | 0.3 | 0.1 | 1.84 | BTCUSDT | 30m |
| Entry Model 2 | medium | 158 | 138 | 20 | 44 | 114 | 3.524141 | 1.450035 | 2.200152 | 0.939642 | 0.797101 | 0.630435 | 0.398551 | 0.537975 | 0.521739 | 0.297101 | 3.0 | SOLUSDT | 4h |
| Entry Model 3 | high | 64 | 58 | 6 | 38 | 26 | 8.412294 | 5.550841 | 10.445531 | 7.152893 | 0.862069 | 0.810345 | 0.689655 | 0.90625 | 0.465517 | 0.362069 | 4.203125 | ETHUSDT | 4h |
| Entry Model 3 | low | 2 | 2 | 0 | 1 | 1 | 12.196497 | 12.196497 | 24.469454 | 24.469454 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 2.0 | ETHUSDT | 4h |
| Entry Model 3 | medium | 22 | 20 | 2 | 8 | 14 | 11.404024 | 5.266714 | 10.232425 | 7.603614 | 0.75 | 0.7 | 0.65 | 0.818182 | 0.6 | 0.55 | 3.0 | BTCUSDT | 1h |

## 6. HTF Context Analysis
### Events by HTF bias
| model | htf_bias | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | bearish | 193 | 180 | 13 | 0 | 193 | 2.017723 | 1.16028 | 1.709163 | 1.127544 | 0.727778 | 0.561111 | 0.316667 | 0.559585 | 0.461111 | 0.244444 | 3.523316 | SOLUSDT | 4h |
| Entry Model 1 | bullish | 287 | 271 | 16 | 287 | 0 | 2.166041 | 1.352852 | 1.55829 | 0.769657 | 0.760148 | 0.586716 | 0.361624 | 0.439024 | 0.520295 | 0.321033 | 4.101045 | ETHUSDT | 30m |
| Entry Model 1 | neutral | 187 | 167 | 20 | 95 | 92 | 2.272821 | 1.12618 | 2.846187 | 1.068079 | 0.766467 | 0.538922 | 0.299401 | 0.593583 | 0.419162 | 0.209581 | 3.160428 | ETHUSDT | 4h |
| Entry Model 2 | bearish | 195 | 181 | 14 | 0 | 195 | 2.776542 | 1.210187 | 2.469034 | 1.330709 | 0.723757 | 0.519337 | 0.325967 | 0.646154 | 0.364641 | 0.176796 | 3.625641 | SOLUSDT | 4h |
| Entry Model 2 | bullish | 310 | 276 | 34 | 310 | 0 | 2.605486 | 1.541731 | 1.930228 | 0.995392 | 0.815217 | 0.623188 | 0.391304 | 0.554839 | 0.51087 | 0.300725 | 4.322581 | SOLUSDT | 30m |
| Entry Model 2 | neutral | 180 | 147 | 33 | 100 | 80 | 2.673572 | 1.634173 | 1.873697 | 0.92 | 0.877551 | 0.680272 | 0.414966 | 0.561111 | 0.557823 | 0.312925 | 3.377778 | BTCUSDT | 30m |
| Entry Model 3 | bearish | 41 | 37 | 4 | 0 | 41 | 6.374221 | 4.0 | 8.54876 | 5.465364 | 0.837838 | 0.810811 | 0.675676 | 0.926829 | 0.513514 | 0.378378 | 3.609756 | SOLUSDT | 1h |
| Entry Model 3 | bullish | 47 | 43 | 4 | 47 | 0 | 11.733497 | 5.75 | 12.630792 | 8.618352 | 0.837209 | 0.767442 | 0.697674 | 0.851064 | 0.511628 | 0.465116 | 4.06383 | ETHUSDT | 1h |

### Performance by HTF location
| model | htf_location | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | discount | 272 | 252 | 20 | 169 | 103 | 1.970861 | 1.244976 | 1.879451 | 1.049876 | 0.769841 | 0.56746 | 0.325397 | 0.558824 | 0.47619 | 0.25 | 3.709559 | ETHUSDT | 4h |
| Entry Model 1 | equilibrium | 106 | 104 | 2 | 68 | 38 | 1.919013 | 1.14697 | 1.77878 | 0.870144 | 0.75 | 0.557692 | 0.355769 | 0.481132 | 0.451923 | 0.288462 | 3.764151 | BTCUSDT | 30m |
| Entry Model 1 | premium | 289 | 262 | 27 | 145 | 144 | 2.417992 | 1.231899 | 2.086429 | 0.829006 | 0.736641 | 0.568702 | 0.328244 | 0.491349 | 0.484733 | 0.278626 | 3.598616 | ETHUSDT | 4h |
| Entry Model 2 | discount | 265 | 236 | 29 | 170 | 95 | 2.39885 | 1.348357 | 2.239119 | 1.134017 | 0.79661 | 0.580508 | 0.372881 | 0.603774 | 0.440678 | 0.233051 | 3.837736 | SOLUSDT | 30m |
| Entry Model 2 | equilibrium | 110 | 98 | 12 | 80 | 30 | 2.061696 | 1.295995 | 1.570124 | 0.775199 | 0.795918 | 0.612245 | 0.316327 | 0.481818 | 0.540816 | 0.27551 | 4.018182 | BTCUSDT | 30m |
| Entry Model 2 | premium | 310 | 270 | 40 | 160 | 150 | 3.135217 | 1.613253 | 2.121361 | 1.060282 | 0.811111 | 0.625926 | 0.403704 | 0.6 | 0.488889 | 0.292593 | 3.858065 | SOLUSDT | 4h |
| Entry Model 3 | discount | 15 | 14 | 1 | 7 | 8 | 11.037182 | 1.556706 | 11.930088 | 7.212831 | 0.785714 | 0.714286 | 0.428571 | 0.866667 | 0.428571 | 0.285714 | 3.733333 | ETHUSDT | 4h |
| Entry Model 3 | equilibrium | 12 | 11 | 1 | 7 | 5 | 4.52006 | 3.357616 | 10.364767 | 9.784106 | 0.818182 | 0.818182 | 0.636364 | 0.916667 | 0.454545 | 0.363636 | 4.166667 | BTCUSDT | 30m |
| Entry Model 3 | premium | 61 | 55 | 6 | 33 | 28 | 9.748097 | 6.083791 | 10.516264 | 5.5 | 0.854545 | 0.8 | 0.763636 | 0.885246 | 0.545455 | 0.472727 | 3.819672 | BTCUSDT | 1h |

### Performance by HTF zone type
| model | htf_zone_type | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | Breaker | 136 | 125 | 11 | 97 | 39 | 1.951757 | 1.260493 | 1.627795 | 0.846154 | 0.784 | 0.552 | 0.328 | 0.5 | 0.44 | 0.24 | 3.860294 | BTCUSDT | 15m |
| Entry Model 1 | FVG | 180 | 162 | 18 | 129 | 51 | 2.185441 | 1.509805 | 1.669925 | 1.095292 | 0.777778 | 0.635802 | 0.395062 | 0.583333 | 0.493827 | 0.283951 | 3.683333 | SOLUSDT | 5m |
| Entry Model 1 | IFVG | 177 | 164 | 13 | 64 | 113 | 2.189969 | 1.256217 | 2.467498 | 0.775931 | 0.737805 | 0.609756 | 0.341463 | 0.480226 | 0.560976 | 0.310976 | 3.418079 | ETHUSDT | 4h |
| Entry Model 1 | Liquidity | 3 | 3 | 0 | 0 | 3 | 1.534715 | 1.074074 | 0.963375 | 0.925926 | 0.666667 | 0.666667 | 0.333333 | 0.333333 | 0.666667 | 0.333333 | 3.0 | BTCUSDT | 30m |
| Entry Model 1 | OB | 19 | 18 | 1 | 15 | 4 | 1.328302 | 0.740375 | 3.100227 | 1.530646 | 0.722222 | 0.277778 | 0.222222 | 0.684211 | 0.166667 | 0.111111 | 3.526316 | ETHUSDT | 30m |
| Entry Model 1 | PD | 152 | 146 | 6 | 77 | 75 | 2.356635 | 0.988698 | 1.834884 | 0.888673 | 0.719178 | 0.486301 | 0.267123 | 0.480263 | 0.424658 | 0.246575 | 3.809211 | ETHUSDT | 30m |
| Entry Model 2 | Breaker | 137 | 116 | 21 | 98 | 39 | 2.312749 | 1.724007 | 1.968258 | 1.216106 | 0.853448 | 0.62931 | 0.448276 | 0.635036 | 0.431034 | 0.275862 | 4.051095 | BTCUSDT | 1h |
| Entry Model 2 | FVG | 182 | 150 | 32 | 127 | 55 | 3.488733 | 1.625282 | 2.070823 | 1.176848 | 0.833333 | 0.686667 | 0.4 | 0.664835 | 0.506667 | 0.273333 | 3.879121 | SOLUSDT | 4h |
| Entry Model 2 | IFVG | 173 | 155 | 18 | 80 | 93 | 2.417096 | 1.320755 | 2.337707 | 1.100645 | 0.748387 | 0.587097 | 0.322581 | 0.589595 | 0.490323 | 0.245161 | 3.820809 | SOLUSDT | 15m |
| Entry Model 2 | Liquidity | 10 | 8 | 2 | 1 | 9 | 3.284171 | 3.854839 | 0.803601 | 0.84375 | 1.0 | 0.875 | 0.75 | 0.4 | 0.625 | 0.5 | 3.2 | BTCUSDT | 30m |
| Entry Model 2 | OB | 18 | 17 | 1 | 13 | 5 | 3.318161 | 1.634173 | 3.493012 | 1.8 | 0.882353 | 0.705882 | 0.470588 | 0.722222 | 0.529412 | 0.176471 | 3.833333 | SOLUSDT | 30m |
| Entry Model 2 | PD | 165 | 158 | 7 | 91 | 74 | 2.314952 | 1.028842 | 1.822631 | 0.857343 | 0.772152 | 0.506329 | 0.329114 | 0.436364 | 0.462025 | 0.272152 | 3.830303 | ETHUSDT | 30m |

_Showing 12 of 17 rows._

### Performance by HTF alignment
| model | htf_alignment | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | aligned | 480 | 451 | 29 | 287 | 193 | 2.106845 | 1.263467 | 1.618505 | 0.843931 | 0.747228 | 0.576497 | 0.343681 | 0.4875 | 0.496674 | 0.290466 | 3.86875 | ETHUSDT | 30m |
| Entry Model 1 | neutral | 187 | 167 | 20 | 95 | 92 | 2.272821 | 1.12618 | 2.846187 | 1.068079 | 0.766467 | 0.538922 | 0.299401 | 0.593583 | 0.419162 | 0.209581 | 3.160428 | ETHUSDT | 4h |
| Entry Model 2 | aligned | 505 | 457 | 48 | 310 | 195 | 2.673235 | 1.336889 | 2.143629 | 1.14382 | 0.778993 | 0.582057 | 0.365427 | 0.590099 | 0.452954 | 0.251641 | 4.053465 | SOLUSDT | 4h |
| Entry Model 2 | neutral | 180 | 147 | 33 | 100 | 80 | 2.673572 | 1.634173 | 1.873697 | 0.92 | 0.877551 | 0.680272 | 0.414966 | 0.561111 | 0.557823 | 0.312925 | 3.377778 | BTCUSDT | 30m |
| Entry Model 3 | aligned | 88 | 80 | 8 | 47 | 41 | 9.254832 | 5.619318 | 10.742852 | 7.152893 | 0.8375 | 0.7875 | 0.6875 | 0.886364 | 0.5125 | 0.425 | 3.852273 | ETHUSDT | 1h |

### Performance by displacement
| model | displacement | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | has_displacement | 422 | 403 | 19 | 249 | 173 | 2.272486 | 1.311787 | 2.11226 | 0.843931 | 0.789082 | 0.600496 | 0.337469 | 0.473934 | 0.51861 | 0.280397 | 3.85782 | ETHUSDT | 30m |
| Entry Model 1 | weak_or_none | 245 | 215 | 30 | 133 | 112 | 1.925284 | 1.006203 | 1.646597 | 1.079624 | 0.683721 | 0.502326 | 0.32093 | 0.591837 | 0.395349 | 0.246512 | 3.346939 | SOLUSDT | 4h |
| Entry Model 2 | has_displacement | 685 | 604 | 81 | 410 | 275 | 2.673317 | 1.403879 | 2.077933 | 1.036769 | 0.80298 | 0.60596 | 0.377483 | 0.582482 | 0.478477 | 0.266556 | 3.875912 | SOLUSDT | 30m |
| Entry Model 3 | has_displacement | 67 | 60 | 7 | 39 | 28 | 9.040824 | 5.225527 | 11.790852 | 9.692821 | 0.833333 | 0.766667 | 0.666667 | 0.925373 | 0.466667 | 0.383333 | 4.0 | ETHUSDT | 1h |
| Entry Model 3 | weak_or_none | 21 | 20 | 1 | 8 | 13 | 9.896855 | 7.710541 | 7.598854 | 3.421907 | 0.85 | 0.85 | 0.75 | 0.761905 | 0.65 | 0.55 | 3.380952 | BTCUSDT | 1h |

### Performance by FVG status
| model | fvg_status | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | filled | 71 | 64 | 7 | 39 | 32 | 1.447318 | 0.914734 | 2.053083 | 1.145154 | 0.640625 | 0.484375 | 0.3125 | 0.633803 | 0.375 | 0.234375 | 3.591549 | SOLUSDT | 30m |
| Entry Model 1 | open | 426 | 387 | 39 | 240 | 186 | 2.347289 | 1.375372 | 2.092873 | 0.837599 | 0.790698 | 0.609819 | 0.366925 | 0.5 | 0.529716 | 0.302326 | 3.711268 | ETHUSDT | 4h |
| Entry Model 1 | partially_filled | 170 | 167 | 3 | 103 | 67 | 1.968376 | 0.993726 | 1.58036 | 1.04104 | 0.706587 | 0.497006 | 0.257485 | 0.511765 | 0.389222 | 0.203593 | 3.6 | ETHUSDT | 30m |
| Entry Model 2 | unknown | 685 | 604 | 81 | 410 | 275 | 2.673317 | 1.403879 | 2.077933 | 1.036769 | 0.80298 | 0.60596 | 0.377483 | 0.582482 | 0.478477 | 0.266556 | 3.875912 | SOLUSDT | 30m |
| Entry Model 3 | filled | 57 | 54 | 3 | 31 | 26 | 6.701567 | 5.198237 | 9.63388 | 5.436297 | 0.814815 | 0.740741 | 0.685185 | 0.894737 | 0.444444 | 0.37037 | 4.017544 | ETHUSDT | 1h |
| Entry Model 3 | partially_filled | 31 | 26 | 5 | 16 | 15 | 14.557767 | 6.90165 | 13.046103 | 10.61105 | 0.884615 | 0.884615 | 0.692308 | 0.870968 | 0.653846 | 0.538462 | 3.548387 | ETHUSDT | 1h |

### Model 3 fill variants
| model | fill_mode | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | none | 667 | 618 | 49 | 382 | 285 | 2.151696 | 1.221309 | 1.950258 | 0.921141 | 0.752427 | 0.566343 | 0.331715 | 0.517241 | 0.475728 | 0.268608 | 3.670165 | ETHUSDT | 30m |
| Entry Model 2 | none | 685 | 604 | 81 | 410 | 275 | 2.673317 | 1.403879 | 2.077933 | 1.036769 | 0.80298 | 0.60596 | 0.377483 | 0.582482 | 0.478477 | 0.266556 | 3.875912 | SOLUSDT | 30m |
| Entry Model 3 | 50 | 88 | 80 | 8 | 47 | 41 | 9.254832 | 5.619318 | 10.742852 | 7.152893 | 0.8375 | 0.7875 | 0.6875 | 0.886364 | 0.5125 | 0.425 | 3.852273 | ETHUSDT | 1h |

## 7. Warnings / skipped events
- 1d5493c93153ca95: invalid risk (risk is not positive; R metrics are skipped)
- 345d3bb416f1db97: invalid risk (risk is not positive; R metrics are skipped)
- 275917050cd6541b: invalid risk (risk is not positive; R metrics are skipped)
- b4550c296a654c1e: invalid risk (risk is not positive; R metrics are skipped)
- 10d246d096055fab: invalid risk (risk is not positive; R metrics are skipped)
- 917dc1b537485181: invalid risk (risk is not positive; R metrics are skipped)
- 8ba1aef6dfadd917: invalid risk (risk is not positive; R metrics are skipped)
- 7e462c4a66f2a0bc: invalid risk (risk is not positive; R metrics are skipped)
- 5c91616e4417d86f: invalid risk (risk is not positive; R metrics are skipped)
- 4e0a6003103dc002: invalid risk (risk is not positive; R metrics are skipped)
- 45171b0ebd74f7e9: invalid risk (risk is not positive; R metrics are skipped)
- 6e8535593bc1b440: invalid risk (risk is not positive; R metrics are skipped)
- 51bb6f5b20acff89: invalid risk (risk is not positive; R metrics are skipped)
- 983706697957fbef: invalid risk (risk is not positive; R metrics are skipped)
- 71ad932fcc1d7ca1: invalid risk (risk is not positive; R metrics are skipped)
- 20550c6a5a3b4bbf: invalid risk (risk is not positive; R metrics are skipped)
- 27fec2d52124dbe3: invalid risk (risk is not positive; R metrics are skipped)
- 93b2363181d2ff5e: invalid risk (risk is not positive; R metrics are skipped)
- 479d219d563d55b2: invalid risk (risk is not positive; R metrics are skipped)
- ce2533422034cb90: invalid risk (risk is not positive; R metrics are skipped)
- fdf1323995a6b685: invalid risk (risk is not positive; R metrics are skipped)
- 518afc53a0dcda4f: invalid risk (risk is not positive; R metrics are skipped)
- 8e975dd5f45ac963: invalid risk (risk is not positive; R metrics are skipped)
- db2e20c81b720f6a: invalid risk (risk is not positive; R metrics are skipped)
- c0f43ca80b72d0e8: invalid risk (risk is not positive; R metrics are skipped)
- 5798f3e8836eb929: invalid risk (risk is not positive; R metrics are skipped)
- ed38165a11b270be: invalid risk (risk is not positive; R metrics are skipped)
- 46fc2ec914f14f8c: invalid risk (risk is not positive; R metrics are skipped)
- 93c25c15ed1b135d: invalid risk (risk is not positive; R metrics are skipped)
- ec5fe7ae1464c578: invalid risk (risk is not positive; R metrics are skipped)
- 440c68a4514919a6: invalid risk (risk is not positive; R metrics are skipped)
- ccdaed80a9545094: invalid risk (risk is not positive; R metrics are skipped)
- d64de26f9700a25c: invalid risk (risk is not positive; R metrics are skipped)
- 340e1e9d1b0bb21c: invalid risk (risk is not positive; R metrics are skipped)
- 06860f7b51ff5f0a: invalid risk (risk is not positive; R metrics are skipped)
- a8d7c0db75355fbe: invalid risk (risk is not positive; R metrics are skipped)
- ddcb009eb0d2c5f4: invalid risk (risk is not positive; R metrics are skipped)
- 48a5b7beb51d4756: invalid risk (risk is not positive; R metrics are skipped)
- 4759871c5dac9c6d: invalid risk (risk is not positive; R metrics are skipped)
- 5f84c176da09ee64: invalid risk (risk is not positive; R metrics are skipped)
- 1a9e30346fe0bc84: invalid risk (risk is not positive; R metrics are skipped)
- 1a79173a0cbcef81: invalid risk (risk is not positive; R metrics are skipped)
- 2a9fddb5d95bec65: invalid risk (risk is not positive; R metrics are skipped)
- 9b4bc57983c5938e: invalid risk (risk is not positive; R metrics are skipped)
- d7204617f077d8a1: invalid risk (risk is not positive; R metrics are skipped)
- 0c69721908f99810: invalid risk (risk is not positive; R metrics are skipped)
- 5eb60bef2371be35: invalid risk (risk is not positive; R metrics are skipped)
- 9cfa72199747424b: invalid risk (risk is not positive; R metrics are skipped)
- 4ab47a35a5e7712f: invalid risk (risk is not positive; R metrics are skipped)
- 2f21a7ed990b9fd2: invalid risk (risk is not positive; R metrics are skipped)

## 8. Interpretation notes
- Replay is bar-by-bar: strategies receive only candles visible at the current bar.
- Forward candles are used only after event detection for outcome measurement.
- `bars_to_*` values are 1-based future bar offsets from the signal bar.
- `*_before_invalidation` uses OHLC bar ordering only; same-bar threshold/invalidation ordering is not modeled.
- HTF-filtered event studies should usually have fewer signals than legacy/off mode.
- If strict signal count does not decrease, HTF gating is too weak.
- If score buckets remain mostly high, scoring is not calibrated enough.
