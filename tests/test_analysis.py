"""Regression and input-integrity checks for the distributed example."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis import ROOT, amplitude, inspection_history, novelty, run, verify_inputs


class AnalysisTests(unittest.TestCase):
    def test_reference_reproduction(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run(ROOT/"data", Path(tmp)/"results", make_figure=False)
        self.assertAlmostEqual(result["frequency_decline_pct"], -5.532573825151477, places=8)
        self.assertEqual(result["changepoint"]["n_supported_bonferroni"], 0)

    def test_rejects_nonpositive_feature(self):
        data = pd.read_csv(ROOT/"data/response_features.csv")
        data.loc[0, "CAV"] = 0
        with self.assertRaises(ValueError): novelty(data)

    def test_reference_model_is_row_order_invariant(self):
        data = pd.read_csv(ROOT/"data/response_features.csv")
        first, _ = novelty(data)
        second, _ = novelty(data.sample(frac=1, random_state=8))
        np.testing.assert_allclose(first.set_index("event").sort_index().MD2,
                                   second.set_index("event").sort_index().MD2)

    def test_singular_reference_is_rejected(self):
        data = pd.read_csv(ROOT/"data/response_features.csv")
        data.loc[data.reference, ["PRA", "CAV"]] = 1
        with self.assertRaises(ValueError): novelty(data)

    def test_inspection_revision_is_not_an_extra_visit(self):
        source = pd.read_csv(ROOT/"data/inspection_by_file.csv")
        result = inspection_history(source.sample(frac=1, random_state=7))
        visit = result[result.inspected.str.startswith("2021")].iloc[0]
        self.assertEqual(len(result), 7)
        self.assertEqual(visit.substructure, 6)
        self.assertEqual(visit.substructure_as_first_published, 7)

    def test_missing_predictor_spread_is_supported(self):
        source = pd.read_csv(ROOT/"data/mode_tracking.csv")
        self.assertTrue(source.freq_spread_hz.isna().any())
        model, residuals, _ = amplitude(source)
        self.assertEqual(len(model), 18)
        self.assertTrue(np.isfinite(residuals.sigma_total).all())

    def test_checksum_detects_changed_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target/"input.csv").write_text("altered")
            (target/"manifest.json").write_text(json.dumps({"files":{"input.csv":"0"*64}}))
            with self.assertRaises(ValueError): verify_inputs(target)

    def test_input_pga_and_reference_selection_match_channel_inventory(self):
        events = pd.read_csv(ROOT/"data/events.csv").set_index("event")
        channels = pd.read_csv(ROOT/"data/channel_inventory.csv")
        config = json.loads((ROOT/"data/predictor_config.json").read_text())
        inputs = [c for d in config["direction_channels"].values() for c in d["input"]]
        outputs = [c for d in config["direction_channels"].values() for c in d["output"]]
        for role, numbers in [("input", inputs), ("structure", outputs)]:
            peak = channels[channels.channel.isin(numbers)].groupby("event").pga_g.max()
            np.testing.assert_allclose(peak.sort_index(), events[f"pga_{role}_g"].sort_index())
        weakest = set(events.sort_values("pga_structure_g").head(8).index)
        self.assertEqual(weakest, set(config["reference_events"]))

    def test_horizontal_feature_aggregation(self):
        frame = pd.read_csv(ROOT/"data/response_features.csv")
        for feature in ["PRA", "CAV"]:
            np.testing.assert_allclose(frame[feature], frame[[feature+"_T", feature+"_L"]].mean(axis=1))


if __name__ == "__main__":
    unittest.main()
