"""Regression tests for committed v5 BLAGN science products."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.v5_catalogue import HARIKANE_SOURCE_KEY
from src.v5_science import EPSILON, MERGER_BOOST, Z_SEED


class V5ScienceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        stems = {
            "measurement_eval": "measurement_evaluation", "object_eval": "physical_object_evaluation",
            "measurement_point": "measurement_point_ranking", "object_point": "physical_object_point_ranking",
            "measurement_fedd": "measurement_uncertainty_fedd", "measurement_mseed": "measurement_uncertainty_mseed",
            "object_fedd": "physical_object_uncertainty_fedd", "object_mseed": "physical_object_uncertainty_mseed",
            "measurement_uncertainty": "measurement_uncertainty_ranking", "object_uncertainty": "physical_object_uncertainty_ranking",
            "catalogue_summary": "catalogue_summary", "growth_summary": "growth_summary",
            "alternate_sensitivity": "alternate_measurement_sensitivity",
        }
        cls.frames = {
            name: pd.read_csv(ROOT / "results" / f"v5_blagn_{stem}.csv")
            for name, stem in stems.items()
        }

    def test_counts_release_and_ranks(self) -> None:
        expected = {
            "measurement_eval": 464, "object_eval": 439, "measurement_point": 106,
            "object_point": 99, "measurement_fedd": 1392, "measurement_mseed": 928,
            "object_fedd": 1317, "object_mseed": 878,
            "measurement_uncertainty": 106, "object_uncertainty": 99,
            "alternate_sensitivity": 7,
        }
        for name, count in expected.items():
            self.assertEqual(len(self.frames[name]), count, name)
        for frame in self.frames.values():
            self.assertTrue(frame["catalogue_release"].eq("v5-blagn").all())
        self.assertEqual(sorted(self.frames["object_point"]["rank_growth_pressure"]), list(range(1, 100)))

    def test_baseline_math_and_harikane_scenario_policy(self) -> None:
        evaluation = self.frames["measurement_eval"]
        self.assertTrue(evaluation["z_seed"].eq(Z_SEED).all())
        self.assertTrue(evaluation["epsilon"].eq(EPSILON).all())
        self.assertTrue(evaluation["merger_boost"].eq(MERGER_BOOST).all())
        harikane = evaluation[evaluation["source_key"].eq(HARIKANE_SOURCE_KEY)]
        self.assertEqual(set(harikane["scenario"]), {"baseline", "mbh_minus_0p3dex", "mbh_plus_0p3dex"})
        self.assertEqual(len(harikane), 30)
        self.assertFalse(harikane["systematic_combined_with_statistical_error"].astype(bool).any())

    def test_statistical_uncertainty_ordering(self) -> None:
        fedd = self.frames["measurement_fedd"]
        self.assertTrue(fedd["n_samples"].eq(10000).all())
        self.assertTrue(fedd["required_fedd_p16"].le(fedd["required_fedd_p50"]).all())
        self.assertTrue(fedd["required_fedd_p50"].le(fedd["required_fedd_p84"]).all())

    def test_harikane_missing_diagnostics_are_not_penalties(self) -> None:
        point = self.frames["measurement_point"]
        harikane = point[point["source_key"].eq(HARIKANE_SOURCE_KEY)]
        self.assertFalse(harikane["missing_diagnostics_penalized_flag"].astype(bool).any())
        missing_host = harikane[harikane["log_mstar_msun"].isna()]
        self.assertTrue(missing_host["mstar_diagnostic_status"].str.startswith("unavailable").all())
        self.assertTrue(harikane["lbol_diagnostic_status"].eq("available").all())

    def test_object_view_deduplicates_all_measurements(self) -> None:
        measurement = self.frames["measurement_point"]
        objects = self.frames["object_point"]
        triple = measurement[measurement["physical_object_id"].eq("HZA-CEERS-2782")]
        self.assertEqual(len(triple), 3)
        self.assertEqual(len(objects[objects["physical_object_id"].eq("HZA-CEERS-2782")]), 1)
        self.assertEqual(measurement["physical_object_id"].nunique(), len(objects))

    def test_v4_rows_remain_numerically_preserved(self) -> None:
        v5 = self.frames["measurement_point"].set_index("measurement_id")
        v4 = pd.read_csv(ROOT / "results/v4_blagn_measurement_point_ranking.csv").set_index("measurement_id")
        for column in ["req_fedd_seed1e2_z30_eps0p1_b1", "req_log_mseed_fedd0p3_z30_eps0p1_b1"]:
            np.testing.assert_allclose(v5.loc[v4.index, column], v4[column], rtol=0, atol=1e-12)

    def test_top_rank_change_is_auditable(self) -> None:
        point = self.frames["object_point"].set_index("physical_object_id")
        self.assertEqual(int(point.loc["HZA-CEERS-00717", "rank_growth_pressure"]), 4)
        uncertainty = self.frames["object_uncertainty"].set_index("physical_object_id")
        self.assertEqual(int(uncertainty.loc["HZA-CEERS-00717", "rank_uncertainty_pressure"]), 5)


if __name__ == "__main__":
    unittest.main()
