"""Regression tests for committed v4 science products."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.v4_catalogue import ASPIRE_SOURCE_KEY, MATTHEE_SOURCE_KEY
from src.v4_science import EPSILON, MERGER_BOOST, Z_SEED


class V4ScienceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        names = {
            "measurement_eval": "v4_blagn_measurement_evaluation.csv", "object_eval": "v4_blagn_physical_object_evaluation.csv",
            "measurement_point": "v4_blagn_measurement_point_ranking.csv", "object_point": "v4_blagn_physical_object_point_ranking.csv",
            "measurement_fedd": "v4_blagn_measurement_uncertainty_fedd.csv", "measurement_mseed": "v4_blagn_measurement_uncertainty_mseed.csv",
            "object_fedd": "v4_blagn_physical_object_uncertainty_fedd.csv", "object_mseed": "v4_blagn_physical_object_uncertainty_mseed.csv",
            "measurement_uncertainty": "v4_blagn_measurement_uncertainty_ranking.csv", "object_uncertainty": "v4_blagn_physical_object_uncertainty_ranking.csv",
            "catalogue_summary": "v4_blagn_catalogue_summary.csv", "growth_summary": "v4_blagn_growth_summary.csv",
            "alternate_sensitivity": "v4_blagn_alternate_measurement_sensitivity.csv",
        }
        tables = ROOT / "results/releases/v4/tables"
        cls.frames = {name: pd.read_csv(tables / file) for name, file in names.items()}

    def test_counts_release_and_unique_ranks(self) -> None:
        expected = {"measurement_eval": 434, "object_eval": 424, "measurement_point": 96, "object_point": 94, "measurement_fedd": 1302, "measurement_mseed": 868, "object_fedd": 1272, "object_mseed": 848, "measurement_uncertainty": 96, "object_uncertainty": 94}
        for name, count in expected.items():
            self.assertEqual(len(self.frames[name]), count, name)
        for frame in self.frames.values():
            self.assertTrue(frame["catalogue_release"].eq("v4-blagn").all())
        self.assertEqual(sorted(self.frames["object_uncertainty"]["rank_uncertainty_pressure"]), list(range(1, 95)))

    def test_baseline_assumptions_and_separate_systematics(self) -> None:
        evaluation = self.frames["measurement_eval"]
        self.assertTrue(evaluation["z_seed"].eq(Z_SEED).all())
        self.assertTrue(evaluation["epsilon"].eq(EPSILON).all())
        self.assertTrue(evaluation["merger_boost"].eq(MERGER_BOOST).all())
        for source, prefix, count in [(MATTHEE_SOURCE_KEY, "matthee_virial_", 40), (ASPIRE_SOURCE_KEY, "aspire_virial_", 32)]:
            rows = evaluation[evaluation["scenario"].str.startswith(prefix)]
            self.assertEqual(len(rows), count)
            self.assertTrue(rows["source_key"].eq(source).all())
            self.assertEqual(set(rows["mbh_delta_dex"]), {-0.5, 0.5})
            self.assertFalse(rows["systematic_combined_with_statistical_error"].astype(bool).any())

    def test_uncertainty_ordering_and_sample_count(self) -> None:
        fedd = self.frames["measurement_fedd"]
        self.assertTrue(fedd["n_samples"].eq(10000).all())
        self.assertTrue(fedd["required_fedd_p16"].le(fedd["required_fedd_p50"]).all())
        self.assertTrue(fedd["required_fedd_p50"].le(fedd["required_fedd_p84"]).all())
        pivot = fedd[fedd["seed_mass_short"].eq("seed1e2")].pivot(index="measurement_id", columns="scenario", values="required_fedd_p50")
        for prefix, count in [("matthee", 20), ("aspire", 16)]:
            rows = pivot.dropna(subset=[f"{prefix}_virial_minus_0p5dex"])
            self.assertEqual(len(rows), count)
            self.assertTrue((rows[f"{prefix}_virial_minus_0p5dex"] < rows["baseline"]).all())
            self.assertTrue((rows["baseline"] < rows[f"{prefix}_virial_plus_0p5dex"]).all())

    def test_missing_diagnostics_are_not_penalties(self) -> None:
        point = self.frames["measurement_point"]
        new = point[point["source_key"].isin([MATTHEE_SOURCE_KEY, ASPIRE_SOURCE_KEY])]
        self.assertFalse(new["missing_diagnostics_penalized_flag"].astype(bool).any())
        self.assertTrue(new["mstar_diagnostic_status"].str.startswith("unavailable").all())
        self.assertTrue(new["edd_ratio_diagnostic_status"].str.startswith("unavailable").all())
        self.assertTrue(new["lbol_diagnostic_status"].eq("available").all())

    def test_detection_and_mass_reliability_are_separate(self) -> None:
        point = self.frames["measurement_point"].set_index("object_id")
        absorption = point.loc["GOODS-N-9771"]
        self.assertEqual(absorption["detection_confidence_tier"], "high")
        self.assertEqual(absorption["mass_measurement_reliability_tier"], "robust_with_measurement_caveat")
        self.assertEqual(absorption["followup_priority_category"], "B_caveated_high_pressure")
        contaminated = point.loc["GOODS-S-13971"]
        self.assertEqual(contaminated["mass_measurement_reliability_tier"], "robust_with_measurement_caveat")
        alternative = point.loc["RUBIES-EGS-49140"]
        self.assertEqual(alternative["mass_measurement_reliability_tier"], "robust_with_interpretive_caveat")

    def test_object_view_deduplicates_both_known_pairs(self) -> None:
        measurement = self.frames["measurement_point"]
        objects = self.frames["object_point"]
        for physical_id in ["HZA-CEERS-2782", "HZA-GS-204851"]:
            self.assertEqual(len(measurement[measurement["physical_object_id"].eq(physical_id)]), 2)
            self.assertEqual(len(objects[objects["physical_object_id"].eq(physical_id)]), 1)

    def test_v3_baseline_rows_are_numerically_preserved(self) -> None:
        v4 = self.frames["measurement_point"].set_index("measurement_id")
        v3 = pd.read_csv(ROOT / "results/releases/v3/tables/v3_blagn_measurement_point_ranking.csv").set_index("measurement_id")
        for column in ["req_fedd_seed1e2_z30_eps0p1_b1", "req_log_mseed_fedd0p3_z30_eps0p1_b1"]:
            np.testing.assert_allclose(v4.loc[v3.index, column], v3[column], rtol=0, atol=1e-12)

    def test_summary_is_stratified_and_non_demographic(self) -> None:
        summary = self.frames["catalogue_summary"]
        overall = summary[(summary["catalogue_view"].eq("measurement")) & summary["stratum_type"].eq("overall")].iloc[0]
        self.assertEqual(int(overall["n_rows"]), 96)
        self.assertEqual(int(overall["n_physical_objects"]), 94)
        self.assertFalse(bool(overall["demographic_inference_allowed"]))
        self.assertIn("EIGER/FRESCO", overall["selection_function_note"])
        self.assertTrue({"source", "survey", "field", "lrd_phenotype"}.issubset(set(summary["stratum_type"])))
        jades_objects = summary[
            summary["catalogue_view"].eq("physical_object")
            & summary["stratum_type"].eq("source")
            & summary["stratum_value"].eq("juodzbalis25_jades_blagn")
        ].iloc[0]
        self.assertEqual(int(jades_objects["n_lrd"]), 0)
        self.assertEqual(int(jades_objects["n_lrd_any_measurement"]), 1)
        self.assertEqual(int(jades_objects["n_lrd_cross_source_only"]), 1)

    def test_both_duplicate_objects_have_alternate_measurement_sensitivity(self) -> None:
        sensitivity = self.frames["alternate_sensitivity"]
        self.assertEqual(len(sensitivity), 2)
        self.assertEqual(set(sensitivity["physical_object_id"]), {"HZA-CEERS-2782", "HZA-GS-204851"})
        self.assertTrue(sensitivity["n_samples"].eq(10000).all())
        self.assertEqual(set(sensitivity["comparison_scope"]), {"one_object_substitution"})


if __name__ == "__main__":
    unittest.main()
