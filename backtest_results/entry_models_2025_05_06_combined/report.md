# Entry Models Backtest Report

Config:
- symbols: BTCUSDT, ETHUSDT
- timeframes: 5m, 15m, 30m, 1h, 4h
- models: model1, model2, model3
- warmup_bars: 100
- forward_bars: 20
- cooldown_bars: 5
- start: 2025-05-01
- end: 2025-06-30
- generated_at: 2026-04-24T12:06:33.338593+00:00

This is an event-study backtest. It does not model fees, slippage, partial exits, breakeven, or full execution management.

## 1. Overall summary
- events: 16255
- warnings: 4
- skipped_outcome_events: 2001

## 2. Summary by model
| model | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | 5530 | 4879 | 651 | 2810 | 2720 | 3.231354 | 1.490233 | 2.866304 | 1.172665 | 0.811437 | 0.638451 | 0.389219 | 0.599096 | 0.535356 | 0.304366 | 3.909042 | BTCUSDT | 30m |
| Entry Model 2 | 9365 | 8073 | 1292 | 4594 | 4771 | 3.44203 | 1.803726 | 3.118007 | 1.606323 | 0.819398 | 0.679797 | 0.463149 | 0.678697 | 0.529419 | 0.331104 | 4.594127 | ETHUSDT | 4h |
| Entry Model 3 | 1360 | 1302 | 58 | 640 | 720 | 21.919413 | 2.886751 | 10.598061 | 2.791849 | 0.884793 | 0.798003 | 0.624424 | 0.7625 | 0.548387 | 0.372504 | 3.930147 | BTCUSDT | 30m |

## 3. Summary by direction
| model | direction | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | long | 2810 | 2477 | 333 | 2810 | 0 | 3.665196 | 1.506583 | 3.294229 | 1.172939 | 0.818732 | 0.64352 | 0.396447 | 0.600356 | 0.543399 | 0.308438 | 3.925267 | BTCUSDT | 30m |
| Entry Model 1 | short | 2720 | 2402 | 318 | 0 | 2720 | 2.783967 | 1.470655 | 2.425018 | 1.17227 | 0.803913 | 0.633222 | 0.381765 | 0.597794 | 0.527061 | 0.300167 | 3.892279 | ETHUSDT | 15m |
| Entry Model 2 | long | 4594 | 3970 | 624 | 4594 | 0 | 3.425804 | 1.843862 | 3.034221 | 1.577691 | 0.83199 | 0.694458 | 0.473048 | 0.669569 | 0.538287 | 0.338791 | 4.624946 | ETHUSDT | 4h |
| Entry Model 2 | short | 4771 | 4103 | 668 | 0 | 4771 | 3.45773 | 1.760446 | 3.199077 | 1.638398 | 0.807214 | 0.665611 | 0.453571 | 0.687487 | 0.520838 | 0.323666 | 4.564452 | ETHUSDT | 15m |
| Entry Model 3 | long | 640 | 617 | 23 | 640 | 0 | 35.687333 | 2.857458 | 15.378429 | 2.732505 | 0.896272 | 0.82658 | 0.640194 | 0.75 | 0.580227 | 0.36953 | 3.940625 | BTCUSDT | 30m |
| Entry Model 3 | short | 720 | 685 | 35 | 0 | 720 | 9.518234 | 2.916344 | 6.292241 | 2.851429 | 0.874453 | 0.772263 | 0.610219 | 0.773611 | 0.519708 | 0.375182 | 3.920833 | ETHUSDT | 1h |

## 4. Summary by timeframe
| model | timeframe | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | 15m | 1105 | 960 | 145 | 560 | 545 | 3.317382 | 1.506626 | 2.180298 | 1.141473 | 0.816667 | 0.635417 | 0.40625 | 0.59095 | 0.526042 | 0.303125 | 3.898643 | ETHUSDT | 15m |
| Entry Model 1 | 1h | 265 | 234 | 31 | 137 | 128 | 2.260306 | 1.452355 | 2.114826 | 1.273523 | 0.760684 | 0.628205 | 0.371795 | 0.607547 | 0.525641 | 0.286325 | 3.69434 | BTCUSDT | 1h |
| Entry Model 1 | 30m | 502 | 459 | 43 | 277 | 225 | 6.088753 | 1.517471 | 3.329616 | 1.067037 | 0.814815 | 0.636166 | 0.389978 | 0.551793 | 0.557734 | 0.313725 | 3.832669 | BTCUSDT | 30m |
| Entry Model 1 | 4h | 69 | 67 | 2 | 35 | 34 | 1.829972 | 0.969626 | 2.267528 | 1.559652 | 0.791045 | 0.462687 | 0.328358 | 0.681159 | 0.358209 | 0.268657 | 3.101449 | BTCUSDT | 4h |
| Entry Model 1 | 5m | 3589 | 3159 | 430 | 1801 | 1788 | 2.891685 | 1.485306 | 3.075823 | 1.173491 | 0.813549 | 0.644191 | 0.386515 | 0.606018 | 0.539411 | 0.305476 | 3.954305 | ETHUSDT | 5m |
| Entry Model 2 | 15m | 1906 | 1636 | 270 | 948 | 958 | 3.583532 | 1.820969 | 3.138921 | 1.562804 | 0.82335 | 0.687042 | 0.466381 | 0.667891 | 0.529951 | 0.328851 | 4.540399 | BTCUSDT | 15m |
| Entry Model 2 | 1h | 455 | 392 | 63 | 219 | 236 | 3.294847 | 1.85275 | 2.664033 | 1.514504 | 0.844388 | 0.665816 | 0.466837 | 0.650549 | 0.545918 | 0.354592 | 4.305495 | ETHUSDT | 1h |
| Entry Model 2 | 30m | 921 | 805 | 116 | 444 | 477 | 3.167016 | 1.75087 | 2.746154 | 1.438042 | 0.814907 | 0.669565 | 0.445963 | 0.630836 | 0.545342 | 0.33913 | 4.44734 | ETHUSDT | 30m |
| Entry Model 2 | 4h | 115 | 107 | 8 | 56 | 59 | 3.766939 | 1.527623 | 3.346828 | 1.992618 | 0.841121 | 0.71028 | 0.476636 | 0.695652 | 0.523364 | 0.308411 | 3.930435 | ETHUSDT | 4h |
| Entry Model 2 | 5m | 5968 | 5133 | 835 | 2927 | 3041 | 3.444528 | 1.807736 | 3.199558 | 1.643564 | 0.816482 | 0.679525 | 0.464251 | 0.691354 | 0.525619 | 0.329242 | 4.668733 | ETHUSDT | 5m |
| Entry Model 3 | 15m | 829 | 803 | 26 | 387 | 442 | 5.425133 | 2.751787 | 6.300096 | 2.751773 | 0.879203 | 0.794521 | 0.612702 | 0.755127 | 0.545455 | 0.371108 | 3.960193 | ETHUSDT | 15m |
| Entry Model 3 | 1h | 230 | 220 | 10 | 110 | 120 | 20.663959 | 4.541361 | 7.039785 | 3.252954 | 0.904545 | 0.854545 | 0.759091 | 0.813043 | 0.568182 | 0.431818 | 3.895652 | ETHUSDT | 1h |

_Showing 12 of 13 rows._

## 5. Score bucket analysis
| model | score_bucket | count | valid_outcome_count | skipped_outcome_count | long_count | short_count | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_0_5r_rate | hit_1r_rate | hit_2r_rate | invalidation_rate | hit_1r_before_invalidation_rate | hit_2r_before_invalidation_rate | avg_score | best_symbol | best_timeframe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry Model 1 | high | 5042 | 4448 | 594 | 2607 | 2435 | 3.220635 | 1.506054 | 3.003491 | 1.203418 | 0.811151 | 0.642986 | 0.395908 | 0.610472 | 0.536646 | 0.307104 | 4.0 | BTCUSDT | 30m |
| Entry Model 1 | low | 15 | 14 | 1 | 7 | 8 | 1.182699 | 0.614642 | 2.027679 | 2.405152 | 0.714286 | 0.285714 | 0.142857 | 0.8 | 0.142857 | 0.071429 | 2.0 | BTCUSDT | 15m |
| Entry Model 1 | medium | 473 | 417 | 56 | 196 | 277 | 3.414473 | 1.396094 | 1.431137 | 0.761988 | 0.817746 | 0.601918 | 0.326139 | 0.471459 | 0.534772 | 0.282974 | 3.0 | ETHUSDT | 15m |
| Entry Model 2 | high | 9337 | 8050 | 1287 | 4576 | 4761 | 3.435911 | 1.800529 | 3.114631 | 1.608696 | 0.819255 | 0.679379 | 0.462484 | 0.67934 | 0.52882 | 0.330311 | 4.598908 | ETHUSDT | 15m |
| Entry Model 2 | medium | 28 | 23 | 5 | 18 | 10 | 5.583736 | 3.045965 | 4.299516 | 0.881181 | 0.869565 | 0.826087 | 0.695652 | 0.464286 | 0.73913 | 0.608696 | 3.0 | ETHUSDT | 30m |
| Entry Model 3 | high | 1269 | 1218 | 51 | 602 | 667 | 23.195155 | 2.984501 | 11.07898 | 2.852778 | 0.889163 | 0.805419 | 0.633826 | 0.77305 | 0.541872 | 0.369458 | 4.0 | BTCUSDT | 30m |
| Entry Model 3 | low | 4 | 4 | 0 | 0 | 4 | 1.562279 | 1.482259 | 3.089098 | 2.27721 | 1.0 | 0.5 | 0.5 | 0.5 | 0.5 | 0.5 | 2.0 | ETHUSDT | 1h |
| Entry Model 3 | medium | 87 | 80 | 7 | 38 | 49 | 3.514095 | 1.875992 | 3.651523 | 1.609854 | 0.8125 | 0.7 | 0.4875 | 0.62069 | 0.65 | 0.4125 | 3.0 | BTCUSDT | 15m |

## 6. Warnings / skipped events
- Entry Model 3 BTCUSDT 5m 0: missing optional LTF history 1m; model3 context will be incomplete
- Entry Model 3 ETHUSDT 5m 0: missing optional LTF history 1m; model3 context will be incomplete
- Entry Model 3 BTCUSDT 4h 0: missing optional HTF history 1d; model3 context will be incomplete
- Entry Model 3 ETHUSDT 4h 0: missing optional HTF history 1d; model3 context will be incomplete
- f370aebd28c4c1ba: invalid risk (risk is not positive; R metrics are skipped)
- e67e7a208e39216e: invalid risk (risk is not positive; R metrics are skipped)
- 842d63f150d184e5: invalid risk (risk is not positive; R metrics are skipped)
- 9a506a84afb2a0bb: invalid risk (risk is not positive; R metrics are skipped)
- 1205ad67bde6a006: invalid risk (risk is not positive; R metrics are skipped)
- 995ffdeb54764add: invalid risk (risk is not positive; R metrics are skipped)
- 56bb134ae826f6bf: invalid risk (risk is not positive; R metrics are skipped)
- 17aff481dc8f9f1b: invalid risk (risk is not positive; R metrics are skipped)
- a4d30c227526031b: invalid risk (risk is not positive; R metrics are skipped)
- fa8c3136e6238502: invalid risk (risk is not positive; R metrics are skipped)
- d6a77d24a307ad86: invalid risk (risk is not positive; R metrics are skipped)
- 8c1773cbbae740ca: invalid risk (risk is not positive; R metrics are skipped)
- 6920d4a86b603935: invalid risk (risk is not positive; R metrics are skipped)
- 293d297d4dfe89e1: invalid risk (risk is not positive; R metrics are skipped)
- f44f3dcd17c615f2: invalid risk (risk is not positive; R metrics are skipped)
- 0140f0b97f4cc1a1: invalid risk (risk is not positive; R metrics are skipped)
- 8ca3731b6052c380: invalid risk (risk is not positive; R metrics are skipped)
- 6de737e733325756: invalid risk (risk is not positive; R metrics are skipped)
- 7fa27a7260915810: invalid risk (risk is not positive; R metrics are skipped)
- 7c8f3a1c45cb3c1e: invalid risk (risk is not positive; R metrics are skipped)
- 47e74880dbcdc680: invalid risk (risk is not positive; R metrics are skipped)
- 5dd64cb6f536f135: invalid risk (risk is not positive; R metrics are skipped)
- 1cfbe91cd0e678d0: invalid risk (risk is not positive; R metrics are skipped)
- 6fc484e1e3d38946: invalid risk (risk is not positive; R metrics are skipped)
- cd6d73abff56e407: invalid risk (risk is not positive; R metrics are skipped)
- bbe8732d2263f2d8: invalid risk (risk is not positive; R metrics are skipped)
- 4fe9baf6d34f5e56: invalid risk (risk is not positive; R metrics are skipped)
- 81c38ccae508e96f: invalid risk (risk is not positive; R metrics are skipped)
- afa4ce0799399112: invalid risk (risk is not positive; R metrics are skipped)
- d92a2b1c8f2057cd: invalid risk (risk is not positive; R metrics are skipped)
- 7dca276677070597: invalid risk (risk is not positive; R metrics are skipped)
- 6cb8d26565bcfba1: invalid risk (risk is not positive; R metrics are skipped)
- 7e0c2afc3b3fa7ef: invalid risk (risk is not positive; R metrics are skipped)
- 4a2f79897c1fe1e0: invalid risk (risk is not positive; R metrics are skipped)
- a55f8a9d91bb17be: invalid risk (risk is not positive; R metrics are skipped)
- f067955731e4f888: invalid risk (risk is not positive; R metrics are skipped)
- 5cb0d684a5a26cd3: invalid risk (risk is not positive; R metrics are skipped)
- 77c6a7629a0b960d: invalid risk (risk is not positive; R metrics are skipped)
- 9616a5714c9e521b: invalid risk (risk is not positive; R metrics are skipped)
- eceeef9f8bb72888: invalid risk (risk is not positive; R metrics are skipped)
- d4572b11e5bd6186: invalid risk (risk is not positive; R metrics are skipped)
- e0699504529538fe: invalid risk (risk is not positive; R metrics are skipped)
- fcebf9d4a2581319: invalid risk (risk is not positive; R metrics are skipped)
- f14d9a28c428742a: invalid risk (risk is not positive; R metrics are skipped)
- ee76aec11431cb2b: invalid risk (risk is not positive; R metrics are skipped)
- 4a0d2a840c0ad22f: invalid risk (risk is not positive; R metrics are skipped)
- 80d3f5ddcfb595f4: invalid risk (risk is not positive; R metrics are skipped)
- b69304189ec34bfa: invalid risk (risk is not positive; R metrics are skipped)
- bb8b1977b04d8a89: invalid risk (risk is not positive; R metrics are skipped)
- bb45b0b5afef14c6: invalid risk (risk is not positive; R metrics are skipped)

## 7. Interpretation notes
- Replay is bar-by-bar: strategies receive only candles visible at the current bar.
- Forward candles are used only after event detection for outcome measurement.
- `bars_to_*` values are 1-based future bar offsets from the signal bar.
- `*_before_invalidation` uses OHLC bar ordering only; same-bar threshold/invalidation ordering is not modeled.
