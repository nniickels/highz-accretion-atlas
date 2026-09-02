"""Core numerical and canonical-result regression tests."""

from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from src import models
from src.scoring import aggregate_feasibility_score, score_required_fedd, score_required_seed_mass


ROOT = Path(__file__).resolve().parents[1]


class GrowthModelTests(unittest.TestCase):
    def test_growth_round_trip(self) -> None:
        predicted = models.predicted_log_mbh(4.0, 0.7, 0.1, 30.0, 7.0, merger_boost=2.0)
        recovered_fedd = models.required_fedd_for_seed(
            4.0, predicted, 0.1, 30.0, 7.0, merger_boost=2.0,
        )
        recovered_seed = models.required_seed_mass_for_growth(
            predicted, 0.7, 0.1, 30.0, 7.0, merger_boost=2.0,
        )
        self.assertAlmostEqual(float(recovered_fedd), 0.7, places=12)
        self.assertAlmostEqual(float(recovered_seed), 4.0, places=12)

    def test_invalid_inputs_raise(self) -> None:
        with self.assertRaises(ValueError):
            models.cosmic_time_gyr(-1.0)
        with self.assertRaises(ValueError):
            models.available_growth_time_gyr(z_seed=6.0, z_obs=7.0)
        with self.assertRaises(ValueError):
            models.growth_log10_factor(f_edd=-0.1, epsilon=0.1, delta_t_gyr=0.5)

    def test_two_state_duty_cycle(self) -> None:
        self.assertAlmostEqual(float(models.two_state_average_fedd(0.25, 2.0)), 0.5)
        np.testing.assert_allclose(models.required_duty_cycle([0.5, 2.5], 2.0), [0.25, 1.25])

    def test_sanity_check_anchors(self) -> None:
        checks = models.run_growth_sanity_checks()
        self.assertAlmostEqual(checks["roundtrip_required_fedd"], 1.0, places=12)
        self.assertAlmostEqual(checks["roundtrip_required_log_mseed"], 5.0, places=12)
        self.assertAlmostEqual(checks["merger_boost_x2_dex"], np.log10(2.0), places=12)


class ScoringTests(unittest.TestCase):
    def test_feasibility_scores(self) -> None:
        self.assertEqual(score_required_seed_mass(5.0, 4.0, 6.0), 1.0)
        self.assertEqual(score_required_seed_mass(3.0, 4.0, 6.0), 0.0)
        self.assertEqual(score_required_fedd(0.5), 1.0)
        self.assertEqual(score_required_fedd(3.5), 0.0)
        self.assertAlmostEqual(aggregate_feasibility_score(1.0, 0.5), 0.8)


class CanonicalResultTests(unittest.TestCase):
    def test_v1_regression_anchors(self) -> None:
        objects = pd.read_csv(ROOT / "data/processed/v1/v1_accreting_objects.csv")
        self.assertEqual(len(objects), 23)
        self.assertEqual(objects["quality_flag"].value_counts().to_dict(), {"robust": 18, "tentative": 5})
        inconsistent = objects[objects["edd_ratio_consistency_flag"].eq("inconsistent")]
        self.assertEqual(inconsistent["object_id"].tolist(), ["GN-11836"])

    def test_v1_pressure_ranking_anchor(self) -> None:
        ranking = pd.read_csv(ROOT / "results/v1/tables/v1_object_point_ranking.csv")
        top = set(ranking.nsmallest(6, "rank_global_navigation")["object_id"])
        expected = {"GS-20057765", "GS-20030333", "GS-164055", "GN-38509", "GN-4685", "GN-954"}
        self.assertEqual(top, expected)

    def test_v1_required_seed_anchor(self) -> None:
        required = pd.read_csv(ROOT / "results/v1/tables/v1_required_mseed_by_growth_assumption.csv")
        gentle = required[required["fedd_assumption"].eq("0p3")]
        top = gentle.nlargest(1, "required_log_mseed").iloc[0]
        self.assertEqual(top["object_id"], "GN-38509")
        self.assertAlmostEqual(top["required_log_mseed"], 6.718503, places=6)


if __name__ == "__main__":
    unittest.main()
