"""Regression tests for committed v6 BLAGN science products."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import v4_science, v5_science
from src.v6_catalogue import THRILS_SOURCE_KEY
from src.v6_science import EPSILON, MERGER_BOOST, Z_SEED, evaluate_catalogue, prepare_catalogue_view


class V6ScienceTests(unittest.TestCase):
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
            "measurement_history": "measurement_accretion_history",
            "object_history": "physical_object_accretion_history",
            "ranking_comparison": "primary_ranking_comparison",
        }
        cls.frames = {
            name: pd.read_csv(ROOT / "results" / f"v6_blagn_{stem}.csv")
            for name, stem in stems.items()
        }

    def test_counts_release_and_rank_integrity(self) -> None:
        expected = {
            "measurement_eval": 494, "object_eval": 469, "measurement_point": 112,
            "object_point": 105, "measurement_fedd": 1482, "measurement_mseed": 988,
            "object_fedd": 1407, "object_mseed": 938,
            "measurement_uncertainty": 112, "object_uncertainty": 105,
            "alternate_sensitivity": 7, "measurement_history": 336,
            "object_history": 315, "ranking_comparison": 105,
        }
        for name, count in expected.items():
            self.assertEqual(len(self.frames[name]), count, name)
        for frame in self.frames.values():
            self.assertTrue(frame["catalogue_release"].eq("v6-blagn").all())
        for name, column in [
            ("measurement_point", "rank_growth_pressure"),
            ("object_point", "rank_growth_pressure"),
            ("measurement_uncertainty", "rank_uncertainty_pressure"),
            ("object_uncertainty", "rank_uncertainty_pressure"),
        ]:
            self.assertEqual(sorted(self.frames[name][column].astype(int)), list(range(1, len(self.frames[name]) + 1)))

    def test_baseline_math_and_thrils_systematic_policy(self) -> None:
        evaluation = self.frames["measurement_eval"]
        self.assertTrue(evaluation["z_seed"].eq(Z_SEED).all())
        self.assertTrue(evaluation["epsilon"].eq(EPSILON).all())
        self.assertTrue(evaluation["merger_boost"].eq(MERGER_BOOST).all())
        thrils = evaluation[evaluation["source_key"].eq(THRILS_SOURCE_KEY)]
        self.assertEqual(set(thrils["scenario"]), {
            "baseline", "mbh_minus_0p3dex", "mbh_plus_0p3dex",
            "thrils_virial_minus_0p5dex", "thrils_virial_plus_0p5dex",
        })
        self.assertEqual(len(thrils), 30)
        self.assertFalse(thrils["systematic_combined_with_statistical_error"].astype(bool).any())

    def test_statistical_errors_and_missing_diagnostics(self) -> None:
        fedd = self.frames["measurement_fedd"]
        self.assertTrue(fedd["required_fedd_p16"].le(fedd["required_fedd_p50"]).all())
        self.assertTrue(fedd["required_fedd_p50"].le(fedd["required_fedd_p84"]).all())
        point = self.frames["measurement_point"]
        thrils = point[point["source_key"].eq(THRILS_SOURCE_KEY)]
        self.assertFalse(thrils["missing_diagnostics_penalized_flag"].astype(bool).any())
        self.assertTrue(thrils["mstar_diagnostic_status"].str.startswith("unavailable").all())
        self.assertTrue(thrils["lbol_diagnostic_status"].str.startswith("unavailable").all())

    def test_v5_rows_remain_numerically_preserved(self) -> None:
        v6 = self.frames["measurement_point"].set_index("measurement_id")
        v5 = pd.read_csv(ROOT / "results/v5_blagn_measurement_point_ranking.csv").set_index("measurement_id")
        for column in ["req_fedd_seed1e2_z30_eps0p1_b1", "req_log_mseed_fedd0p3_z30_eps0p1_b1"]:
            np.testing.assert_allclose(v6.loc[v5.index, column], v5[column], rtol=0, atol=1e-12)

    def test_source_extension_does_not_mutate_v5_configuration(self) -> None:
        release = v5_science.CATALOGUE_RELEASE
        scenarios = v4_science.SOURCE_SCENARIOS
        measurements = prepare_catalogue_view(
            pd.read_csv(ROOT / "data/processed/v6_blagn_measurements.csv"), view="measurement",
        )
        evaluate_catalogue(measurements)
        self.assertEqual(v5_science.CATALOGUE_RELEASE, release)
        self.assertIs(v4_science.SOURCE_SCENARIOS, scenarios)

    def test_summary_names_thrils_and_preserves_unreported_lrd(self) -> None:
        overall = self.frames["catalogue_summary"]
        overall = overall[overall["stratum_type"].eq("overall")]
        self.assertTrue(overall["selection_function_note"].str.contains("THRILS", regex=False).all())
        object_summary = overall[overall["catalogue_view"].eq("physical_object")].iloc[0]
        self.assertEqual(
            int(object_summary["n_lrd"] + object_summary["n_non_lrd"] + object_summary["n_lrd_not_reported"]),
            int(object_summary["n_rows"]),
        )


if __name__ == "__main__":
    unittest.main()
