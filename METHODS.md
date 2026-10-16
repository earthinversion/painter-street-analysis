# Methods and data

## Records and channels

The analysis uses the modern instrumentation configuration at CESMD station CE89324 (Painter Street Overpass, Rio Dell). The primary set contains 22 events during 2012–2024. Earlier records are excluded because the instrumentation changed in 2010. The source archive was retrieved on September 21, 2026 UTC (September 20 locally); the source snapshot contained 32 processed events and 537 channel records across both instrumentation eras. Those archive-wide counts are not the size of the present analysis subset.

Processed CSMIP/COSMOS V2 accelerations were read with their declared units and sampling intervals. The upstream parser checked point counts, units, and declared peaks. It supplied instrument- and baseline-corrected acceleration in cm/s². Feature calculation divides by 980.665 to obtain g and uses each complete processed record without an additional feature-stage filter or threshold. Sampling intervals and durations are retained per channel in `data/channel_inventory.csv`.

| Direction | Input channels | Response channels |
| --- | --- | --- |
| Longitudinal | 1, 15, 18 | 11 |
| Transverse | 3, 17, 20 | 4, 7, 9 |
| Vertical | 2, 16, 19 | 5, 6, 8, 10 |

Input channels are at the middle bent near ground level and on the ground near the abutments. Response channels are on the deck and at the top of the middle-bent column. Missing channels are listed by event. The separate free-field station CE89462 is not used as the amplitude regressor in this release.

Peak input is the maximum absolute acceleration over the available input channels, including all three directions. It is an excitation proxy measured near the structure, not a claim of free-field motion. Peak structural response, used for reference selection, is the maximum over response channels.

## Response features and reference envelope

For a channel with acceleration samples in g, PRA is `max(abs(a))` and ordinary CAV is `sum(abs(a)) * dt`, in g s. Each feature is averaged across response channels within a horizontal direction and then across the two horizontal directions. This is a feature aggregation rule, not an interaction rule for directional structural capacities. Standardized, thresholded CAV is not used here.

The eight events with the smallest peak structural response define the reference set. Their identifiers are frozen in `predictor_config.json`; the remaining 14 events form the test set. The example refits a bivariate Gaussian to log10 PRA and log10 CAV. Squared Mahalanobis distance is compared with the 0.95 quantile of a chi-square distribution with two degrees of freedom (5.9915).

The envelope is nominal: the mean and covariance are estimated from only eight selected events, the reference observations participate in the fit, and the threshold is not calibrated against independent damage labels. `results/reference_sensitivity.csv` repeats the fit while omitting each reference event and evaluates the original 14 test events. These checks assess reference sensitivity, not damage-detection performance.

## Modal estimates and amplitude adjustment

The upstream workflow searched 1–12 Hz using frequency-domain decomposition, a separate local FDD implementation, Fourier and response spectral transfer functions, and SRIM state-space identification. The external methods used `mdof` 0.0.22; that package is not redistributed or required to run this derived-data example. OKID-ERA supplied no admissible modes in its evaluated subset and did not contribute to the ensemble. The saved configuration records model orders, quality thresholds, channel mappings, reference frequencies, and matching windows. Transfer-function pairs were 17→9 (transverse), 19→6 (vertical), and 18→11 (longitudinal).

Within each frozen mode window, the closest admissible estimate to the reference frequency was retained for each method. The event-level frequency is the median across contributing methods; `freq_spread_hz` is their sample standard deviation, missing when only one estimate contributes. Reference frequencies come from the reference-event estimates. Eighteen modes have sufficient coverage for amplitude fits. The displayed vertical mode has a reference frequency of 3.382945 Hz.

For each mode with at least eight observations, weighted least squares fits

`ln(f / f_ref) = a - beta * ln(PGA / PGA_ref)`.

`PGA_ref` is the geometric mean of the distinct input amplitudes in the modal table. Relative uncertainty is the across-method frequency spread divided by the frequency, with a floor of 0.002; missing spreads use the overall median spread. Coefficient covariance is multiplied by the larger of one and reduced chi-square. A per-mode residual discrepancy is estimated from residual variance beyond the assigned measurement variance.

The displayed trend is the fitted relationship across the observed amplitude range. Its approximate 95% band includes intercept–slope covariance. The original proposal figure omitted that covariance when drawing its approximate band; the release retains the fitted coefficients and reports this display correction explicitly. The band is conditional on the fitted model and does not propagate uncertainty in reference selection, upstream modal estimation, or shared predictor errors. It is not a prediction interval for a future earthquake or a damage probability.

## Persistent-shift assessment

Amplitude-adjusted residuals are pooled within each event with inverse-variance weights. An event-level variance component equals the nonnegative difference between residual variance across events and mean within-event variance. The example tests an intercept plus a step at each of 21 candidate event boundaries.

The original analysis used a Šidák threshold of 3.0307 for absolute z, with zero supported steps. Its reported maximum-test probability of approximately 0.647 uses an independence approximation. Candidate boundaries share observations, and error variances and amplitude corrections are estimated from the same dataset; this value is not an empirically calibrated probability for the full procedure. The release labels it accordingly and also reports a Bonferroni comparison. Neither correction establishes exact coverage for the fitted error model. No step exceeds either threshold here. Failure to reject a step does not prove that damage is absent.

## Inspection history

The identity match uses Caltrans bridge 4-236, NBI structure `04 0236`, location `01-HUM-101-R52.89`, and facility `PAINTER ST` over US Highway 101. FHWA California NBI files for 2012–2025 supply deck, superstructure, and substructure condition ratings (items 58–60). `inspection_sources.json` records the source URLs and original file checksums.

The plot uses inspection date, not file publication year. For repeated inspection dates, it retains the latest published rating and compares it with the first published value. A hollow symbol marks a changed value for that component. For example, the July 2021 substructure rating was revised from 7 to 6 without a new inspection date. The deck rating fell from 8 in 2015 to 5 in 2019 and was 7 in 2023; the substructure fell from 8 in 2015 to 5 in 2023. These records do not identify earthquake causation. A missing reconstruction entry does not establish that no intervention occurred.

## Data dictionary

| File | Rows and principal fields |
| --- | --- |
| `events.csv` | One row per earthquake; source event IDs, UTC time, magnitude, input/response PGA in g, available channels, sample rate in Hz, duration in s. `order` retains the original archive index and need not start at zero. |
| `response_features.csv` | One row per earthquake; `reference` membership; PRA in g and CAV in g s, with `_T` and `_L` directional components. |
| `mode_tracking.csv` | One row per available event/mode; direction, mode label, frequencies/spread in Hz, frequency ratio, contributing-method counts. Missing spread or damping remains blank. |
| `channel_inventory.csv` | Available channels per event; location, orientation, sample count, interval in s, rate in Hz, duration in s, PGA in g, original acceleration unit. |
| `inspection_by_file.csv` | One bridge record per publication year, with inspection date and component ratings. |
| `inspection.csv` | Original saved per-inspection table used to verify regrouping; first-published component values retained. |
| `predictor_config.json` | Frozen upstream channel mappings, reference membership, modal windows and method settings. |
| `reference_results.json` | Original numerical outputs used for regression verification; these are not additional observations. |
| `manifest.json` | SHA-256 checksums of distributed inputs and source-snapshot description. |

All tables produced by `analysis.py` are stored in `results/`. The figure is drawn from those tables, not from hard-coded result values. Numerical agreement verifies the packaged calculations; independent engineering evidence is still needed to validate damage inference.
