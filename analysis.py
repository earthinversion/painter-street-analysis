"""Reproduce the Painter Street analysis from derived response measurements."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2, norm

ROOT = Path(__file__).resolve().parent


def novelty(features):
    """Fit the two-feature Gaussian reference model in log10 coordinates."""
    frame = features.copy()
    values = frame[["PRA", "CAV"]].to_numpy(float)
    if not np.isfinite(values).all() or (values <= 0).any():
        raise ValueError("PRA and CAV must be finite and positive")
    reference = frame.reference.to_numpy(bool)
    if reference.sum() < 3:
        raise ValueError("At least three reference observations are required")
    x = np.log10(values)
    mean, covariance = x[reference].mean(0), np.cov(x[reference].T)
    if np.linalg.matrix_rank(covariance) != 2:
        raise ValueError("Reference feature covariance is singular")
    delta = x - mean
    frame["MD2"] = np.einsum("ij,jk,ik->i", delta, np.linalg.inv(covariance), delta)
    threshold = float(chi2.ppf(0.95, 2))
    frame["novel"] = frame.MD2 >= threshold
    return frame, dict(mean=mean.tolist(), cov=covariance.tolist(), threshold_md2=threshold,
                      n_reference=int(reference.sum()), n_test=int((~reference).sum()),
                      n_novel_test=int(frame.loc[~reference, "novel"].sum()),
                      n_novel_reference=int(frame.loc[reference, "novel"].sum()))


def amplitude(tracking):
    """Fit log frequency ratio = intercept - beta * log(input/reference input)."""
    tr = tracking.copy()
    if not np.isfinite(tr[["pga_input_g", "freq_hz", "freq_ratio"]]).all().all():
        raise ValueError("Modal frequency and input amplitude must be finite")
    if (tr[["pga_input_g", "freq_hz", "freq_ratio"]] <= 0).any().any():
        raise ValueError("Modal frequency and input amplitude must be positive")
    a_ref = float(np.exp(np.mean(np.log(tr.pga_input_g.unique()))))
    tr["ln_ratio"] = np.log(tr.freq_ratio)
    tr["ln_amp"] = np.log(tr.pga_input_g / a_ref)
    spread = tr.freq_spread_hz.fillna(float(np.nanmedian(tr.freq_spread_hz)))
    tr["sigma"] = np.maximum(spread / tr.freq_hz, 0.002)
    rows, residuals = [], []
    for (direction, mode), group in tr.groupby(["direction", "mode"]):
        if len(group) < 8:
            continue
        x = np.column_stack([np.ones(len(group)), -group.ln_amp.to_numpy()])
        y, weights = group.ln_ratio.to_numpy(), 1 / group.sigma.to_numpy() ** 2
        covariance = np.linalg.inv((x.T * weights) @ x)
        coefficient = covariance @ ((x.T * weights) @ y)
        residual = y - x @ coefficient
        reduced_chi2 = float((weights * residual**2).sum() / (len(group) - 2))
        covariance *= max(reduced_chi2, 1.0)
        discrepancy = float(np.sqrt(max(np.mean(residual**2) - np.mean(group.sigma**2), 0)))
        rows.append(dict(direction=direction, mode=mode, n_events=len(group),
                         reference_freq_hz=float(group.reference_freq_hz.iloc[0]),
                         a=float(coefficient[0]), beta=float(coefficient[1]),
                         a_sd=float(np.sqrt(covariance[0, 0])),
                         beta_sd=float(np.sqrt(covariance[1, 1])),
                         a_beta_cov=float(covariance[0, 1]), discrepancy_sd=discrepancy,
                         chi2_per_dof=reduced_chi2,
                         amp_range_factor=float(group.pga_input_g.max()/group.pga_input_g.min()),
                         resid_sd=float(np.std(residual, ddof=1))))
        group = group.copy()
        group["resid"] = residual
        group["sigma_total"] = np.sqrt(group.sigma**2 + discrepancy**2)
        residuals.append(group)
    if not rows:
        raise ValueError("No mode has at least eight observations")
    return pd.DataFrame(rows), pd.concat(residuals), a_ref


def weighted_fit(x, y, w):
    covariance = np.linalg.pinv((x.T * w) @ x)
    return covariance @ ((x.T * w) @ y), covariance


def changepoints(residuals, events):
    """Evaluate candidate steps using event-level residuals and estimated errors."""
    rows = []
    for order, group in residuals.groupby("order"):
        w = 1 / np.maximum(group.sigma_total.to_numpy(), 1e-4)**2
        rows.append(dict(order=order, event=group.event.iloc[0], n_modes=len(group),
                         resid=float(w @ group.resid / w.sum()), se_within=float(1/np.sqrt(w.sum()))))
    event = pd.DataFrame(rows).sort_values("order").reset_index(drop=True)
    event = event.merge(events[["event", "time", "pga_input_g"]], on="event", validate="one_to_one")
    tau2 = max(float(np.var(event.resid, ddof=1) - np.mean(event.se_within**2)), 0)
    event["sd_total"] = np.sqrt(event.se_within**2 + tau2)
    y, w = event.resid.to_numpy(), 1/event.sd_total.to_numpy()**2
    n, rows = len(event), []
    sidak = float(norm.ppf(1 - (1 - 0.95**(1/(n-1)))/2))
    bonferroni = float(norm.ppf(1 - 0.05/(2*(n-1))))
    for i in range(1, n):
        x = np.column_stack([np.ones(n), (np.arange(n) >= i).astype(float)])
        b, covariance = weighted_fit(x, y, w)
        sd = float(np.sqrt(covariance[1, 1]))
        z = float(b[1]/sd)
        rows.append(dict(event=event.event.iloc[i], time=event.time.iloc[i], n_before=i,
                         n_after=n-i, step_pct=float(100*np.expm1(b[1])),
                         lower_pct=float(100*np.expm1(b[1]-1.96*sd)),
                         upper_pct=float(100*np.expm1(b[1]+1.96*sd)), z=z,
                         supported_nominal=abs(z)>1.96, supported_sidak=abs(z)>sidak,
                         supported_bonferroni=abs(z)>bonferroni))
    cp = pd.DataFrame(rows)
    summary = dict(n_events=n, n_candidates=n-1, event_variance_component_pct=100*np.sqrt(tau2),
                   max_abs_z=float(cp.z.abs().max()), sidak_z_crit_fwer05=sidak,
                   sidak_independence_approximation_p=float(1-(2*norm.cdf(cp.z.abs().max())-1)**(n-1)),
                   n_supported_nominal=int(cp.supported_nominal.sum()),
                   n_supported_fwer=int(cp.supported_sidak.sum()),
                   n_supported_bonferroni=int(cp.supported_bonferroni.sum()))
    return event, cp, summary


def inspection_history(by_file):
    """Keep the latest published rating for each inspection; retain earlier values."""
    rows = []
    for date, group in by_file.sort_values("file_year").groupby("inspected", sort=True):
        last, first = group.iloc[-1], group.iloc[0]
        row = dict(inspected=date, file_year=int(last.file_year))
        for component in ("deck", "superstructure", "substructure"):
            row[component] = int(last[component])
            row[component+"_as_first_published"] = int(first[component])
        rows.append(row)
    return pd.DataFrame(rows)


def verify_inputs(data):
    manifest = json.loads((data/"manifest.json").read_text())
    for name, expected in manifest["files"].items():
        if hashlib.sha256((data/name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Input checksum mismatch: {name}")


def run(data, output, make_figure=True):
    verify_inputs(data)
    events = pd.read_csv(data/"events.csv")
    features = pd.read_csv(data/"response_features.csv")
    tracking = pd.read_csv(data/"mode_tracking.csv")
    config = json.loads((data/"predictor_config.json").read_text())
    if len(events) != 22 or events.event.duplicated().any():
        raise ValueError("Expected 22 unique events")
    if set(events.event) != set(features.event) or set(tracking.event) != set(events.event):
        raise ValueError("Event identifiers do not match across input tables")
    if set(features.loc[features.reference, "event"]) != set(config["reference_events"]):
        raise ValueError("Reference membership does not match the frozen configuration")
    nframe, ns = novelty(features)
    model, residuals, a_ref = amplitude(tracking)
    ef, cp, cs = changepoints(residuals, events)
    ins = inspection_history(pd.read_csv(data/"inspection_by_file.csv"))
    expected = json.loads((data/"reference_results.json").read_text())
    np.testing.assert_allclose(ns["mean"], expected["novelty"]["mean"], rtol=1e-9, atol=1e-11)
    np.testing.assert_allclose(ns["cov"], expected["novelty"]["cov"], rtol=1e-9, atol=1e-11)
    assert (ns["n_reference"], ns["n_test"], ns["n_novel_test"]) == (8, 14, 12)
    assert sorted(nframe.loc[nframe.novel & ~nframe.reference, "event"]) == sorted(expected["novelty"]["novel_events"])
    old = pd.DataFrame(expected["amplitude_model"]).set_index(["direction", "mode"]).sort_index()
    new = model.set_index(["direction", "mode"]).sort_index()
    for column in ("a", "beta", "a_sd", "beta_sd", "discrepancy_sd", "resid_sd"):
        np.testing.assert_allclose(new[column], old[column].astype(float), rtol=1e-8, atol=1e-10)
    for key in ("max_abs_z", "event_variance_component_pct", "sidak_z_crit_fwer05"):
        np.testing.assert_allclose(cs[key], expected["changepoint"][key], rtol=1e-8, atol=1e-10)
    assert cs["n_supported_fwer"] == expected["changepoint"]["n_supported_fwer"] == 0
    old_ins = pd.read_csv(data/"inspection.csv")
    assert ins.inspected.tolist() == old_ins.inspected.tolist()
    for column in ("deck", "superstructure", "substructure"):
        np.testing.assert_array_equal(ins[column], old_ins[column])
        np.testing.assert_array_equal(ins[column+"_as_first_published"], old_ins[column+"_as_first_published"])
    sensitivity = []
    for idx in features.index[features.reference]:
        trial = features.copy()
        trial.loc[idx, "reference"] = False
        assessed, _ = novelty(trial)
        sensitivity.append(dict(omitted_reference=features.loc[idx, "event"],
                                n_original_test_flagged=int(assessed.loc[~features.reference, "novel"].sum())))
    v1 = model[(model.direction == "vertical") & (model["mode"] == "V1")].iloc[0]
    modal = tracking[(tracking.direction == "vertical") & (tracking["mode"] == "V1")].merge(
        nframe[["event", "reference", "novel"]], on="event", validate="one_to_one")
    modal["frequency_change_pct"] = 100*(modal.freq_ratio-1)
    a = np.geomspace(events.pga_input_g.min(), events.pga_input_g.max(), 150)
    log_a = np.log(a/a_ref)
    prediction = v1.a - v1.beta*log_a
    sd = np.sqrt(np.maximum(v1.a_sd**2 + log_a**2*v1.beta_sd**2 - 2*log_a*v1.a_beta_cov, 0))
    curve = pd.DataFrame(dict(pga_input_g=a, change_pct=100*np.expm1(prediction),
                              lower_pct=100*np.expm1(prediction-1.96*sd),
                              upper_pct=100*np.expm1(prediction+1.96*sd)))
    summary = dict(novelty=ns, changepoint=cs,
                   frequency_decline_pct=float(100*np.expm1(-v1.beta*np.log(v1.amp_range_factor))),
                   reference_frequency_hz=float(v1.reference_freq_hz),
                   verification="Passed comparisons with original saved analysis outputs",
                   uncertainty_note="Coefficient covariance included in figure band; conditional approximate intervals, not damage probabilities.")
    output.mkdir(parents=True, exist_ok=True)
    for name, frame in [("novelty", nframe), ("amplitude_model", model), ("amplitude_residuals", residuals),
                        ("event_residuals", ef), ("changepoints", cp), ("inspection", ins),
                        ("reference_sensitivity", pd.DataFrame(sensitivity)),
                        ("frequency_panel", modal), ("frequency_curve", curve)]:
        frame.to_csv(output/f"{name}.csv", index=False)
    (output/"summary.json").write_text(json.dumps(summary, indent=2)+"\n")
    if make_figure:
        from plot import draw
        draw(output, output.parent/"figures")
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT/"data")
    parser.add_argument("--output", type=Path, default=ROOT/"results")
    parser.add_argument("--no-figure", action="store_true")
    args = parser.parse_args()
    run(args.data, args.output, not args.no_figure)
