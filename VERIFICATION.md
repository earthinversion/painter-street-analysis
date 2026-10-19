# Verification

We checked the package on October 18, 2026 using Python 3.11.15 in a clean environment with dependencies from `requirements-lock.txt`. All installed versions matched the lock file, and `pip check` reported no broken requirements. The analysis ran offline from the distributed inputs and regenerated its tables and figure. Nine tests passed, covering numerical reproduction, input checksums, invalid or singular features, row-order invariance, missing predictor spread, inspection-date revisions, horizontal feature aggregation, and input PGA/reference selection from the channel inventory.

| Quantity | Reproduced value |
| --- | --- |
| Events / reference / test | 22 / 8 / 14 |
| Test events outside nominal envelope | 12 |
| Tracked vertical reference frequency | 3.382945 Hz |
| Fitted frequency change across input range | −5.532574% |
| Candidate persistent shifts | 21 |
| Largest absolute z | 1.973665 |
| Nominal / Šidák / Bonferroni supported shifts | 1 / 0 / 0 |
| Unique inspection dates | 7 |

All 18 modes’ fitted coefficients, coefficient standard errors, discrepancy terms, and residual spreads were compared with the original saved outputs (`rtol=1e-8`, `atol=1e-10`). The reference mean and covariance were checked to `rtol=1e-9`, `atol=1e-11`; flagged-event identities and inspection ratings were compared exactly. Input checksums are recorded in `data/manifest.json`.

Omitting one reference event at a time flags 12–13 of the original 14 test events. This is a sensitivity check on the fitted envelope, not a false-positive estimate. Both multiple-testing corrections yield zero supported steps. The reported maximum-test probability assumes independent tests; the fitted error model and dependence among candidate boundaries limit its interpretation.

The figure includes all 22 modal observations, the fitted trend, and the coefficient interval with intercept–slope covariance. Inspection markers distinguish revised ratings from new inspection dates.

This verification establishes reproducibility from the supplied derived measurements. It does not repeat waveform parsing or modal identification and does not validate damage attribution against independent damage labels.
