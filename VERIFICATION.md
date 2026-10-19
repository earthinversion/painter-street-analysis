# Verification

The release candidate was rechecked on October 18, 2026 using Python 3.11.15 in a newly created virtual environment, with the exact dependencies installed from `requirements-lock.txt`. All installed versions matched the lock file, and `pip check` reported no broken requirements. The analysis ran offline from the distributed inputs and regenerated its tables and figure. Nine tests passed, covering numerical reproduction, input checksums, invalid or singular features, row-order invariance, missing predictor spread, inspection-date revisions, horizontal feature aggregation, and input PGA/reference selection from the channel inventory.

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

Omitting one reference event at a time flags 12–13 of the original 14 test events. This is a sensitivity check on the fitted envelope, not a false-positive estimate. The original maximum-test probability is retained under an explicit independence-approximation label. The added Bonferroni comparison yields the same zero-step conclusion; estimated error models and correlated features still limit its interpretation.

The release figure shows the full observed frequency range, including an observation near +4.7% that fell outside the older proposal figure’s plotting limits. Its approximate coefficient band includes intercept–slope covariance. Neither change alters the underlying observations or fitted coefficients. The PDF is 7.2 × 7.3 inches with embedded non-Type-3 fonts, minimum 12 pt text, and a 450 dpi PNG export. The rendered figure was inspected for clipping and label overlap.

This verification establishes reproducibility from the supplied derived measurements. It does not repeat waveform parsing or modal identification and does not validate damage attribution against independent damage labels. The package has not yet been archived on Zenodo or assigned a DOI.

## October 18 proposal alignment

The live GitHub `main` matched the local starting commit, `d05a8ea1dc529faf71644d23b232be039319e0c2`, when checked for this revision. The proposed `0.1.0-rc2` changes documentation and citation metadata; the distributed inputs, numerical code, saved results, and repository figure remain unchanged. All saved CSV result tables reproduce within `rtol=1e-8`, `atol=1e-10` in the clean locked environment.

The proposal reports the same 22 events, eight response-selected reference events, 12 flags among 14 test events, approximately 5.5% amplitude-dependent frequency decline, and no persistent shift above the nominal multiple-testing threshold. Its bridge validation text now keeps uncertain cases unresolved and distinguishes damage from earthquake causation. These are proposed validation rules, not new validation results from this package.

The proposal uses a separate four-panel layout: its panels B, C, and D correspond to this repository's panels (a), (b), and (c); its locator and sensor schematic are additional context. The high-frequency observation was already visible in the reviewed proposal, but the uncertainty band still omitted intercept–slope covariance. That band and its generating source were corrected on October 18. The corrected proposal's fitted curve, covariance band, and all 22 modal observations were checked against this package's numerical results to within 0.001 PDF point. Numerical estimates and conclusions were unchanged. The repository figure already included covariance and the full observed range.

Proposal figure checked: `figures/bridge_painter_street.pdf` in the proposal source directory.

SHA-256: `df60ca2c4f1b1c13a8daef2f52a37e192ca3a5ffbe55afdf49297718de29eca0`.

The proposed author list is Utpal Kumar, followed by Khalid M. Mosalam. Final citation confirmation remains pending. No release tag, Zenodo publication, DOI, or author-confirmation status is asserted by these checks. See the release steps in `README.md`.
