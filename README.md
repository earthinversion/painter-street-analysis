# Painter Street Overpass response analysis

This repository examines earthquake response at the Painter Street Overpass in Rio Dell, California. It contains derived measurements from 22 earthquakes recorded during 2012–2024, National Bridge Inventory inspection records, and code for the response-feature, frequency–amplitude, and persistent-shift analyses. The bridge is identified by CESMD station CE89324, Caltrans bridge number 4-236, and NBI structure `04 0236`.

Peak response acceleration and cumulative absolute velocity (CAV) place 12 of 14 test events outside a nominal 95% envelope fitted to eight weak-motion reference events. The tracked 3.38 Hz vertical mode decreases by approximately 5.5% across the observed input-amplitude range. Event-level tests find no persistent frequency shift after amplitude adjustment and the specified multiple-comparison correction. These results describe response variability; they do not establish earthquake damage or its absence. Inspection records provide separate evidence of changes in component condition, without identifying their cause.

![Response features, amplitude-dependent modal frequency, and inspection ratings at Painter Street Overpass.](figures/painter-street.png)

**Figure 1.** (a) Response features and the nominal reference envelope. Open circles identify the eight reference events; orange triangles identify test events outside the envelope. (b) Relative change in the 3.38 Hz mode versus peak input PGA. The line is a weighted log-frequency fit; shading is an approximate 95% coefficient-uncertainty interval, including covariance. (c) NBI component ratings by inspection date, using the latest published value for each inspection. Hollow symbols mark a revised rating at an unchanged inspection date. Lines connect inspection records and do not date physical changes. No damage state is assigned. [Vector figure](figures/painter-street.pdf).

## Reproduce the example

Use Python 3.11 and the pinned dependencies:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python analysis.py
python -m unittest discover -s tests -v
```

The analysis runs offline, verifies input checksums, recomputes the numerical results, compares them with saved reference results, and writes tables to `results/` and figures to `figures/`. To repeat only the numerical analysis, use `python analysis.py --no-figure`. To change the output location, use `--output /path/to/results`; figures are written beside that directory. To redraw the figure from existing results, run `python plot.py`.

The example starts from derived response features and modal estimates. It does not download or redistribute waveforms, rerun modal identification, or include the broader adaptive-monitoring workflow. [Methods and data definitions](METHODS.md) describe the upstream calculations, channels, reference selection, statistical assumptions, and inspection provenance. [Verification](VERIFICATION.md) records what was reproduced and the limits of that check.

## Sources and reuse

Strong-motion records were accessed through [CESMD](https://doi.org/10.5066/P13HTZQS) and provided by CGS/CSMIP through the Caltrans–CGS bridge instrumentation program. Inspection records are from the [FHWA National Bridge Inventory](https://www.fhwa.dot.gov/bridge/nbi/ascii.cfm). The response features follow the human–machine collaboration framework of [Muin, Chern, and Mosalam (2024)](https://doi.org/10.1061/JBENF2.BEENG-6587). This example is an independent preliminary application, not a validation of bridge damage classification.

Original code is distributed under the MIT license. Original text, figures, and derived analysis tables are licensed under CC BY 4.0; source metadata retain their original terms. See [source notices](SOURCE_NOTICES.md). Citation metadata are in `CITATION.cff`. This is a release candidate for review; no Zenodo DOI has been assigned.
