"""Lightweight verification checks for the v1 catalogue and v2 analysis."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.generate_v2_rankings import build_ranking_table, read_inputs
from scripts.generate_v2_uncertainty_rankings import (
    asymmetric_normal_samples,
    build_outputs as build_uncertainty_outputs,
    resolve_mbh_uncertainty,
    uncertainty_followup_category,
    verify_outputs as verify_uncertainty_outputs,
)
from src import models
from src.scoring import (
    aggregate_feasibility_score,
    score_model_table,
    score_required_fedd,
    score_required_seed_mass,
)
from src.standardize_data import CANONICAL_RAW_FIELDS, standardize_dataframe


def minimal_raw_rows() -> pd.DataFrame:
    """Return canonical raw rows covering robust/tentative and missing optional fields."""
    rows = [
        {
            "measurement_id": "obj_lowz",
            "object_id": "LOWZ",
            "ra_deg": 1.0,
            "dec_deg": 2.0,
            "redshift": 3.9,
            "redshift_kind": "spec",
            "survey": "TEST",
            "object_class": "broad-line-agn",
            "log_mbh_msun": 6.5,
            "log_mbh_err_plus": 0.2,
            "log_mbh_err_minus": 0.2,
            "mbh_method": "test-method",
            "detection_evidence": "individual_robust",
            "log_mstar_msun": 8.0,
            "log_mstar_err_plus": 0.3,
            "log_mstar_err_minus": 0.3,
            "mstar_method": "test-sed",
            "log_lbol_erg_s": 44.0,
            "log_lbol_err_plus": 0.1,
            "log_lbol_err_minus": 0.1,
            "lbol_method": "test-bol",
            "edd_ratio_reported": 0.1,
            "edd_ratio_err_plus": 0.02,
            "edd_ratio_err_minus": 0.02,
            "agn_contam_flag": 0,
            "lensing_mu": np.nan,
            "lensing_mu_err": np.nan,
            "source_key": "test_source",
            "source_table": "test_table",
            "notes": "Robust sample; synthetic test row.",
        },
        {
            "measurement_id": "obj_highz_full",
            "object_id": "HIGHZ-FULL",
            "ra_deg": 3.0,
            "dec_deg": 4.0,
            "redshift": 5.1,
            "redshift_kind": "spec",
            "survey": "TEST",
            "object_class": "broad-line-agn",
            "log_mbh_msun": 7.0,
            "log_mbh_err_plus": 0.2,
            "log_mbh_err_minus": 0.2,
            "mbh_method": "test-method",
            "detection_evidence": "individual_robust",
            "log_mstar_msun": 9.0,
            "log_mstar_err_plus": 0.3,
            "log_mstar_err_minus": 0.4,
            "mstar_method": "test-sed",
            "log_lbol_erg_s": 44.3,
            "log_lbol_err_plus": 0.1,
            "log_lbol_err_minus": 0.1,
            "lbol_method": "test-bol",
            "edd_ratio_reported": 0.2,
            "edd_ratio_err_plus": 0.03,
            "edd_ratio_err_minus": 0.01,
            "agn_contam_flag": 1,
            "lensing_mu": np.nan,
            "lensing_mu_err": np.nan,
            "source_key": "test_source",
            "source_table": "test_table",
            "notes": "Robust sample; synthetic test row.",
        },
        {
            "measurement_id": "obj_highz_missing",
            "object_id": "HIGHZ-MISSING",
            "ra_deg": 5.0,
            "dec_deg": 6.0,
            "redshift": 6.0,
            "redshift_kind": "spec",
            "survey": "TEST",
            "object_class": "broad-line-agn",
            "log_mbh_msun": 7.2,
            "log_mbh_err_plus": 0.2,
            "log_mbh_err_minus": 0.2,
            "mbh_method": "test-method",
            "detection_evidence": "individual_tentative",
            "log_mstar_msun": np.nan,
            "log_mstar_err_plus": np.nan,
            "log_mstar_err_minus": np.nan,
            "mstar_method": "",
            "log_lbol_erg_s": 44.5,
            "log_lbol_err_plus": 0.1,
            "log_lbol_err_minus": 0.1,
            "lbol_method": "test-bol",
            "edd_ratio_reported": np.nan,
            "edd_ratio_err_plus": np.nan,
            "edd_ratio_err_minus": np.nan,
            "agn_contam_flag": 0,
            "lensing_mu": np.nan,
            "lensing_mu_err": np.nan,
            "source_key": "test_source",
            "source_table": "test_table",
            "notes": "Tentative sample; synthetic test row.",
        },
    ]
    df = pd.DataFrame(rows)
    return df[CANONICAL_RAW_FIELDS]


class ModelsTests(unittest.TestCase):
    def test_two_state_duty_cycle_model(self) -> None:
        average = models.two_state_average_fedd(0.25, 2.0)
        self.assertAlmostEqual(float(average), 0.5)
        required = models.required_duty_cycle(np.array([0.5, 2.5]), 2.0)
        np.testing.assert_allclose(required, [0.25, 1.25])
        self.assertGreater(float(required[1]), 1.0)
        with self.assertRaisesRegex(ValueError, "0 <= D <= 1"):
            models.two_state_average_fedd(1.1, 2.0)
        with self.assertRaisesRegex(ValueError, "burst_fedd must be >"):
            models.required_duty_cycle(0.5, 0.2, 0.2)
        with self.assertRaisesRegex(ValueError, "required_fedd_avg must be >="):
            models.required_duty_cycle(0.1, 1.0, 0.2)

    def test_run_growth_sanity_checks(self) -> None:
        checks = models.run_growth_sanity_checks()
        self.assertAlmostEqual(checks["merger_boost_x2_dex"], np.log10(2.0), places=12)
        self.assertAlmostEqual(checks["epsilon_spin_minus1"], 0.03774955, places=7)
        self.assertAlmostEqual(checks["epsilon_spin_0"], 0.05719096, places=7)
        self.assertAlmostEqual(checks["epsilon_spin_plus1"], 0.42264973, places=7)
        self.assertAlmostEqual(checks["roundtrip_required_fedd"], 1.0, places=12)

    def test_required_fedd_and_required_seed_round_trip(self) -> None:
        z_seed = 30.0
        z_obs = 7.0
        epsilon = 0.1
        log_seed = 4.0
        predicted = models.predicted_log_mbh(log_seed, 0.7, epsilon, z_seed, z_obs, merger_boost=2.0)
        recovered_fedd = models.required_fedd_for_seed(
            log_seed,
            predicted,
            epsilon,
            z_seed,
            z_obs,
            merger_boost=2.0,
        )
        recovered_seed = models.required_seed_mass_for_growth(
            predicted,
            0.7,
            epsilon,
            z_seed,
            z_obs,
            merger_boost=2.0,
        )
        self.assertAlmostEqual(float(recovered_fedd), 0.7, places=12)
        self.assertAlmostEqual(float(recovered_seed), log_seed, places=12)

    def test_invalid_inputs_raise(self) -> None:
        with self.assertRaises(ValueError):
            models.cosmic_time_gyr(-1.0)
        with self.assertRaises(ValueError):
            models.available_growth_time_gyr(z_seed=6.0, z_obs=7.0)
        with self.assertRaises(ValueError):
            models.growth_log10_factor(f_edd=-0.1, epsilon=0.1, delta_t_gyr=0.5)
        with self.assertRaises(ValueError):
            models.growth_log10_factor(f_edd=1.0, epsilon=1.0, delta_t_gyr=0.5)
        with self.assertRaises(ValueError):
            models.predicted_log_mbh_from_delta_t(4.0, 1.0, 0.1, 0.5, merger_boost=0.0)


class StandardizeDataTests(unittest.TestCase):
    def test_required_columns_validation(self) -> None:
        raw = minimal_raw_rows().drop(columns=["source_table"])
        with self.assertRaisesRegex(ValueError, "Missing canonical raw fields"):
            standardize_dataframe(raw)

    def test_required_values_and_uniqueness_validation(self) -> None:
        missing_required = minimal_raw_rows()
        missing_required.loc[1, "log_mbh_msun"] = np.nan
        with self.assertRaisesRegex(ValueError, "Required column 'log_mbh_msun'"):
            standardize_dataframe(missing_required)

        duplicate_ids = minimal_raw_rows()
        duplicate_ids.loc[1, "measurement_id"] = duplicate_ids.loc[2, "measurement_id"]
        with self.assertRaisesRegex(ValueError, "measurement_id must be unique"):
            standardize_dataframe(duplicate_ids)

    def test_redshift_filter_and_optional_missingness_flags(self) -> None:
        standardized = standardize_dataframe(minimal_raw_rows())
        self.assertEqual(len(standardized), 2)
        self.assertTrue((standardized["redshift"] >= 4.0).all())

        full = standardized.set_index("measurement_id").loc["obj_highz_full"]
        missing = standardized.set_index("measurement_id").loc["obj_highz_missing"]
        self.assertFalse(bool(full["missing_mstar_flag"]))
        self.assertTrue(bool(full["missing_lensing_flag"]))
        self.assertEqual(full["missing_optional_fields"], "lensing")
        self.assertTrue(bool(missing["missing_mstar_flag"]))
        self.assertTrue(bool(missing["missing_edd_ratio_flag"]))
        self.assertEqual(missing["missing_optional_fields"], "mstar;edd_ratio;lensing")

    def test_optional_methods_required_when_values_present(self) -> None:
        raw = minimal_raw_rows()
        raw.loc[1, "mstar_method"] = ""
        with self.assertRaisesRegex(ValueError, "Mstar values require mstar_method"):
            standardize_dataframe(raw)

    def test_nonblank_malformed_numeric_values_raise(self) -> None:
        raw = minimal_raw_rows()
        raw["redshift"] = raw["redshift"].astype(object)
        raw.loc[1, "redshift"] = "not-a-redshift"
        with self.assertRaisesRegex(ValueError, "Column 'redshift' has non-numeric values"):
            standardize_dataframe(raw)

    def test_detection_evidence_is_structured_and_drives_quality(self) -> None:
        raw = minimal_raw_rows()
        raw.loc[1, "detection_evidence"] = "stack_supported_tentative_hbeta"
        standardized = standardize_dataframe(raw).set_index("measurement_id")

        self.assertEqual(standardized.loc["obj_highz_full", "quality_flag"], "tentative")
        self.assertEqual(
            standardized.loc["obj_highz_full", "detection_evidence"],
            "stack_supported_tentative_hbeta",
        )

        invalid = minimal_raw_rows()
        invalid.loc[1, "detection_evidence"] = "free-text-status"
        with self.assertRaisesRegex(ValueError, "detection_evidence must be one of"):
            standardize_dataframe(invalid)

    def test_eddington_ratio_consistency_crosscheck_and_domains(self) -> None:
        standardized = standardize_dataframe(minimal_raw_rows()).set_index("measurement_id")
        full = standardized.loc["obj_highz_full"]
        expected = 10.0 ** (44.3 - 7.0) / 1.26e38
        self.assertAlmostEqual(full["edd_ratio_from_mbh_lbol"], expected, places=12)
        self.assertEqual(full["edd_ratio_consistency_flag"], "consistent")

        inconsistent = minimal_raw_rows()
        inconsistent.loc[1, "edd_ratio_reported"] = 0.01
        flagged = standardize_dataframe(inconsistent).set_index("measurement_id").loc["obj_highz_full"]
        self.assertEqual(flagged["edd_ratio_consistency_flag"], "inconsistent")

        invalid_ratio = minimal_raw_rows()
        invalid_ratio.loc[1, "edd_ratio_reported"] = 0.0
        with self.assertRaisesRegex(ValueError, "edd_ratio_reported must be positive"):
            standardize_dataframe(invalid_ratio)

        invalid_error = minimal_raw_rows()
        invalid_error.loc[1, "log_mbh_err_plus"] = -0.1
        with self.assertRaisesRegex(ValueError, "must be non-negative"):
            standardize_dataframe(invalid_error)


class ScoringTests(unittest.TestCase):
    def test_seed_score_flags_both_undergrowth_and_overgrowth_mismatch(self) -> None:
        inside = score_required_seed_mass(5.0, 4.0, 6.0)
        overgrowth_like = score_required_seed_mass(3.0, 4.0, 6.0)
        undergrowth_like = score_required_seed_mass(7.0, 4.0, 6.0)

        self.assertEqual(inside, 1.0)
        self.assertEqual(overgrowth_like, 0.0)
        self.assertEqual(undergrowth_like, 0.0)
        self.assertEqual(overgrowth_like, undergrowth_like)

    def test_fedd_and_aggregate_scores(self) -> None:
        self.assertEqual(score_required_fedd(0.5), 1.0)
        self.assertEqual(score_required_fedd(3.5), 0.0)
        self.assertAlmostEqual(score_required_fedd(2.0), 0.5)
        self.assertAlmostEqual(aggregate_feasibility_score(1.0, 0.5, weights=(1.0, 1.0)), 0.75)

    def test_score_model_table(self) -> None:
        evaluations = pd.DataFrame(
            {
                "required_log_mseed": [5.0, 3.0, 7.0],
                "model_log_mseed_min": [4.0, 4.0, 4.0],
                "model_log_mseed_max": [6.0, 6.0, 6.0],
                "required_fedd": [0.5, 0.5, 2.0],
            }
        )
        scored = score_model_table(evaluations)
        self.assertIn("feasibility_score", scored.columns)
        self.assertEqual(scored.loc[0, "seed_mass_score"], 1.0)
        self.assertEqual(scored.loc[1, "seed_mass_score"], 0.0)
        self.assertEqual(scored.loc[2, "seed_mass_score"], 0.0)


class RankingGeneratorTests(unittest.TestCase):
    def test_v2_release_metadata_identifies_v1_input(self) -> None:
        catalogue, required_fedd, required_mseed = read_inputs()
        ranking = build_ranking_table(catalogue, required_fedd, required_mseed)
        self.assertTrue(ranking["analysis_release"].eq("v2").all())
        self.assertTrue(ranking["input_catalogue_release"].eq("v1").all())

    def test_current_v1_ranking_table_contract(self) -> None:
        catalogue, required_fedd, required_mseed = read_inputs()
        ranking = build_ranking_table(catalogue, required_fedd, required_mseed)

        required_columns = {
            "rank_physical_pressure",
            "rank_followup_priority",
            "measurement_id",
            "object_id",
            "redshift",
            "quality_flag",
            "detection_evidence",
            "edd_ratio_consistency_flag",
            "edd_ratio_log_residual_dex",
            "req_fedd_seed1e2_z30_eps0p1_b1",
            "req_fedd_seed1e4_z30_eps0p1_b1",
            "req_fedd_seed1e5_z30_eps0p1_b1",
            "req_log_mseed_fedd0p3_z30_eps0p1_b1",
            "req_log_mseed_fedd1_z30_eps0p1_b1",
            "mbh_mstar_tension_label",
            "missing_mstar_flag",
            "caveat_tags",
            "followup_priority_category",
            "followup_priority_reason",
        }
        self.assertTrue(required_columns.issubset(ranking.columns))
        self.assertEqual(len(ranking), len(catalogue))
        self.assertTrue(ranking["measurement_id"].is_unique)
        self.assertFalse(ranking["req_fedd_seed1e2_z30_eps0p1_b1"].isna().any())
        self.assertFalse(ranking["req_log_mseed_fedd0p3_z30_eps0p1_b1"].isna().any())

    def test_expected_high_leverage_objects_rank_near_top(self) -> None:
        catalogue, required_fedd, required_mseed = read_inputs()
        ranking = build_ranking_table(catalogue, required_fedd, required_mseed)
        top_objects = set(ranking.nsmallest(8, "rank_physical_pressure")["object_id"])
        expected = {"GN-38509", "GS-20057765", "GS-20030333", "GS-164055", "GN-4685", "GN-954"}

        self.assertTrue(expected.issubset(set(ranking["object_id"])))
        self.assertTrue(expected.issubset(top_objects))

        gn38509 = ranking.loc[ranking["object_id"] == "GN-38509"].iloc[0]
        gs20057765 = ranking.loc[ranking["object_id"] == "GS-20057765"].iloc[0]
        self.assertEqual(gn38509["followup_priority_category"], "A_robust_high_pressure")
        self.assertEqual(gs20057765["followup_priority_category"], "B_tentative_high_pressure")
        self.assertEqual(gs20057765["mbh_method"], "single-epoch-virial-hbeta")
        self.assertEqual(gs20057765["detection_evidence"], "stack_supported_tentative_hbeta")
        self.assertEqual(gs20057765["measurement_confidence_tier"], "low")
        self.assertIn("individual_detection_not_formally_significant", gs20057765["caveat_tags"])

        restored_hosts = ranking.set_index("object_id").loc[
            ["GS-200679", "GS-20030333", "GS-164055"]
        ]
        self.assertFalse(restored_hosts["missing_mstar_flag"].any())
        np.testing.assert_allclose(restored_hosts["log_mstar_msun"], [8.53, 8.61, 7.99])
        self.assertEqual(restored_hosts.loc["GS-20030333", "mbh_mstar_tension_label"], "elevated")
        self.assertEqual(restored_hosts.loc["GS-164055", "mbh_mstar_tension_label"], "extreme")

        gn11836 = ranking.loc[ranking["object_id"].eq("GN-11836")].iloc[0]
        self.assertEqual(gn11836["edd_ratio_consistency_flag"], "inconsistent")
        self.assertAlmostEqual(gn11836["edd_ratio_from_mbh_lbol"], 0.890491, places=6)
        self.assertAlmostEqual(gn11836["edd_ratio_log_residual_dex"], -0.908237, places=6)
        self.assertEqual(gn11836["measurement_confidence_tier"], "medium")
        self.assertEqual(gn11836["followup_priority_category"], "D_source_consistency")
        self.assertIn("published_edd_ratio_inconsistent_with_mbh_lbol", gn11836["caveat_tags"])

    def test_ranking_metrics_match_baseline_source_result_rows(self) -> None:
        catalogue, required_fedd, required_mseed = read_inputs()
        ranking = build_ranking_table(catalogue, required_fedd, required_mseed)

        baseline_fedd = required_fedd[
            required_fedd["interpretation_variant"].eq("baseline")
            & required_fedd["fedd_requirement_config"].eq("eps0p1_no_merger_boost")
        ]
        for seed_assumption, ranking_col in [
            ("seed_1e2_msun", "req_fedd_seed1e2_z30_eps0p1_b1"),
            ("seed_1e4_msun", "req_fedd_seed1e4_z30_eps0p1_b1"),
            ("seed_1e5_msun", "req_fedd_seed1e5_z30_eps0p1_b1"),
        ]:
            source = baseline_fedd[baseline_fedd["seed_mass_assumption"].eq(seed_assumption)][
                ["measurement_id", "required_fedd"]
            ]
            merged = ranking[["measurement_id", ranking_col]].merge(
                source,
                on="measurement_id",
                how="left",
                validate="one_to_one",
            )
            self.assertFalse(merged["required_fedd"].isna().any())
            self.assertTrue(np.allclose(merged[ranking_col], merged["required_fedd"], rtol=0.0, atol=0.0))

        baseline_mseed = required_mseed[required_mseed["interpretation_variant"].eq("baseline")]
        for growth_config, log_col, linear_col in [
            (
                "fedd0p3_eps0p1_no_merger_boost",
                "req_log_mseed_fedd0p3_z30_eps0p1_b1",
                "req_mseed_fedd0p3_msun",
            ),
            (
                "fedd1_eps0p1_no_merger_boost",
                "req_log_mseed_fedd1_z30_eps0p1_b1",
                "req_mseed_fedd1_msun",
            ),
        ]:
            source = baseline_mseed[baseline_mseed["growth_config"].eq(growth_config)][
                ["measurement_id", "required_log_mseed", "required_mseed_msun"]
            ]
            merged = ranking[["measurement_id", log_col, linear_col]].merge(
                source,
                on="measurement_id",
                how="left",
                validate="one_to_one",
            )
            self.assertFalse(merged["required_log_mseed"].isna().any())
            self.assertTrue(np.allclose(merged[log_col], merged["required_log_mseed"], rtol=0.0, atol=0.0))
            self.assertTrue(np.allclose(merged[linear_col], merged["required_mseed_msun"], rtol=0.0, atol=0.0))


class V1NumericRegressionAnchorTests(unittest.TestCase):
    """Lock current v1 outputs against accidental science-drift.

    These anchors describe the present v1 catalogue and baseline output CSVs.
    They are regression sentinels, not universal physical truths: if the sample,
    assumptions, or source extraction intentionally changes, these expected
    values should be reviewed and updated in the same change.
    """

    def test_processed_catalogue_current_v1_sample_anchors(self) -> None:
        catalogue = pd.read_csv(REPO_ROOT / "data" / "processed" / "v1_processed.csv")

        self.assertEqual(len(catalogue), 23)
        self.assertAlmostEqual(catalogue["redshift"].min(), 4.133, places=3)
        self.assertAlmostEqual(catalogue["redshift"].max(), 8.913, places=3)
        self.assertEqual(catalogue["quality_flag"].value_counts().to_dict(), {"robust": 18, "tentative": 5})
        self.assertEqual(int(catalogue["missing_mstar_flag"].sum()), 1)
        inconsistent = catalogue[catalogue["edd_ratio_consistency_flag"].eq("inconsistent")]
        self.assertEqual(inconsistent["object_id"].tolist(), ["GN-11836"])

    def test_baseline_light_seed_required_fedd_top_objects(self) -> None:
        required_fedd = pd.read_csv(REPO_ROOT / "results" / "v1_required_fedd_by_seed_mass.csv")
        baseline_light_seed = required_fedd[
            required_fedd["interpretation_variant"].eq("baseline")
            & required_fedd["fedd_requirement_config"].eq("eps0p1_no_merger_boost")
            & required_fedd["seed_mass_assumption"].eq("seed_1e2_msun")
        ]

        expected_top_six = {"GS-20057765", "GS-20030333", "GS-164055", "GN-38509", "GN-4685", "GN-954"}
        actual_top_six = set(baseline_light_seed.nlargest(6, "required_fedd")["object_id"])
        self.assertEqual(actual_top_six, expected_top_six)

    def test_baseline_gentle_growth_required_seed_top_object(self) -> None:
        required_mseed = pd.read_csv(REPO_ROOT / "results" / "v1_required_mseed_by_growth_assumption.csv")
        baseline_gentle = required_mseed[
            required_mseed["interpretation_variant"].eq("baseline")
            & required_mseed["growth_config"].eq("fedd0p3_eps0p1_no_merger_boost")
        ]

        top = baseline_gentle.nlargest(1, "required_log_mseed").iloc[0]
        self.assertEqual(top["object_id"], "GN-38509")
        self.assertAlmostEqual(top["required_log_mseed"], 6.718503, places=6)

    def test_result_table_merger_boost_x2_shifts_required_seed_by_log10_two(self) -> None:
        required_mseed = pd.read_csv(REPO_ROOT / "results" / "v1_required_mseed_by_growth_assumption.csv")
        baseline = required_mseed[
            required_mseed["interpretation_variant"].eq("baseline")
            & required_mseed["growth_config"].eq("fedd0p3_eps0p1_no_merger_boost")
        ].set_index("measurement_id")
        boosted = required_mseed[
            required_mseed["interpretation_variant"].eq("baseline")
            & required_mseed["growth_config"].eq("fedd0p3_eps0p1_merger_boost_x2")
        ].set_index("measurement_id")

        diff = baseline["required_log_mseed"] - boosted["required_log_mseed"]
        self.assertTrue(np.allclose(diff.to_numpy(), np.log10(2.0), rtol=0.0, atol=1e-12))

    def test_model_round_trip_regression_anchor(self) -> None:
        checks = models.run_growth_sanity_checks()

        self.assertAlmostEqual(checks["roundtrip_required_fedd"], 1.0, places=12)
        self.assertAlmostEqual(checks["roundtrip_required_log_mseed"], 5.0, places=12)
        self.assertAlmostEqual(checks["merger_boost_x2_dex"], np.log10(2.0), places=12)


class UncertaintyPropagationTests(unittest.TestCase):
    def test_v2_uncertainty_release_metadata_identifies_v1_input(self) -> None:
        fedd, mseed, ranking = build_uncertainty_outputs(n_samples=32, random_seed=13579)
        for frame in [fedd, mseed, ranking]:
            self.assertTrue(frame["analysis_release"].eq("v2").all())
            self.assertTrue(frame["input_catalogue_release"].eq("v1").all())

    def test_source_consistency_precedes_pressure_and_host_categories(self) -> None:
        row = pd.Series(
            {
                "followup_priority_category": "D_source_consistency",
                "uncertainty_growth_pressure_tier": "likely_high_pressure",
                "quality_flag": "robust",
                "mbh_mstar_tension_label": "extreme",
            }
        )

        self.assertEqual(uncertainty_followup_category(row), "D_source_consistency")

    def test_uncertainty_verifier_accepts_catalogue_without_source_inconsistencies(self) -> None:
        fedd, mseed, ranking = build_uncertainty_outputs(n_samples=64, random_seed=24680)
        clean_ranking = ranking.copy()
        source_rows = clean_ranking["followup_priority_category"].eq("D_source_consistency")
        clean_ranking.loc[source_rows, "followup_priority_category"] = "E_comparison_anchor"
        clean_ranking.loc[source_rows, "uncertainty_followup_category"] = (
            "E_comparison_or_systematics_anchor"
        )
        point_ranking = clean_ranking.drop(columns=["rank_uncertainty_pressure"])

        verify_uncertainty_outputs(point_ranking, fedd, mseed, clean_ranking)

    def test_asymmetric_mbh_sampling_and_missing_error_modes(self) -> None:
        rng = np.random.default_rng(123)
        samples = asymmetric_normal_samples(7.0, 0.6, 0.3, n_samples=200000, rng=rng)

        self.assertAlmostEqual(float(np.percentile(samples, 50)), 7.0, delta=0.01)
        self.assertGreater(float(np.percentile(samples, 84) - 7.0), 0.5)
        self.assertLess(float(7.0 - np.percentile(samples, 16)), 0.35)
        self.assertEqual(resolve_mbh_uncertainty(0.6, 0.3).mode, "asymmetric")
        self.assertEqual(resolve_mbh_uncertainty(0.4, np.nan).mode, "symmetric_from_plus")
        self.assertEqual(resolve_mbh_uncertainty(np.nan, 0.4).mode, "symmetric_from_minus")
        self.assertEqual(resolve_mbh_uncertainty(np.nan, np.nan).mode, "point_estimate_no_reported_mbh_error")

        point_samples = asymmetric_normal_samples(
            7.5,
            np.nan,
            np.nan,
            n_samples=128,
            rng=np.random.default_rng(456),
        )
        self.assertTrue(np.all(point_samples == 7.5))
        with self.assertRaisesRegex(ValueError, "non-negative"):
            resolve_mbh_uncertainty(-0.1, 0.2)

    def test_uncertainty_outputs_are_deterministic_for_fixed_seed(self) -> None:
        fedd_a, mseed_a, ranking_a = build_uncertainty_outputs(n_samples=256, random_seed=12345)
        fedd_b, mseed_b, ranking_b = build_uncertainty_outputs(n_samples=256, random_seed=12345)

        pd.testing.assert_frame_equal(fedd_a, fedd_b)
        pd.testing.assert_frame_equal(mseed_a, mseed_b)
        pd.testing.assert_frame_equal(ranking_a, ranking_b)

    def test_uncertainty_percentiles_and_shift_behavior(self) -> None:
        fedd, mseed, ranking = build_uncertainty_outputs(n_samples=512, random_seed=24680)

        self.assertTrue(fedd["required_fedd_p5"].le(fedd["required_fedd_p16"]).all())
        self.assertTrue(fedd["required_fedd_p16"].le(fedd["required_fedd_p50"]).all())
        self.assertTrue(fedd["required_fedd_p50"].le(fedd["required_fedd_p84"]).all())
        self.assertTrue(fedd["required_fedd_p84"].le(fedd["required_fedd_p95"]).all())
        self.assertTrue(mseed["required_log_mseed_p5"].le(mseed["required_log_mseed_p16"]).all())
        self.assertTrue(mseed["required_log_mseed_p16"].le(mseed["required_log_mseed_p50"]).all())
        self.assertTrue(mseed["required_log_mseed_p50"].le(mseed["required_log_mseed_p84"]).all())
        self.assertTrue(mseed["required_log_mseed_p84"].le(mseed["required_log_mseed_p95"]).all())

        fedd_1e2 = fedd[fedd["seed_mass_short"].eq("seed1e2")]
        base = fedd_1e2[fedd_1e2["scenario"].eq("baseline")].set_index("measurement_id")
        minus = fedd_1e2[fedd_1e2["scenario"].eq("mbh_minus_0p3dex")].set_index("measurement_id")
        plus = fedd_1e2[fedd_1e2["scenario"].eq("mbh_plus_0p3dex")].set_index("measurement_id")
        self.assertTrue(minus["required_fedd_p50"].lt(base["required_fedd_p50"]).all())
        self.assertTrue(base["required_fedd_p50"].lt(plus["required_fedd_p50"]).all())

        mseed_0p3 = mseed[mseed["growth_history"].eq("fedd0p3")]
        mbase = mseed_0p3[mseed_0p3["scenario"].eq("baseline")].set_index("measurement_id")
        mminus = mseed_0p3[mseed_0p3["scenario"].eq("mbh_minus_0p3dex")].set_index("measurement_id")
        mplus = mseed_0p3[mseed_0p3["scenario"].eq("mbh_plus_0p3dex")].set_index("measurement_id")
        self.assertTrue(mminus["required_log_mseed_p50"].lt(mbase["required_log_mseed_p50"]).all())
        self.assertTrue(mbase["required_log_mseed_p50"].lt(mplus["required_log_mseed_p50"]).all())

        expected = {"GN-38509", "GS-20057765", "GS-20030333", "GS-164055", "GN-4685"}
        top_five = set(ranking.nsmallest(5, "rank_uncertainty_pressure")["object_id"])
        self.assertEqual(top_five, expected)

    def test_uncertainty_output_contract_and_probability_bounds(self) -> None:
        fedd, mseed, ranking = build_uncertainty_outputs(n_samples=256, random_seed=13579)
        n_objects = pd.read_csv(REPO_ROOT / "data" / "processed" / "v1_processed.csv")["measurement_id"].nunique()

        self.assertEqual(len(fedd), n_objects * 3 * 3)
        self.assertEqual(len(mseed), n_objects * 3 * 2)
        self.assertEqual(len(ranking), n_objects)
        self.assertTrue(ranking["measurement_id"].is_unique)

        self.assertEqual(set(fedd["scenario"]), {"baseline", "mbh_minus_0p3dex", "mbh_plus_0p3dex"})
        provenance_fields = {
            "detection_evidence",
            "mbh_method",
            "edd_ratio_consistency_flag",
            "edd_ratio_log_residual_dex",
        }
        self.assertTrue(provenance_fields.issubset(fedd.columns))
        self.assertTrue(provenance_fields.issubset(mseed.columns))
        self.assertEqual(set(fedd["seed_mass_short"]), {"seed1e2", "seed1e4", "seed1e5"})
        self.assertEqual(set(mseed["scenario"]), {"baseline", "mbh_minus_0p3dex", "mbh_plus_0p3dex"})
        self.assertEqual(set(mseed["growth_history"]), {"fedd0p3", "fedd1"})
        self.assertEqual(set(fedd["mbh_uncertainty_mode"]), {"asymmetric", "symmetric_reported"})
        self.assertTrue(
            {
                "log_mbh_sigma_plus_used",
                "log_mbh_sigma_minus_used",
                "mbh_uncertainty_mode",
            }.issubset(ranking.columns)
        )
        self.assertTrue((fedd["log_mbh_sigma_plus_used"] >= 0).all())
        self.assertTrue((fedd["log_mbh_sigma_minus_used"] >= 0).all())

        self.assertTrue(fedd["p_required_fedd_gt1"].between(0.0, 1.0).all())
        self.assertTrue(fedd["prob_required_fedd_gt_1"].between(0.0, 1.0).all())
        self.assertTrue(np.allclose(fedd["p_required_fedd_gt1"], fedd["prob_required_fedd_gt_1"]))
        self.assertTrue(mseed["p_required_mseed_gt1e5"].between(0.0, 1.0).all())
        self.assertTrue(mseed["p_required_mseed_gt1e6"].between(0.0, 1.0).all())
        self.assertTrue(mseed["prob_required_mseed_gt_1e5"].between(0.0, 1.0).all())
        self.assertTrue(mseed["prob_required_mseed_gt_1e6"].between(0.0, 1.0).all())
        self.assertTrue(np.allclose(mseed["p_required_mseed_gt1e5"], mseed["prob_required_mseed_gt_1e5"]))
        self.assertTrue(np.allclose(mseed["p_required_mseed_gt1e6"], mseed["prob_required_mseed_gt_1e6"]))
        self.assertTrue((mseed["p_required_mseed_gt1e6"] <= mseed["p_required_mseed_gt1e5"]).all())

        gn11836 = ranking.loc[ranking["object_id"].eq("GN-11836")].iloc[0]
        self.assertEqual(gn11836["followup_priority_category"], "D_source_consistency")
        self.assertEqual(gn11836["uncertainty_followup_category"], "D_source_consistency")
        self.assertIn("requires source clarification", gn11836["uncertainty_followup_reason"])

        required_ranking_columns = {
            "rank_uncertainty_pressure",
            "uncertainty_growth_pressure_tier",
            "uncertainty_followup_category",
            "uncertainty_followup_reason",
            "prob_required_fedd_seed1e2_gt_1_baseline",
            "prob_required_mseed_fedd0p3_gt_1e5_baseline",
            "prob_required_mseed_fedd0p3_gt_1e6_baseline",
            "p_req_fedd_seed1e2_gt1_baseline",
            "p_req_log_mseed_fedd0p3_gt1e5_baseline",
            "p_req_log_mseed_fedd0p3_gt1e6_baseline",
        }
        self.assertTrue(required_ranking_columns.issubset(ranking.columns))
        self.assertTrue(
            ranking["uncertainty_followup_reason"].str.contains("under baseline assumptions", regex=False).all()
        )
        self.assertTrue(
            ranking["uncertainty_followup_reason"].str.contains("robust|tentative", case=False, regex=True).all()
        )


if __name__ == "__main__":
    unittest.main()
