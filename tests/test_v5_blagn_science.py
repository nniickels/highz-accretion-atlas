"""Regression tests for committed v5 BLAGN science products."""

from __future__ import annotations

import sys
import tomllib
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.v5_catalogue import HARIKANE_SOURCE_KEY
from src.v5_science import EPSILON, MERGER_BOOST, Z_SEED, evaluate_catalogue, prepare_catalogue_view


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
            "measurement_history": "measurement_accretion_history",
            "object_history": "physical_object_accretion_history",
            "ranking_comparison": "primary_ranking_comparison",
        }
        cls.frames = {
            name: pd.read_csv(ROOT / "results/releases/v5/tables" / f"v5_blagn_{stem}.csv")
            for name, stem in stems.items()
        }

    def test_counts_release_and_ranks(self) -> None:
        expected = {
            "measurement_eval": 464, "object_eval": 439, "measurement_point": 106,
            "object_point": 99, "measurement_fedd": 1392, "measurement_mseed": 928,
            "object_fedd": 1317, "object_mseed": 878,
            "measurement_uncertainty": 106, "object_uncertainty": 99,
            "alternate_sensitivity": 7,
            "measurement_history": 318, "object_history": 297,
            "ranking_comparison": 99,
        }
        for name, count in expected.items():
            self.assertEqual(len(self.frames[name]), count, name)
        for frame in self.frames.values():
            self.assertTrue(frame["catalogue_release"].eq("v5-blagn").all())
        for name, column in [
            ("measurement_point", "rank_growth_pressure"),
            ("object_point", "rank_growth_pressure"),
            ("measurement_uncertainty", "rank_uncertainty_pressure"),
            ("object_uncertainty", "rank_uncertainty_pressure"),
        ]:
            self.assertEqual(
                sorted(self.frames[name][column].astype(int)),
                list(range(1, len(self.frames[name]) + 1)),
                name,
            )
        for name, column in [
            ("measurement_point", "rank_primary_growth_pressure"),
            ("object_point", "rank_primary_growth_pressure"),
            ("measurement_uncertainty", "rank_primary_uncertainty_pressure"),
            ("object_uncertainty", "rank_primary_uncertainty_pressure"),
        ]:
            ranks = self.frames[name][column].dropna().astype(int)
            self.assertEqual(sorted(ranks), list(range(1, len(ranks) + 1)), name)

    def test_current_package_is_v7_5_and_frozen_v5_figures_remain(self) -> None:
        metadata = tomllib.loads((ROOT / "pyproject.toml").read_text())
        self.assertEqual(metadata["project"]["version"], "7.5.0")
        expected = {
            "v5_main_text_mbh_redshift_growth_overview.png",
            "v5_main_text_primary_vs_full_ranking.png",
            "v5_main_text_accretion_history_diagnostics.png",
            "v5_appendix_measurement_choice_sensitivity.png",
        }
        figure_dir = ROOT / "results/releases/v5/figures/main_text"
        self.assertEqual({path.name for path in figure_dir.glob("*.png")}, expected)
        for name in expected:
            data = (figure_dir / name).read_bytes()
            self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"), name)
            self.assertGreater(len(data), 50_000, name)

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
        v4 = pd.read_csv(ROOT / "results/releases/v4/tables/v4_blagn_measurement_point_ranking.csv").set_index("measurement_id")
        for column in ["req_fedd_seed1e2_z30_eps0p1_b1", "req_log_mseed_fedd0p3_z30_eps0p1_b1"]:
            np.testing.assert_allclose(v5.loc[v4.index, column], v4[column], rtol=0, atol=1e-12)

    def test_top_rank_change_is_auditable(self) -> None:
        point = self.frames["object_point"].set_index("physical_object_id")
        self.assertEqual(int(point.loc["HZA-CEERS-00717", "rank_growth_pressure"]), 4)
        uncertainty = self.frames["object_uncertainty"].set_index("physical_object_id")
        self.assertEqual(int(uncertainty.loc["HZA-CEERS-00717", "rank_uncertainty_pressure"]), 5)

    def test_taxonomy_propagates_and_is_stratified(self) -> None:
        fields = {
            "evidence_status", "evidence_status_basis", "spectroscopic_type",
            "selection_channels", "phenotype_tags", "lensing_status",
            "growth_ranking_eligible_flag", "primary_growth_ranking_flag",
        }
        for name in [
            "measurement_eval", "object_eval", "measurement_point", "object_point",
            "measurement_fedd", "measurement_mseed", "object_fedd", "object_mseed",
            "measurement_uncertainty", "object_uncertainty",
        ]:
            self.assertTrue(fields.issubset(self.frames[name].columns), name)
        expected_strata = {
            "object_class", "evidence_status", "spectroscopic_type",
            "growth_ranking_eligibility", "primary_growth_ranking_population",
        }
        self.assertTrue(expected_strata.issubset(set(self.frames["catalogue_summary"]["stratum_type"])))
        self.assertTrue(expected_strata.issubset(set(self.frames["growth_summary"]["stratum_type"])))

    def test_growth_workflow_rejects_ineligible_rows(self) -> None:
        measurements = pd.read_csv(ROOT / "data/processed/v5/v5_blagn_measurements.csv").head(1)
        measurements.loc[:, "growth_ranking_eligible_flag"] = False
        measurements.loc[:, "primary_growth_ranking_flag"] = False
        prepared = prepare_catalogue_view(measurements, view="measurement")
        with self.assertRaisesRegex(ValueError, "ineligible catalogue rows"):
            evaluate_catalogue(prepared)

    def test_growth_summary_names_all_selection_families(self) -> None:
        overall = self.frames["growth_summary"][
            self.frames["growth_summary"]["stratum_type"].eq("overall")
        ]
        for label in ["JADES", "CEERS/RUBIES", "EIGER/FRESCO", "ASPIRE", "Harikane"]:
            self.assertTrue(overall["selection_function_note"].str.contains(label, regex=False).all())

    def test_primary_ranking_excludes_candidates_but_preserves_diagnostics(self) -> None:
        point = self.frames["object_point"].set_index("physical_object_id")
        candidate = point.loc["HZA-RUBIES-EGS-49140"]
        self.assertEqual(int(candidate["rank_growth_pressure"]), 3)
        self.assertTrue(pd.isna(candidate["rank_primary_growth_pressure"]))
        self.assertEqual(candidate["ranking_population"], "exploratory_candidate_or_disputed")
        primary = point["rank_primary_growth_pressure"].dropna().astype(int)
        self.assertEqual(sorted(primary), list(range(1, 99)))
        self.assertEqual(int(point.loc["HZA-CEERS-00717", "rank_primary_growth_pressure"]), 3)
        uncertainty = self.frames["object_uncertainty"].set_index("physical_object_id")
        self.assertTrue(pd.isna(
            uncertainty.loc["HZA-RUBIES-EGS-49140", "rank_primary_uncertainty_pressure"]
        ))

    def test_object_lrd_summary_preserves_unreported_state(self) -> None:
        summary = self.frames["catalogue_summary"]
        self.assertTrue(
            (summary["n_lrd"] + summary["n_non_lrd"] + summary["n_lrd_not_reported"])
            .eq(summary["n_rows"])
            .all()
        )
        overall = self.frames["catalogue_summary"][
            self.frames["catalogue_summary"]["catalogue_view"].eq("physical_object")
            & self.frames["catalogue_summary"]["stratum_type"].eq("overall")
        ].iloc[0]
        self.assertEqual(int(overall["n_lrd"]), 53)
        self.assertEqual(int(overall["n_non_lrd"]), 19)
        self.assertEqual(int(overall["n_lrd_not_reported"]), 27)

    def test_accretion_history_duty_cycle_semantics(self) -> None:
        history = self.frames["object_history"]
        self.assertEqual(set(history["burst_fedd"]), {1.0, 2.0, 3.0})
        self.assertTrue(history["z_seed"].eq(30.0).all())
        self.assertTrue(history["epsilon"].eq(0.1).all())
        self.assertTrue(history["merger_boost"].eq(1.0).all())
        np.testing.assert_allclose(
            history["required_duty_cycle_point"],
            history["required_lifetime_average_fedd_point"] / history["burst_fedd"],
            rtol=0, atol=1e-12,
        )
        self.assertTrue(
            history["required_duty_cycle_p16"].le(history["required_duty_cycle_p50"]).all()
        )
        self.assertTrue(
            history["required_duty_cycle_p50"].le(history["required_duty_cycle_p84"]).all()
        )
        unavailable = history[history["reported_current_fedd"].isna()]
        self.assertTrue(unavailable["current_to_required_fedd_ratio"].isna().all())
        self.assertTrue(history["current_fedd_is_instantaneous_not_history"].astype(bool).all())
        self.assertFalse(history["mass_systematic_applied"].astype(bool).any())
        provenance = {
            "evidence_status_basis", "spectroscopic_type", "selection_channels",
            "phenotype_tags", "detection_evidence", "quality_flag", "mbh_method",
            "source_table", "source_paper_version", "source_url", "source_doi",
            "source_caveat_tags", "log_mbh_systematic_dex", "mbh_systematic_kind",
            "mbh_formal_uncertainty_kind", "edd_ratio_consistency_flag",
            "edd_ratio_log_residual_dex", "current_fedd_comparison_eligible_flag",
            "current_fedd_comparison_status",
        }
        self.assertTrue(provenance.issubset(history.columns))

    def test_inconsistent_current_fedd_is_retained_but_not_compared(self) -> None:
        for name in ["measurement_history", "object_history"]:
            history = self.frames[name]
            gn = history[history["physical_object_id"].eq("HZA-GN-11836")]
            self.assertEqual(len(gn), 3)
            self.assertTrue(gn["reported_current_fedd"].eq(0.11).all())
            self.assertTrue(gn["edd_ratio_consistency_flag"].eq("inconsistent").all())
            self.assertTrue(np.isfinite(gn["edd_ratio_log_residual_dex"]).all())
            self.assertTrue(gn["current_to_required_fedd_ratio"].isna().all())
            self.assertFalse(gn["current_fedd_comparison_eligible_flag"].astype(bool).any())
            self.assertTrue(
                gn["current_fedd_comparison_status"]
                .eq("excluded_source_table_inconsistency").all()
            )

    def test_paper_ranking_comparison_distinguishes_populations(self) -> None:
        comparison = self.frames["ranking_comparison"].set_index("physical_object_id")
        candidate = comparison.loc["HZA-RUBIES-EGS-49140"]
        self.assertEqual(int(candidate["rank_growth_pressure"]), 3)
        self.assertTrue(pd.isna(candidate["rank_primary_growth_pressure"]))
        self.assertEqual(candidate["full_ranking_role"], "exploratory_diagnostic")
        self.assertEqual(candidate["primary_ranking_role"], "excluded_candidate_or_disputed")
        self.assertEqual(
            int(comparison.loc["HZA-CEERS-00717", "rank_primary_growth_pressure"]), 3
        )
        self.assertTrue({
            "evidence_status_basis", "spectroscopic_type", "selection_channels",
            "phenotype_tags", "quality_flag", "detection_evidence", "mbh_method",
            "source_caveat_tags", "detection_confidence_tier",
            "mass_measurement_reliability_tier",
        }.issubset(comparison.columns))


if __name__ == "__main__":
    unittest.main()
