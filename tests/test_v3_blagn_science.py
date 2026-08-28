"""Regression checks for the v3 BLAGN science workflow."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.v3_catalogue import TAYLOR_SOURCE_KEY
from src.v3_science import EPSILON, MERGER_BOOST, Z_SEED


RESULTS = REPO_ROOT / "results/past_releases/v3/tables"
V2_TABLES = REPO_ROOT / "results/past_releases/v2/tables"


class V3ScienceOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        names = {
            "measurement_eval": "v3_blagn_measurement_evaluation.csv",
            "object_eval": "v3_blagn_physical_object_evaluation.csv",
            "measurement_point": "v3_blagn_measurement_point_ranking.csv",
            "object_point": "v3_blagn_physical_object_point_ranking.csv",
            "measurement_fedd": "v3_blagn_measurement_uncertainty_fedd.csv",
            "measurement_mseed": "v3_blagn_measurement_uncertainty_mseed.csv",
            "object_fedd": "v3_blagn_physical_object_uncertainty_fedd.csv",
            "object_mseed": "v3_blagn_physical_object_uncertainty_mseed.csv",
            "measurement_uncertainty": "v3_blagn_measurement_uncertainty_ranking.csv",
            "object_uncertainty": "v3_blagn_physical_object_uncertainty_ranking.csv",
            "catalogue_summary": "v3_blagn_catalogue_summary.csv",
            "growth_summary": "v3_blagn_growth_summary.csv",
        }
        cls.frames = {key: pd.read_csv(RESULTS / value) for key, value in names.items()}

    def test_output_counts_and_unique_ranking_ids(self) -> None:
        expected = {
            "measurement_eval": 254,
            "object_eval": 249,
            "measurement_point": 60,
            "object_point": 59,
            "measurement_fedd": 762,
            "measurement_mseed": 508,
            "object_fedd": 747,
            "object_mseed": 498,
            "measurement_uncertainty": 60,
            "object_uncertainty": 59,
        }
        for name, count in expected.items():
            self.assertEqual(len(self.frames[name]), count, name)
        self.assertTrue(self.frames["measurement_point"]["measurement_id"].is_unique)
        self.assertTrue(self.frames["object_point"]["physical_object_id"].is_unique)

    def test_all_v3_products_identify_the_release(self) -> None:
        for name, frame in self.frames.items():
            self.assertIn("catalogue_release", frame.columns, name)
            self.assertTrue(frame["catalogue_release"].eq("v3-blagn").all(), name)

    def test_physical_object_view_deduplicates_but_preserves_measurements(self) -> None:
        measurement = self.frames["measurement_point"]
        objects = self.frames["object_point"]
        duplicate_measurements = measurement[
            measurement["physical_object_id"].eq("HZA-CEERS-2782")
        ]
        self.assertEqual(len(duplicate_measurements), 2)
        physical = objects[objects["physical_object_id"].eq("HZA-CEERS-2782")]
        self.assertEqual(len(physical), 1)
        self.assertEqual(physical.iloc[0]["measurement_id"], "RUBIESEGS50052_taylor24")
        self.assertEqual(int(physical.iloc[0]["n_measurements"]), 2)
        self.assertIn("higher-S/N", physical.iloc[0]["preferred_measurement_reason"])

    def test_rank_columns_are_complete_permutations(self) -> None:
        for name, column in [
            ("measurement_point", "rank_growth_pressure"),
            ("object_point", "rank_growth_pressure"),
            ("measurement_point", "rank_followup_priority"),
            ("object_point", "rank_followup_priority"),
            ("measurement_uncertainty", "rank_uncertainty_pressure"),
            ("object_uncertainty", "rank_uncertainty_pressure"),
        ]:
            values = sorted(self.frames[name][column].astype(int).tolist())
            self.assertEqual(values, list(range(1, len(values) + 1)), f"{name}:{column}")

    def test_baseline_assumptions_and_scenario_scope(self) -> None:
        for name in ["measurement_eval", "object_eval", "measurement_fedd", "object_fedd"]:
            frame = self.frames[name]
            self.assertTrue(frame["z_seed"].eq(Z_SEED).all())
            self.assertTrue(frame["epsilon"].eq(EPSILON).all())
            self.assertTrue(frame["merger_boost"].eq(MERGER_BOOST).all())

        evaluation = self.frames["measurement_eval"]
        taylor_sensitivity = evaluation[
            evaluation["scenario"].str.startswith("taylor_virial_")
        ]
        self.assertEqual(len(taylor_sensitivity), 74)
        self.assertTrue(taylor_sensitivity["source_key"].eq(TAYLOR_SOURCE_KEY).all())
        self.assertEqual(set(taylor_sensitivity["mbh_delta_dex"]), {-0.5, 0.5})
        non_taylor = evaluation[~evaluation["source_key"].eq(TAYLOR_SOURCE_KEY)]
        self.assertFalse(non_taylor["scenario"].str.startswith("taylor_virial_").any())

    def test_v1_baseline_growth_metrics_are_preserved(self) -> None:
        expanded = self.frames["measurement_point"]
        expanded = expanded[expanded["source_key"].eq("juodzbalis25_jades_blagn")].set_index(
            "measurement_id"
        )
        v1 = pd.read_csv(V2_TABLES / "v2_object_ranking_table.csv").set_index("measurement_id")
        columns = [
            "req_fedd_seed1e2_z30_eps0p1_b1",
            "req_fedd_seed1e4_z30_eps0p1_b1",
            "req_fedd_seed1e5_z30_eps0p1_b1",
            "req_log_mseed_fedd0p3_z30_eps0p1_b1",
            "req_log_mseed_fedd1_z30_eps0p1_b1",
        ]
        self.assertEqual(set(expanded.index), set(v1.index))
        for column in columns:
            np.testing.assert_allclose(expanded.loc[v1.index, column], v1[column], rtol=0, atol=1e-12)

    def test_missing_taylor_diagnostics_are_unavailable_not_penalties(self) -> None:
        taylor = self.frames["measurement_point"]
        taylor = taylor[taylor["source_key"].eq(TAYLOR_SOURCE_KEY)]
        self.assertFalse(taylor["missing_diagnostics_penalized_flag"].astype(bool).any())
        for column in [
            "mstar_diagnostic_status",
            "lbol_diagnostic_status",
            "edd_ratio_diagnostic_status",
        ]:
            self.assertTrue(taylor[column].str.startswith("unavailable_not_published").all())
        uncaveated = taylor[taylor["source_caveat_tags"].eq(
            "formal_mbh_errors_exclude_virial_systematic;nominal_mass_uncorrected_for_dust"
        )]
        self.assertTrue(uncaveated["measurement_confidence_tier"].eq("high").all())
        self.assertTrue(uncaveated["measurement_confidence_score_0_100"].eq(90).all())

    def test_statistical_and_systematic_uncertainties_remain_separate(self) -> None:
        for name in ["measurement_fedd", "measurement_mseed", "object_fedd", "object_mseed"]:
            frame = self.frames[name]
            self.assertTrue(frame["reported_statistical_errors_sampled"].astype(bool).all())
            self.assertFalse(frame["systematic_combined_with_statistical_error"].astype(bool).any())
            self.assertTrue(frame["n_samples"].eq(10000).all())
            self.assertTrue(frame["random_seed"].eq(20260808).all())

    def test_uncertainty_percentiles_and_systematic_ordering(self) -> None:
        for name, prefix in [
            ("measurement_fedd", "required_fedd"),
            ("measurement_mseed", "required_log_mseed"),
        ]:
            frame = self.frames[name]
            self.assertTrue(frame[f"{prefix}_p5"].le(frame[f"{prefix}_p16"]).all())
            self.assertTrue(frame[f"{prefix}_p16"].le(frame[f"{prefix}_p50"]).all())
            self.assertTrue(frame[f"{prefix}_p50"].le(frame[f"{prefix}_p84"]).all())
            self.assertTrue(frame[f"{prefix}_p84"].le(frame[f"{prefix}_p95"]).all())

        fedd = self.frames["measurement_fedd"]
        fedd = fedd[fedd["seed_mass_short"].eq("seed1e2")]
        pivot = fedd.pivot(index="measurement_id", columns="scenario", values="required_fedd_p50")
        self.assertTrue((pivot["mbh_minus_0p3dex"] < pivot["baseline"]).all())
        self.assertTrue((pivot["baseline"] < pivot["mbh_plus_0p3dex"]).all())
        taylor = pivot.dropna(subset=["taylor_virial_minus_0p5dex"])
        self.assertEqual(len(taylor), 37)
        self.assertTrue((taylor["taylor_virial_minus_0p5dex"] < taylor["mbh_minus_0p3dex"]).all())
        self.assertTrue((taylor["mbh_plus_0p3dex"] < taylor["taylor_virial_plus_0p5dex"]).all())

        mseed = self.frames["measurement_mseed"]
        mseed = mseed[mseed["growth_history"].eq("fedd0p3")]
        mseed_pivot = mseed.pivot(
            index="measurement_id", columns="scenario", values="required_log_mseed_p50"
        )
        self.assertTrue((mseed_pivot["mbh_minus_0p3dex"] < mseed_pivot["baseline"]).all())
        self.assertTrue((mseed_pivot["baseline"] < mseed_pivot["mbh_plus_0p3dex"]).all())
        taylor_mseed = mseed_pivot.dropna(subset=["taylor_virial_minus_0p5dex"])
        self.assertTrue(
            (taylor_mseed["taylor_virial_minus_0p5dex"] < taylor_mseed["mbh_minus_0p3dex"]).all()
        )
        self.assertTrue(
            (taylor_mseed["mbh_plus_0p3dex"] < taylor_mseed["taylor_virial_plus_0p5dex"]).all()
        )

    def test_common_measurement_has_identical_draws_across_views(self) -> None:
        measurement = self.frames["measurement_fedd"]
        measurement = measurement[
            measurement["measurement_id"].eq("RUBIESEGS50052_taylor24")
            & measurement["scenario"].eq("baseline")
            & measurement["seed_mass_short"].eq("seed1e2")
        ].iloc[0]
        physical = self.frames["object_fedd"]
        physical = physical[
            physical["physical_object_id"].eq("HZA-CEERS-2782")
            & physical["scenario"].eq("baseline")
            & physical["seed_mass_short"].eq("seed1e2")
        ].iloc[0]
        for column in ["log_mbh_sample_p16", "log_mbh_sample_p50", "required_fedd_p84"]:
            self.assertEqual(measurement[column], physical[column])

    def test_source_provenance_and_stratified_summary(self) -> None:
        taylor = self.frames["measurement_point"]
        taylor = taylor[taylor["source_key"].eq(TAYLOR_SOURCE_KEY)]
        self.assertTrue(taylor["source_table"].eq("Table 1 (Sample of BLAGN)").all())
        self.assertTrue(taylor["source_doi"].eq("10.3847/1538-4357/add15b").all())

        summary = self.frames["catalogue_summary"]
        measurement_overall = summary[
            summary["catalogue_view"].eq("measurement")
            & summary["stratum_type"].eq("overall")
        ].iloc[0]
        object_overall = summary[
            summary["catalogue_view"].eq("physical_object")
            & summary["stratum_type"].eq("overall")
        ].iloc[0]
        self.assertEqual(int(measurement_overall["n_rows"]), 60)
        self.assertEqual(int(measurement_overall["n_physical_objects"]), 59)
        self.assertEqual(int(object_overall["n_rows"]), 59)
        self.assertEqual(int(object_overall["n_measurements_represented"]), 60)
        self.assertFalse(bool(measurement_overall["demographic_inference_allowed"]))
        self.assertIn("mixes JADES and CEERS/RUBIES", measurement_overall["selection_function_note"])
        self.assertTrue(
            {"source", "survey", "field", "survey_field", "lrd_phenotype"}.issubset(
                set(summary["stratum_type"])
            )
        )

    def test_top_rank_regression_and_cautious_caveat(self) -> None:
        point = self.frames["object_point"].nsmallest(3, "rank_growth_pressure")
        uncertainty = self.frames["object_uncertainty"].nsmallest(3, "rank_uncertainty_pressure")
        expected = ["GN-38509", "GS-20057765", "RUBIES-EGS-49140"]
        self.assertEqual(point["object_id"].tolist(), expected)
        self.assertEqual(uncertainty["object_id"].tolist(), expected)
        egs49140 = point[point["object_id"].eq("RUBIES-EGS-49140")].iloc[0]
        self.assertEqual(egs49140["measurement_confidence_tier"], "robust_with_interpretive_caveat")
        self.assertEqual(egs49140["followup_priority_category"], "B_caveated_high_pressure")
        self.assertIn("not evidence for a unique seed channel", egs49140["ranking_note"])


if __name__ == "__main__":
    unittest.main()
