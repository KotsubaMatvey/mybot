# ICT Refactor Backtest Comparison

Generated after validating the current ICT / HTF-LTF / displacement refactor on `data/history`.

## 1. Test status

- Unit tests: `python -m unittest tests/test_ict_refactor.py` passed, 7 tests OK.
- Pytest: `pytest` passed, 12 tests OK, 13 third-party deprecation warnings from matplotlib/pyparsing.
- Smoke backtest: passed, 117 events, 0 runtime warnings, 5 skipped outcomes.
- Backtest runtime warnings: 0 across all requested runs.
- Missing data: none for BTCUSDT, ETHUSDT, SOLUSDT across `1m, 3m, 5m, 15m, 30m, 1h, 4h, 1d`.
- Data note: all required BTC/ETH/SOL files in `data/history` were refreshed through the project downloader before backtests to avoid mixed download windows.

One report/metrics bug was fixed before final runs: events with no valid R outcome, including end-of-history events without forward candles, are now counted in `skipped_outcome_count`.

## 2. Backtest configs

- `legacy_after_ict_refactor`: BTCUSDT, ETHUSDT, SOLUSDT; `5m 15m 30m 1h 4h`; models 1/2/3; `--htf-mode off`; `--require-displacement false`; `--forward-bars 20`.
- `htf_soft_after_ict_refactor`: same symbols/timeframes/models; `--htf-mode soft`; `--require-displacement true`; `--model3-fill-threshold 0.5`.
- `htf_strict_after_ict_refactor`: same symbols/timeframes/models; `--htf-mode strict`; `--require-displacement true`; `--model3-fill-threshold 0.5`.
- `model3_fill_25`: BTCUSDT, ETHUSDT; `5m 15m 30m 1h`; model3 only; strict; displacement required; fill threshold 0.25.
- `model3_fill_50`: same as above, fill threshold 0.5.
- `model3_fill_100`: same as above, fill threshold 1.0.

## 3. Overall comparison

| run | events | valid | skipped | avg_mfe_r | median_mfe_r | avg_mae_r | median_mae_r | hit_1r_before_inv | hit_2r_before_inv | invalidation_rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| legacy/off | 3236 | 2893 | 343 | 2.503679 | 1.294451 | 2.378569 | 1.100645 | 0.483927 | 0.265814 | 0.577874 |
| htf soft | 1440 | 1302 | 138 | 2.830121 | 1.359240 | 2.549738 | 1.062366 | 0.479263 | 0.277266 | 0.570833 |
| htf strict | 704 | 648 | 56 | 2.782807 | 1.430424 | 2.579714 | 0.953658 | 0.504630 | 0.325617 | 0.531250 |
| model3 fill 25 | 23 | 18 | 5 | 9.083174 | 5.888486 | 7.517218 | 4.511580 | 0.555556 | 0.500000 | 0.826087 |
| model3 fill 50 | 21 | 18 | 3 | 9.083174 | 5.888486 | 7.517218 | 4.511580 | 0.555556 | 0.500000 | 0.809524 |
| model3 fill 100 | 14 | 13 | 1 | 4.918568 | 5.693182 | 9.907313 | 8.618352 | 0.461538 | 0.461538 | 0.928571 |

HTF strict reduced signal count by 78.2 percent versus off mode and improved the main metric from 0.483927 to 0.504630. It also reduced invalidation from 0.577874 to 0.531250 and raised median MFE from 1.294451R to 1.430424R.

## 4. Model comparison

| model | mode | events | valid | skipped | median_mfe_r | avg_mfe_r | invalidation_rate | hit_1r_before_inv | hit_2r_before_inv | avg_score |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Entry Model 1 | off | 1955 | 1749 | 206 | 1.281679 | 2.404960 | 0.573402 | 0.482561 | 0.272727 | 3.318670 |
| Entry Model 1 | soft | 667 | 618 | 49 | 1.221309 | 2.151696 | 0.517241 | 0.475728 | 0.268608 | 3.670165 |
| Entry Model 1 | strict | 324 | 308 | 16 | 1.242285 | 2.246167 | 0.481481 | 0.490260 | 0.327922 | 4.052469 |
| Entry Model 2 | off | 1260 | 1127 | 133 | 1.310781 | 2.467595 | 0.577778 | 0.488021 | 0.254658 | 3.675397 |
| Entry Model 2 | soft | 685 | 604 | 81 | 1.403879 | 2.673317 | 0.582482 | 0.478477 | 0.266556 | 3.875912 |
| Entry Model 2 | strict | 342 | 306 | 36 | 1.524155 | 2.644277 | 0.543860 | 0.516340 | 0.307190 | 4.304094 |
| Entry Model 3 | off | 21 | 17 | 4 | 10.294118 | 15.052291 | 1.000000 | 0.352941 | 0.294118 | 3.380952 |
| Entry Model 3 | soft | 88 | 80 | 8 | 5.619318 | 9.254832 | 0.886364 | 0.512500 | 0.425000 | 3.852273 |
| Entry Model 3 | strict | 38 | 34 | 4 | 5.550841 | 8.890900 | 0.842105 | 0.529412 | 0.470588 | 4.263158 |

Entry Model 1: strict is modestly better than off on the primary metric and clearly better on invalidation. Median MFE is slightly lower than off, so the improvement is more about filtering bad outcomes than expanding upside.

Entry Model 2: strict is the strongest result. It cuts count from 1260 to 342, raises median MFE to 1.524155R, improves hit 1R before invalidation to 0.516340, and lowers invalidation versus off. This supports the expectation that HTF context reduces Model 2 noise.

Entry Model 3: strict improves hit 1R before invalidation versus off, but invalidation remains high at 0.842105. The avg/median gap is smaller than legacy/off, but the sample is small and still risky.

## 5. HTF mode conclusion

- Off mode gives the most signals but more noise and weaker validation quality.
- Soft mode reduces count substantially but does not improve the main hit 1R before invalidation metric overall. It helps Model 3, but Model 1 and Model 2 are not clearly better than off.
- Strict mode is currently the best overall validation mode: fewer events, better hit 1R before invalidation, better hit 2R before invalidation, lower invalidation, and better median MFE.
- Strict does not look too strict on this sample. It still produces 704 events and improves quality. The main caveat is that score distribution becomes too high-heavy.

## 6. Model 3 fill threshold conclusion

| threshold | events | valid | skipped | median_mfe_r | avg_mfe_r | invalidation_rate | hit_1r_before_inv | hit_2r_before_inv |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 25 percent | 23 | 18 | 5 | 5.888486 | 9.083174 | 0.826087 | 0.555556 | 0.500000 |
| 50 percent | 21 | 18 | 3 | 5.888486 | 9.083174 | 0.809524 | 0.555556 | 0.500000 |
| 100 percent | 14 | 13 | 1 | 5.693182 | 4.918568 | 0.928571 | 0.461538 | 0.461538 |

The 50 percent fill threshold is the best default from this sample. It preserves the same valid outcome quality as 25 percent with fewer skipped outcomes and lower invalidation. The 100 percent variant is cleaner by count but worse on invalidation and hit 1R before invalidation.

## 7. Score calibration

Score buckets are not yet well calibrated.

- Strict Model 1: high has 256 events and hit 1R before invalidation 0.485597; medium has 67 events and 0.515625.
- Strict Model 2: high has 320 events and 0.500000; medium has 21 events and 0.750000.
- Strict Model 3: high has 35 events and 0.500000; medium has 3 events and 1.000000.

The high bucket does not consistently outperform medium. In strict mode, most events are high, so the score distribution is still compressed upward.

## 8. Displacement analysis

Displacement is useful for Entry Model 1 and mostly neutral for Entry Model 2 in this implementation.

- Strict Model 1 has displacement: 206 events, hit 1R before invalidation 0.555000, invalidation 0.402913, median MFE 1.401566.
- Strict Model 1 weak_or_none: 118 events, hit 1R before invalidation 0.370370, invalidation 0.618644, median MFE 0.996160.
- Strict Model 2 only appears in `has_displacement` because IFVG candidates require displacement.
- Strict Model 3 has displacement: 28 events, hit 1R before invalidation 0.480000, invalidation 0.892857.
- Strict Model 3 weak_or_none: 10 events, hit 1R before invalidation 0.666667, invalidation 0.700000.

The Model 3 displacement relationship is not clean. This suggests Model 3 source/entry risk quality needs more calibration before treating displacement as sufficient confirmation.

## 9. Problems found

- Fixed: report/metrics skipped outcome counting did not include events with no valid R outcome when no forward candles were available.
- Persistent: invalid risk skipped outcomes remain common: 343 in legacy/off, 138 in soft, 56 in strict, and 1 to 5 in Model 3 fill variants.
- Score calibration is weak: strict mode is high-score heavy and medium sometimes performs better than high.
- Model 3 has high invalidation even in strict mode: 0.842105 in the full strict run and 0.809524 at the 50 percent fill variant.
- No missing history after refresh.
- No detector runtime exceptions or CLI failures in final runs.

## 10. Recommended next actions

- Fix or audit invalid risk generation paths, especially end-of-zone/invalidation placement for skipped outcome events.
- Calibrate score weighting so high bucket consistently beats medium and low; do not add new signals.
- Keep strict mode as the default validation candidate for current Entry Models.
- Keep Model 3 fill threshold at 0.5 for now.
- Treat Entry Model 2 strict as the strongest current candidate.
- Treat Entry Model 3 as promising but not production-ready until invalidation and risk placement improve.
- Run the next comparison on a longer, fixed date range with all required timeframes aligned by `--start` and `--end`.
