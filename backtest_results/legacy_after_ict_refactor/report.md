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
- htf_mode: off
- require_displacement: False
- model3_fill_threshold: 0.5
- execution_pairs: {'1m': '15m', '3m': '30m', '5m': '1h', '15m': '4h', '30m': '4h', '1h': '1d'}
- model_3_htf_map: {'1m': '15m', '3m': '30m', '5m': '1h', '15m': '4h', '30m': '4h', '1h': '1d', '4h': '1d'}
- model_3_ltf_map: {'5m': '1m', '15m': '3m', '30m': '5m', '1h': '15m', '4h': '1h'}
- generated_at: 2026-04-25T23:12:42.260953+00:00

This is an event-study backtest. It does not model fees, slippage, partial exits, breakeven, or full execution management.

## 1. Overall summary
- events: 3236
- warnings: 0
- skipped_outcome_events: 343

## 2. Summary by model
| model | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | 1955 | 1749 | 206 | 937 | 1018 | 2.40496 | 1.281679 | 2.185173 | 1.075008 | 0.792453 | 0.576329 | 0.352773 | 0.573402 | 0.482561 | 0.272727 | 3.31867 | SOLUSDT | 4h |
| Entry Model 2 | 1260 | 1127 | 133 | 633 | 627 | 2.467595 | 1.310781 | 2.591715 | 1.133619 | 0.796806 | 0.595386 | 0.345164 | 0.577778 | 0.488021 | 0.254658 | 3.675397 | SOLUSDT | 4h |
| Entry Model 3 | 21 | 17 | 4 | 14 | 7 | 15.052291 | 10.294118 | 8.145257 | 4.0 | 0.941176 | 0.882353 | 0.823529 | 1.0 | 0.352941 | 0.294118 | 3.380952 | BTCUSDT | 1h |

## 3. Summary by direction
| model | direction | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | long | 937 | 836 | 101 | 937 | 0 | 2.572721 | 1.353635 | 1.982913 | 1.028142 | 0.796651 | 0.594498 | 0.370813 | 0.558164 | 0.497608 | 0.287081 | 3.371398 | ETHUSDT | 4h |
| Entry Model 1 | short | 1018 | 913 | 105 | 0 | 1018 | 2.251348 | 1.171078 | 2.370375 | 1.144307 | 0.788609 | 0.559693 | 0.336254 | 0.587426 | 0.468784 | 0.259584 | 3.270138 | SOLUSDT | 4h |
| Entry Model 2 | long | 633 | 567 | 66 | 633 | 0 | 2.408573 | 1.39604 | 2.36794 | 0.870386 | 0.811287 | 0.619048 | 0.365079 | 0.516588 | 0.511464 | 0.276896 | 3.704581 | SOLUSDT | 30m |
| Entry Model 2 | short | 627 | 560 | 67 | 0 | 627 | 2.527356 | 1.232874 | 2.818287 | 1.460171 | 0.782143 | 0.571429 | 0.325 | 0.639553 | 0.464286 | 0.232143 | 3.645933 | SOLUSDT | 4h |
| Entry Model 3 | long | 14 | 11 | 3 | 14 | 0 | 15.935829 | 6.4453 | 9.834246 | 4.206074 | 0.909091 | 0.818182 | 0.818182 | 1.0 | 0.454545 | 0.454545 | 3.357143 | ETHUSDT | 1h |
| Entry Model 3 | short | 7 | 6 | 1 | 0 | 7 | 13.432472 | 13.43956 | 5.048776 | 3.252941 | 1.0 | 1.0 | 0.833333 | 1.0 | 0.166667 | 0.0 | 3.428571 | SOLUSDT | 1h |

## 4. Summary by timeframe
| model | timeframe | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | 15m | 399 | 354 | 45 | 179 | 220 | 2.201215 | 1.32405 | 1.966986 | 1.010625 | 0.850282 | 0.615819 | 0.378531 | 0.553885 | 0.539548 | 0.316384 | 3.521303 | BTCUSDT | 15m |
| Entry Model 1 | 1h | 349 | 308 | 41 | 167 | 182 | 2.311107 | 1.111074 | 2.606359 | 1.187573 | 0.733766 | 0.532468 | 0.305195 | 0.584527 | 0.448052 | 0.24026 | 3.123209 | ETHUSDT | 1h |
| Entry Model 1 | 30m | 402 | 354 | 48 | 186 | 216 | 2.403485 | 1.147475 | 2.614945 | 1.266224 | 0.79661 | 0.545198 | 0.333333 | 0.644279 | 0.451977 | 0.245763 | 3.345771 | SOLUSDT | 30m |
| Entry Model 1 | 4h | 376 | 340 | 36 | 201 | 175 | 3.155421 | 1.429846 | 2.0527 | 0.973483 | 0.782353 | 0.629412 | 0.408824 | 0.539894 | 0.502941 | 0.294118 | 2.861702 | SOLUSDT | 4h |
| Entry Model 1 | 5m | 429 | 393 | 36 | 204 | 225 | 2.014114 | 1.235294 | 1.779103 | 1.00605 | 0.791349 | 0.557252 | 0.335878 | 0.545455 | 0.468193 | 0.264631 | 3.664336 | ETHUSDT | 5m |
| Entry Model 2 | 15m | 261 | 235 | 26 | 132 | 129 | 2.474603 | 1.320755 | 2.217999 | 1.445986 | 0.821277 | 0.591489 | 0.374468 | 0.651341 | 0.46383 | 0.26383 | 3.89272 | BTCUSDT | 15m |
| Entry Model 2 | 1h | 212 | 186 | 26 | 107 | 105 | 2.537277 | 1.53742 | 1.871778 | 0.896574 | 0.83871 | 0.672043 | 0.370968 | 0.518868 | 0.596774 | 0.301075 | 3.466981 | BTCUSDT | 1h |
| Entry Model 2 | 30m | 242 | 221 | 21 | 114 | 128 | 2.786818 | 1.343914 | 2.31118 | 1.2 | 0.855204 | 0.628959 | 0.357466 | 0.61157 | 0.479638 | 0.239819 | 3.818182 | SOLUSDT | 30m |
| Entry Model 2 | 4h | 239 | 213 | 26 | 115 | 124 | 2.963939 | 1.257827 | 4.46507 | 0.962205 | 0.741784 | 0.57277 | 0.338028 | 0.539749 | 0.455399 | 0.234742 | 3.087866 | SOLUSDT | 4h |
| Entry Model 2 | 5m | 306 | 272 | 34 | 165 | 141 | 1.765841 | 1.118056 | 2.167835 | 1.0 | 0.742647 | 0.536765 | 0.297794 | 0.558824 | 0.466912 | 0.242647 | 3.980392 | SOLUSDT | 5m |
| Entry Model 3 | 15m | 6 | 4 | 2 | 4 | 2 | 9.217158 | 8.334315 | 11.414534 | 3.529068 | 0.75 | 0.75 | 0.75 | 1.0 | 0.25 | 0.25 | 3.5 | SOLUSDT | 15m |
| Entry Model 3 | 1h | 8 | 7 | 1 | 6 | 2 | 24.326209 | 22.0 | 6.473078 | 6.745776 | 1.0 | 0.857143 | 0.857143 | 1.0 | 0.285714 | 0.142857 | 3.25 | BTCUSDT | 1h |

_Showing 12 of 15 rows._

## 5. Score bucket analysis
| model | score_bucket | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | high | 786 | 733 | 53 | 414 | 372 | 2.403864 | 1.352852 | 2.22878 | 1.144307 | 0.803547 | 0.592087 | 0.360164 | 0.581425 | 0.496589 | 0.28513 | 4.0 | ETHUSDT | 4h |
| Entry Model 1 | low | 161 | 132 | 29 | 66 | 95 | 1.97063 | 1.129277 | 1.774586 | 0.934797 | 0.780303 | 0.55303 | 0.325758 | 0.565217 | 0.469697 | 0.234848 | 1.987578 | SOLUSDT | 5m |
| Entry Model 1 | medium | 1008 | 884 | 124 | 457 | 551 | 2.470723 | 1.274534 | 2.210324 | 1.050334 | 0.785068 | 0.566742 | 0.350679 | 0.568452 | 0.472851 | 0.2681 | 3.0 | SOLUSDT | 4h |
| Entry Model 2 | high | 881 | 805 | 76 | 460 | 421 | 2.419956 | 1.351852 | 2.500139 | 1.316131 | 0.798758 | 0.598758 | 0.361491 | 0.609535 | 0.484472 | 0.269565 | 4.0 | SOLUSDT | 1h |
| Entry Model 2 | low | 30 | 24 | 6 | 14 | 16 | 2.260065 | 1.97247 | 1.762844 | 1.252247 | 0.875 | 0.708333 | 0.5 | 0.7 | 0.625 | 0.291667 | 2.0 | BTCUSDT | 4h |
| Entry Model 2 | medium | 349 | 298 | 51 | 159 | 190 | 2.613001 | 1.212704 | 2.905846 | 0.809449 | 0.785235 | 0.577181 | 0.288591 | 0.487106 | 0.486577 | 0.211409 | 3.0 | SOLUSDT | 4h |
| Entry Model 3 | high | 8 | 5 | 3 | 5 | 3 | 6.466918 | 2.175022 | 11.508947 | 3.552331 | 0.8 | 0.8 | 0.6 | 1.0 | 0.4 | 0.2 | 4.0 | SOLUSDT | 1h |
| Entry Model 3 | medium | 13 | 12 | 1 | 9 | 4 | 18.62953 | 12.115269 | 6.743719 | 4.103037 | 1.0 | 0.916667 | 0.916667 | 1.0 | 0.333333 | 0.333333 | 3.0 | ETHUSDT | 1h |

## 6. HTF Context Analysis
### Events by HTF bias
| model | htf_bias | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | bearish | 497 | 442 | 55 | 238 | 259 | 2.485565 | 1.311787 | 1.900831 | 1.046075 | 0.778281 | 0.581448 | 0.357466 | 0.559356 | 0.484163 | 0.269231 | 3.215292 | SOLUSDT | 4h |
| Entry Model 1 | bullish | 913 | 820 | 93 | 425 | 488 | 2.405728 | 1.32405 | 2.212628 | 1.068079 | 0.810976 | 0.589024 | 0.37561 | 0.571742 | 0.497561 | 0.3 | 3.389923 | SOLUSDT | 4h |
| Entry Model 1 | neutral | 545 | 487 | 58 | 274 | 271 | 2.330509 | 1.171078 | 2.397012 | 1.142159 | 0.774127 | 0.550308 | 0.310062 | 0.588991 | 0.455852 | 0.229979 | 3.293578 | ETHUSDT | 1h |
| Entry Model 2 | bearish | 367 | 339 | 28 | 196 | 171 | 2.418862 | 1.225564 | 2.057572 | 0.96875 | 0.761062 | 0.554572 | 0.321534 | 0.531335 | 0.436578 | 0.212389 | 3.485014 | SOLUSDT | 4h |
| Entry Model 2 | bullish | 581 | 512 | 69 | 292 | 289 | 2.500335 | 1.359223 | 2.466713 | 1.259493 | 0.820312 | 0.613281 | 0.347656 | 0.600688 | 0.513672 | 0.273438 | 3.767642 | BTCUSDT | 1h |
| Entry Model 2 | neutral | 312 | 276 | 36 | 145 | 167 | 2.466719 | 1.309786 | 3.479669 | 1.148148 | 0.797101 | 0.612319 | 0.369565 | 0.589744 | 0.503623 | 0.271739 | 3.727564 | SOLUSDT | 30m |
| Entry Model 3 | bearish | 7 | 6 | 1 | 0 | 7 | 13.432472 | 13.43956 | 5.048776 | 3.252941 | 1.0 | 1.0 | 0.833333 | 1.0 | 0.166667 | 0.0 | 3.428571 | SOLUSDT | 1h |
| Entry Model 3 | bullish | 14 | 11 | 3 | 14 | 0 | 15.935829 | 6.4453 | 9.834246 | 4.206074 | 0.909091 | 0.818182 | 0.818182 | 1.0 | 0.454545 | 0.454545 | 3.357143 | ETHUSDT | 1h |

### Performance by HTF location
| model | htf_location | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | discount | 824 | 741 | 83 | 360 | 464 | 2.322388 | 1.270922 | 2.222443 | 1.186441 | 0.804318 | 0.573549 | 0.337382 | 0.59466 | 0.481781 | 0.260459 | 3.282767 | SOLUSDT | 4h |
| Entry Model 1 | equilibrium | 254 | 236 | 18 | 116 | 138 | 1.982348 | 1.34123 | 1.884036 | 1.109714 | 0.817797 | 0.601695 | 0.364407 | 0.57874 | 0.487288 | 0.254237 | 3.393701 | SOLUSDT | 4h |
| Entry Model 1 | premium | 877 | 772 | 105 | 461 | 416 | 2.613409 | 1.278538 | 2.241457 | 0.973594 | 0.773316 | 0.571244 | 0.36399 | 0.551881 | 0.481865 | 0.290155 | 3.330673 | ETHUSDT | 4h |
| Entry Model 2 | discount | 513 | 468 | 45 | 230 | 283 | 2.201657 | 1.264507 | 2.692463 | 1.336879 | 0.788462 | 0.583333 | 0.324786 | 0.614035 | 0.463675 | 0.222222 | 3.649123 | SOLUSDT | 30m |
| Entry Model 2 | equilibrium | 163 | 144 | 19 | 85 | 78 | 1.891505 | 1.218402 | 1.89251 | 0.969312 | 0.763889 | 0.611111 | 0.3125 | 0.546012 | 0.506944 | 0.229167 | 3.680982 | BTCUSDT | 30m |
| Entry Model 2 | premium | 584 | 515 | 69 | 318 | 266 | 2.870345 | 1.39604 | 2.695667 | 0.984589 | 0.813592 | 0.601942 | 0.372816 | 0.554795 | 0.504854 | 0.291262 | 3.696918 | SOLUSDT | 4h |
| Entry Model 3 | discount | 2 | 1 | 1 | 2 | 0 | 12.65911 | 12.65911 | 25.038623 | 25.038623 | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 3.5 | BTCUSDT | 4h |
| Entry Model 3 | equilibrium | 2 | 2 | 0 | 1 | 1 | 4.079784 | 4.079784 | 2.519279 | 2.519279 | 1.0 | 1.0 | 0.5 | 1.0 | 0.5 | 0.5 | 4.0 | BTCUSDT | 30m |
| Entry Model 3 | premium | 17 | 14 | 3 | 11 | 6 | 16.790733 | 10.932773 | 7.742299 | 4.103037 | 0.928571 | 0.857143 | 0.857143 | 1.0 | 0.357143 | 0.285714 | 3.294118 | ETHUSDT | 1h |

### Performance by HTF zone type
| model | htf_zone_type | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | Breaker | 483 | 439 | 44 | 218 | 265 | 2.188586 | 1.300652 | 1.828388 | 1.085765 | 0.792711 | 0.569476 | 0.334852 | 0.57971 | 0.471526 | 0.248292 | 3.389234 | SOLUSDT | 4h |
| Entry Model 1 | FVG | 559 | 499 | 60 | 267 | 292 | 2.295486 | 1.32809 | 2.117411 | 1.068966 | 0.805611 | 0.593186 | 0.360721 | 0.581395 | 0.49499 | 0.270541 | 3.296959 | SOLUSDT | 5m |
| Entry Model 1 | IFVG | 465 | 416 | 49 | 233 | 232 | 2.508339 | 1.316015 | 2.59182 | 1.043508 | 0.802885 | 0.598558 | 0.365385 | 0.56129 | 0.536058 | 0.317308 | 3.294624 | ETHUSDT | 4h |
| Entry Model 1 | Liquidity | 12 | 11 | 1 | 5 | 7 | 3.782472 | 0.808239 | 1.234907 | 1.397851 | 0.636364 | 0.454545 | 0.363636 | 0.583333 | 0.454545 | 0.363636 | 3.583333 | BTCUSDT | 30m |
| Entry Model 1 | OB | 42 | 35 | 7 | 23 | 19 | 3.378108 | 1.344096 | 3.767051 | 1.43384 | 0.742857 | 0.542857 | 0.457143 | 0.690476 | 0.428571 | 0.342857 | 3.190476 | BTCUSDT | 1h |
| Entry Model 1 | PD | 394 | 349 | 45 | 191 | 203 | 2.569421 | 1.172016 | 2.117446 | 1.043478 | 0.770774 | 0.541547 | 0.338109 | 0.555838 | 0.421203 | 0.243553 | 3.296954 | SOLUSDT | 4h |
| Entry Model 2 | Breaker | 264 | 239 | 25 | 137 | 127 | 1.956103 | 1.215247 | 3.487739 | 1.255981 | 0.803347 | 0.564854 | 0.334728 | 0.602273 | 0.443515 | 0.238494 | 3.814394 | SOLUSDT | 1h |
| Entry Model 2 | FVG | 347 | 298 | 49 | 180 | 167 | 2.858917 | 1.399969 | 1.881516 | 1.045424 | 0.832215 | 0.634228 | 0.345638 | 0.582133 | 0.513423 | 0.261745 | 3.616715 | SOLUSDT | 4h |
| Entry Model 2 | IFVG | 310 | 282 | 28 | 146 | 164 | 2.385369 | 1.328917 | 2.495248 | 1.211588 | 0.762411 | 0.606383 | 0.340426 | 0.587097 | 0.514184 | 0.258865 | 3.66129 | SOLUSDT | 30m |
| Entry Model 2 | Liquidity | 12 | 10 | 2 | 2 | 10 | 3.372318 | 3.854839 | 0.857363 | 0.84375 | 1.0 | 0.9 | 0.7 | 0.416667 | 0.6 | 0.5 | 3.916667 | BTCUSDT | 30m |
| Entry Model 2 | OB | 34 | 31 | 3 | 16 | 18 | 3.151178 | 1.762 | 6.935076 | 1.754542 | 0.870968 | 0.709677 | 0.451613 | 0.735294 | 0.580645 | 0.258065 | 3.588235 | SOLUSDT | 15m |
| Entry Model 2 | PD | 293 | 267 | 26 | 152 | 141 | 2.462286 | 1.204861 | 2.244869 | 0.966667 | 0.771536 | 0.543071 | 0.333333 | 0.52901 | 0.456929 | 0.247191 | 3.634812 | BTCUSDT | 30m |

_Showing 12 of 17 rows._

### Performance by HTF alignment
| model | htf_alignment | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | aligned | 684 | 609 | 75 | 425 | 259 | 2.167023 | 1.353388 | 1.968391 | 1.188374 | 0.793103 | 0.600985 | 0.364532 | 0.597953 | 0.490969 | 0.284072 | 3.321637 | ETHUSDT | 4h |
| Entry Model 1 | neutral | 545 | 487 | 58 | 274 | 271 | 2.330509 | 1.171078 | 2.397012 | 1.142159 | 0.774127 | 0.550308 | 0.310062 | 0.588991 | 0.455852 | 0.229979 | 3.293578 | ETHUSDT | 1h |
| Entry Model 1 | opposed | 726 | 653 | 73 | 238 | 488 | 2.682388 | 1.285714 | 2.229361 | 0.952793 | 0.805513 | 0.572741 | 0.37366 | 0.538567 | 0.49464 | 0.294028 | 3.334711 | SOLUSDT | 4h |
| Entry Model 2 | aligned | 463 | 418 | 45 | 292 | 171 | 2.735287 | 1.377855 | 2.145485 | 1.150471 | 0.794258 | 0.595694 | 0.368421 | 0.589633 | 0.466507 | 0.258373 | 3.695464 | SOLUSDT | 4h |
| Entry Model 2 | neutral | 312 | 276 | 36 | 145 | 167 | 2.466719 | 1.309786 | 3.479669 | 1.148148 | 0.797101 | 0.612319 | 0.369565 | 0.589744 | 0.503623 | 0.271739 | 3.727564 | SOLUSDT | 30m |
| Entry Model 2 | opposed | 485 | 433 | 52 | 196 | 289 | 2.209736 | 1.225564 | 2.456492 | 1.078195 | 0.799076 | 0.584296 | 0.307159 | 0.558763 | 0.498845 | 0.240185 | 3.62268 | BTCUSDT | 15m |
| Entry Model 3 | aligned | 21 | 17 | 4 | 14 | 7 | 15.052291 | 10.294118 | 8.145257 | 4.0 | 0.941176 | 0.882353 | 0.823529 | 1.0 | 0.352941 | 0.294118 | 3.380952 | BTCUSDT | 1h |

### Performance by displacement
| model | displacement | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | has_displacement | 708 | 681 | 27 | 354 | 354 | 2.296738 | 1.31283 | 2.145749 | 0.930399 | 0.801762 | 0.587372 | 0.337739 | 0.5 | 0.51395 | 0.277533 | 3.677966 | ETHUSDT | 4h |
| Entry Model 1 | weak_or_none | 1247 | 1068 | 179 | 583 | 664 | 2.473966 | 1.268623 | 2.210311 | 1.1863 | 0.786517 | 0.569288 | 0.36236 | 0.615076 | 0.462547 | 0.269663 | 3.114675 | SOLUSDT | 4h |
| Entry Model 2 | has_displacement | 1260 | 1127 | 133 | 633 | 627 | 2.467595 | 1.310781 | 2.591715 | 1.133619 | 0.796806 | 0.595386 | 0.345164 | 0.577778 | 0.488021 | 0.254658 | 3.675397 | SOLUSDT | 4h |
| Entry Model 3 | has_displacement | 8 | 5 | 3 | 5 | 3 | 6.466918 | 2.175022 | 11.508947 | 3.552331 | 0.8 | 0.8 | 0.6 | 1.0 | 0.4 | 0.2 | 4.0 | SOLUSDT | 1h |
| Entry Model 3 | weak_or_none | 13 | 12 | 1 | 9 | 4 | 18.62953 | 12.115269 | 6.743719 | 4.103037 | 1.0 | 0.916667 | 0.916667 | 1.0 | 0.333333 | 0.333333 | 3.0 | ETHUSDT | 1h |

### Performance by FVG status
| model | fvg_status | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | filled | 216 | 192 | 24 | 95 | 121 | 2.142806 | 1.083391 | 2.076315 | 1.07992 | 0.739583 | 0.526042 | 0.34375 | 0.587963 | 0.432292 | 0.28125 | 3.240741 | BTCUSDT | 4h |
| Entry Model 1 | open | 1432 | 1263 | 169 | 683 | 749 | 2.506338 | 1.363668 | 2.230982 | 1.078011 | 0.80285 | 0.597783 | 0.368963 | 0.578911 | 0.500396 | 0.284244 | 3.34567 | SOLUSDT | 4h |
| Entry Model 1 | partially_filled | 307 | 294 | 13 | 159 | 148 | 2.140651 | 1.04547 | 2.059472 | 1.068804 | 0.782313 | 0.517007 | 0.289116 | 0.537459 | 0.438776 | 0.217687 | 3.247557 | SOLUSDT | 4h |
| Entry Model 2 | unknown | 1260 | 1127 | 133 | 633 | 627 | 2.467595 | 1.310781 | 2.591715 | 1.133619 | 0.796806 | 0.595386 | 0.345164 | 0.577778 | 0.488021 | 0.254658 | 3.675397 | SOLUSDT | 4h |
| Entry Model 3 | filled | 17 | 15 | 2 | 11 | 6 | 14.448895 | 6.937977 | 7.295383 | 3.705882 | 0.933333 | 0.866667 | 0.8 | 1.0 | 0.333333 | 0.266667 | 3.352941 | BTCUSDT | 1h |
| Entry Model 3 | partially_filled | 4 | 2 | 2 | 3 | 1 | 19.577756 | 19.577756 | 14.519312 | 14.519312 | 1.0 | 1.0 | 1.0 | 1.0 | 0.5 | 0.5 | 3.5 | ETHUSDT | 1h |

### Model 3 fill variants
| model | fill_mode | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | none | 1955 | 1749 | 206 | 937 | 1018 | 2.40496 | 1.281679 | 2.185173 | 1.075008 | 0.792453 | 0.576329 | 0.352773 | 0.573402 | 0.482561 | 0.272727 | 3.31867 | SOLUSDT | 4h |
| Entry Model 2 | none | 1260 | 1127 | 133 | 633 | 627 | 2.467595 | 1.310781 | 2.591715 | 1.133619 | 0.796806 | 0.595386 | 0.345164 | 0.577778 | 0.488021 | 0.254658 | 3.675397 | SOLUSDT | 4h |
| Entry Model 3 | 50 | 21 | 17 | 4 | 14 | 7 | 15.052291 | 10.294118 | 8.145257 | 4.0 | 0.941176 | 0.882353 | 0.823529 | 1.0 | 0.352941 | 0.294118 | 3.380952 | BTCUSDT | 1h |

## 7. Warnings / skipped events
- aeecb2d8564207f7: invalid risk (risk is not positive; R metrics are skipped)
- 1d5493c93153ca95: invalid risk (risk is not positive; R metrics are skipped)
- 345d3bb416f1db97: invalid risk (risk is not positive; R metrics are skipped)
- c990bfb1d2cf5778: invalid risk (risk is not positive; R metrics are skipped)
- a4fc125c14927cd2: invalid risk (risk is not positive; R metrics are skipped)
- a1d67277883fab92: invalid risk (risk is not positive; R metrics are skipped)
- e040448d82b29b8f: invalid risk (risk is not positive; R metrics are skipped)
- d99f8930cf65ce3e: invalid risk (risk is not positive; R metrics are skipped)
- 275917050cd6541b: invalid risk (risk is not positive; R metrics are skipped)
- 32607efa78de6845: invalid risk (risk is not positive; R metrics are skipped)
- e633a13b24554be1: invalid risk (risk is not positive; R metrics are skipped)
- 7844af38f8b9637b: invalid risk (risk is not positive; R metrics are skipped)
- 998145200c98995e: invalid risk (risk is not positive; R metrics are skipped)
- 09efbc54b40e86da: invalid risk (risk is not positive; R metrics are skipped)
- b4550c296a654c1e: invalid risk (risk is not positive; R metrics are skipped)
- adac0a06f918fe3a: invalid risk (risk is not positive; R metrics are skipped)
- c6763cfde569f8a6: invalid risk (risk is not positive; R metrics are skipped)
- 10d246d096055fab: invalid risk (risk is not positive; R metrics are skipped)
- d6c62a0521a6d471: invalid risk (risk is not positive; R metrics are skipped)
- f58df6f4daa4f43e: invalid risk (risk is not positive; R metrics are skipped)
- dc9953f9763017e9: invalid risk (risk is not positive; R metrics are skipped)
- 917dc1b537485181: invalid risk (risk is not positive; R metrics are skipped)
- 8ba1aef6dfadd917: invalid risk (risk is not positive; R metrics are skipped)
- 7e462c4a66f2a0bc: invalid risk (risk is not positive; R metrics are skipped)
- 5c91616e4417d86f: invalid risk (risk is not positive; R metrics are skipped)
- 4e0a6003103dc002: invalid risk (risk is not positive; R metrics are skipped)
- 45171b0ebd74f7e9: invalid risk (risk is not positive; R metrics are skipped)
- 6e8535593bc1b440: invalid risk (risk is not positive; R metrics are skipped)
- f754aef5f88e0dca: invalid risk (risk is not positive; R metrics are skipped)
- 5aa98b9810f440e1: invalid risk (risk is not positive; R metrics are skipped)
- c93e7e7c3063cf30: invalid risk (risk is not positive; R metrics are skipped)
- 6737942d16983e7c: invalid risk (risk is not positive; R metrics are skipped)
- c8b81898a737be20: invalid risk (risk is not positive; R metrics are skipped)
- ee79dd74817b4107: invalid risk (risk is not positive; R metrics are skipped)
- 368167a5badec66d: invalid risk (risk is not positive; R metrics are skipped)
- 60d19a588938ae46: invalid risk (risk is not positive; R metrics are skipped)
- ddfa6b2513b7c84b: invalid risk (risk is not positive; R metrics are skipped)
- 4d399208836ed8e8: invalid risk (risk is not positive; R metrics are skipped)
- 51bb6f5b20acff89: invalid risk (risk is not positive; R metrics are skipped)
- e10671072e9da13f: invalid risk (risk is not positive; R metrics are skipped)
- 71ad932fcc1d7ca1: invalid risk (risk is not positive; R metrics are skipped)
- 20550c6a5a3b4bbf: invalid risk (risk is not positive; R metrics are skipped)
- 27fec2d52124dbe3: invalid risk (risk is not positive; R metrics are skipped)
- 54c814b4a78a02b0: invalid risk (risk is not positive; R metrics are skipped)
- 3b8823ffc56d2225: invalid risk (risk is not positive; R metrics are skipped)
- 93b2363181d2ff5e: invalid risk (risk is not positive; R metrics are skipped)
- 9bf79d0dde51f865: invalid risk (risk is not positive; R metrics are skipped)
- 949a5c5d8141a8d5: invalid risk (risk is not positive; R metrics are skipped)
- efcb119ff120cbbf: invalid risk (risk is not positive; R metrics are skipped)
- 3a7148e257dc31c7: invalid risk (risk is not positive; R metrics are skipped)

## 8. Interpretation notes
- Replay is bar-by-bar: strategies receive only candles visible at the current bar.
- Forward candles are used only after event detection for outcome measurement.
- `bars_to_*` values are 1-based future bar offsets from the signal bar.
- `*_before_invalidation` uses OHLC bar ordering only; same-bar threshold/invalidation ordering is not modeled.
- HTF-filtered event studies should usually have fewer signals than legacy/off mode.
- If strict signal count does not decrease, HTF gating is too weak.
- If score buckets remain mostly high, scoring is not calibrated enough.
