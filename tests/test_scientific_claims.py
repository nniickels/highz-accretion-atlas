"""Focused regression anchors for headline v3 manuscript claims."""

from __future__ import annotations

import unittest
from pathlib import Path

import pandas as pd

from src.internal.atlas import (
    FULL_TRACK_CURVE_COUNT,
    FULL_TRACK_EPSILON_CASES,
    FULL_TRACK_FEDD_STYLES,
    FULL_TRACK_MERGER_CASES,
    FULL_TRACK_SEEDS,
    FULL_TRACK_STATUS_COLORS,
    GROWTH_TRACK_AGE_TICKS,
    GROWTH_TRACK_COLORS,
    GROWTH_TRACK_REDSHIFT_LIMITS,
)
from src.datasets import V3_SOURCES

from src.internal.compatibility.v7_scholtz import (
    parse_full_table_membership,
    validate_full_table_selection,
)


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw"
TABLES = ROOT / "results/v3/tables"


class V3ScientificClaimTests(unittest.TestCase):
    def test_full_growth_track_assumption_grid_matches_historical_v1(self) -> None:
        self.assertEqual(len(FULL_TRACK_SEEDS), 3)
        self.assertEqual([item[0] for item in FULL_TRACK_FEDD_STYLES], [0.3, 1.0, 2.0])
        self.assertEqual([item[2] for item in FULL_TRACK_SEEDS], ["#2F6B9A", "#3A8B5C", "#B66A1E"])
        self.assertEqual(
            [item[1] for item in FULL_TRACK_FEDD_STYLES],
            [(0, (5, 3)), "-", (0, (1, 1))],
        )
        self.assertEqual(len(FULL_TRACK_EPSILON_CASES), 4)
        self.assertEqual([item[0] for item in FULL_TRACK_MERGER_CASES], [1.0, 2.0])
        self.assertEqual(FULL_TRACK_CURVE_COUNT, 72)
        self.assertEqual(GROWTH_TRACK_REDSHIFT_LIMITS, (13.0, 3.0))
        self.assertEqual(GROWTH_TRACK_AGE_TICKS.tolist(), list(range(13, 2, -1)))
        self.assertEqual(GROWTH_TRACK_COLORS["broad_line_agn"], "#7B2CBF")
        self.assertEqual(FULL_TRACK_STATUS_COLORS["narrow_line_agn_candidate"], "#176B87")
        self.assertEqual(FULL_TRACK_STATUS_COLORS["xray_agn_candidate"], "#777777")

    def test_v3_contains_only_declared_jwst_identified_sources(self) -> None:
        objects = pd.read_csv(ROOT / "data/processed/v3/v3_accreting_objects.csv")
        self.assertEqual(set(objects["source_key"]), set(V3_SOURCES))
        self.assertNotIn("luminous_quasar_comparison", set(objects["object_class"]))

    def test_canonical_mass_additions_follow_version_scope(self) -> None:
        v1 = pd.read_csv(ROOT / "data/processed/v1/v1_accreting_objects.csv")
        v2 = pd.read_csv(ROOT / "data/processed/v2/v2_accreting_objects.csv")
        v3 = pd.read_csv(ROOT / "data/processed/v3/v3_accreting_objects.csv")
        self.assertEqual(len(set(v2["physical_object_id"]) - set(v1["physical_object_id"])), 188)
        new_source_keys = {
            "greene24_uncover_blagn", "kocevski25_lrd_blagn",
            "skyfire26_ceers_blagn", "larson23_ceers1019",
            "killi24_j0647_lrd_blagn", "ubler24_zs7_offset_blagn",
            "baccus26_nirspec_blagn", "fei26_glimpse_blagn",
        }
        additions = v2[v2["source_key"].isin(new_source_keys)]
        self.assertEqual(len(additions), 99)
        self.assertTrue(additions["growth_ranking_eligible_flag"].astype(bool).all())
        expanded = v2[v2["source_key"].isin({
            "baccus26_nirspec_blagn", "fei26_glimpse_blagn",
        })]
        self.assertEqual(
            expanded.groupby("source_key").size().to_dict(),
            {"baccus26_nirspec_blagn": 49, "fei26_glimpse_blagn": 10},
        )
        baccus = expanded[expanded["source_key"].eq("baccus26_nirspec_blagn")]
        self.assertFalse(baccus["object_id"].str.startswith(("GLIMPSE", "MACS0416", "MACS1149")).any())
        fei = expanded[expanded["source_key"].eq("fei26_glimpse_blagn")]
        self.assertTrue(fei["lensing_status"].eq("lensed").all())
        self.assertTrue(fei["lensing_mass_correction_status"].eq("applied").all())
        self.assertEqual(fei["evidence_status"].value_counts().to_dict(), {"secure": 8, "candidate": 2})
        self.assertNotIn("maiolino24_gnz11_agn", set(v2["source_key"]))
        gnz11 = v3[v3["source_key"].eq("maiolino24_gnz11_agn")].squeeze()
        self.assertEqual(gnz11["object_class"], "high_ionization_line_candidate")
        self.assertFalse(bool(gnz11["primary_mass_comparison_flag"]))

    def test_heterogeneous_expansion_adds_only_new_unplottable_v3_objects(self) -> None:
        measurements = pd.read_csv(
            ROOT / "data/processed/v3/v3_accreting_measurements.csv", low_memory=False,
        )
        expected = {
            "chisholm24_gn42437_nev": 1, "tang25_high_ionization": 3,
            "mazzolari24_ceers_nlagn": 25, "meow26_miri_agn": 12,
            "lyu24_smiles_miri_agn": 19, "napolitano25_ghz9": 1,
            "zhang25_narrow_line_lrds": 5, "chavezortiz26_ghz2": 1,
            "mascia26_compact_blue_ble": 8,
            "treiber25_uncover_uv_emitters": 2, "naidu26_mom_bhstar1": 1,
        }
        added = measurements[measurements["source_key"].isin(expected)]
        self.assertEqual(added.groupby("source_key").size().to_dict(), expected)
        self.assertEqual(len(added), 78)
        self.assertTrue(added["log_mbh_msun_std"].isna().all())
        self.assertFalse(added["growth_ranking_eligible_flag"].astype(bool).any())
        self.assertNotIn("GS_3073", set(added["object_id"]))

    def test_final_v3_completion_adds_new_jwst_objects_and_resolves_nx10835(self) -> None:
        measurements = pd.read_csv(
            ROOT / "data/processed/v3/v3_accreting_measurements.csv", low_memory=False,
        )
        objects = pd.read_csv(
            ROOT / "data/processed/v3/v3_accreting_objects.csv", low_memory=False,
        )
        expected = {
            "zhuang25_nexus_wfss": 15,
            "lin25_cosmos3d_blagn": 13,
            "napolitano25_seven_wonders": 2,
        }
        added = measurements[measurements["source_key"].isin(expected)]
        self.assertEqual(added.groupby("source_key").size().to_dict(), expected)
        self.assertEqual(
            added.groupby("source_key")["log_mbh_msun_std"].count().to_dict(),
            {
                "zhuang25_nexus_wfss": 12,
                "lin25_cosmos3d_blagn": 13,
                "napolitano25_seven_wonders": 0,
            },
        )
        self.assertEqual((len(measurements), len(objects)), (350, 340))
        self.assertEqual(int(objects["growth_ranking_eligible_flag"].astype(bool).sum()), 237)
        nx = measurements[measurements["physical_object_id"].eq("HZA-NEXUS-OBS3-5105-10835")]
        self.assertEqual(len(nx), 2)
        self.assertEqual(int(nx["preferred_measurement_flag"].astype(bool).sum()), 1)
        self.assertEqual(
            nx.loc[nx["preferred_measurement_flag"].astype(bool), "source_key"].item(),
            "zhuang25_nexus_wfss",
        )

    def test_recent_addition_metadata_reaches_canonical_and_long_form_tables(self) -> None:
        measurements = pd.read_csv(ROOT / "data/processed/v3/v3_accreting_measurements.csv")
        observables = pd.read_csv(ROOT / "data/processed/v3/v3_source_observables.csv")
        rows = measurements.set_index("measurement_id")
        self.assertEqual(
            rows.loc["RUBIESEGS61496_kocevski25", "mstar_method"],
            "CIGALE v2022.1 hybrid galaxy+AGN SED fit",
        )
        self.assertEqual(
            rows.loc["CEERS1019_larson23", "mstar_method"],
            "NIRCam+MIRI photometric SED fit",
        )
        self.assertAlmostEqual(rows.loc["ZS7_ubler24", "edd_ratio_std"], 0.14)
        self.assertAlmostEqual(rows.loc["ZS7_ubler24", "log_lbol_err_plus_std"], 0.1)
        names = set(observables.loc[
            observables["measurement_id"].eq("ZS7_ubler24"), "observable_name"
        ])
        self.assertEqual(names, {"log_mbh", "hbeta_broad_fwhm", "log_lbol", "edd_ratio"})

    def test_published_values_have_method_metadata(self) -> None:
        measurements = pd.read_csv(
            ROOT / "data/processed/v3/v3_accreting_measurements.csv",
            low_memory=False,
        )
        for value_field, method_field in [
            ("log_mstar_msun_std", "mstar_method"),
            ("log_lbol_erg_s_std", "lbol_method"),
            ("edd_ratio_std", "edd_ratio_method"),
        ]:
            missing = measurements[value_field].notna() & measurements[method_field].isna()
            self.assertFalse(
                missing.any(),
                f"{method_field} missing for {missing.sum()} rows with {value_field}",
            )

    def test_scholtz_full_table_and_admitted_redshift_cut(self) -> None:
        full_table_path = RAW / "scholtz25_jades_table_sample_full.tex"
        full = parse_full_table_membership(full_table_path)
        admitted = pd.concat(
            [
                pd.read_csv(RAW / "scholtz25_jades_narrow_line_agn_zge4.csv"),
                pd.read_csv(RAW / "scholtz25_jades_narrow_line_agn_correction.csv"),
            ],
            ignore_index=True,
        )

        self.assertEqual(len(full), 41)
        self.assertEqual(int(full["redshift"].ge(4).sum()), 21)
        validate_full_table_selection(full_table_path, admitted)

    def test_jades_99671_has_no_invented_black_hole_mass(self) -> None:
        measurements = pd.read_csv(
            ROOT / "data/processed/v3/v3_accreting_measurements.csv",
            low_memory=False,
        )
        row = measurements.loc[
            measurements["object_id"].eq("JADES-NS-GS00099671")
        ].squeeze()

        self.assertEqual(row["source_key"], "scholtz25_jades_narrow_line_agn")
        self.assertTrue(pd.isna(row["log_mbh_msun_std"]))
        self.assertEqual(row["mass_comparability_group"], "no_numeric_mass")
        self.assertFalse(bool(row["growth_ranking_eligible_flag"]))

    def test_ghz2_revised_context_mass_remains_conditional(self) -> None:
        measurements = pd.read_csv(
            ROOT / "data/processed/v3/v3_accreting_measurements.csv", low_memory=False,
        )
        row = measurements.loc[measurements["object_id"].eq("GHZ2")].squeeze()
        self.assertTrue(pd.isna(row["log_mbh_msun_std"]))
        self.assertFalse(bool(row["growth_ranking_eligible_flag"]))
        observables = pd.read_csv(ROOT / "data/processed/v3/v3_source_observables.csv")
        value = observables.loc[
            observables["observable_id"].eq("GHZ2_chavezortiz26__log_mbh_context"), "value"
        ].squeeze()
        self.assertAlmostEqual(float(value), 7.20)

    def test_jwst_objects_lead_navigation_rankings(self) -> None:
        point = pd.read_csv(TABLES / "v3_object_point_ranking.csv")
        uncertainty = pd.read_csv(TABLES / "v3_object_uncertainty_ranking.csv")

        point_first = point.nsmallest(1, "rank_global_navigation").iloc[0]
        uncertainty_first = uncertainty.nsmallest(
            1, "rank_uncertainty_global_navigation"
        ).iloc[0]
        self.assertEqual(point_first["object_id"], "UNCOVER-20466")
        self.assertEqual(uncertainty_first["object_id"], "UNCOVER-20466")

    def test_no_error_masses_are_not_presented_as_posteriors(self) -> None:
        uncertainty = pd.read_csv(TABLES / "v3_object_uncertainty_ranking.csv")
        point_only = uncertainty["mbh_uncertainty_mode"].eq(
            "point_estimate_no_reported_mbh_error"
        )
        self.assertEqual(int(point_only.sum()), 12)
        self.assertEqual(
            set(uncertainty.loc[point_only, "source_key"]),
            {"zhuang25_nexus_wfss"},
        )
        self.assertFalse(
            uncertainty.loc[point_only, "reported_mass_errors_sampled"].astype(bool).any()
        )
        self.assertTrue(
            uncertainty.loc[point_only, "prob_required_fedd_seed1e2_gt_1"].isna().all()
        )
        self.assertTrue(
            uncertainty.loc[point_only, "rank_uncertainty_global_navigation"].isna().all()
        )

    def test_primary_alternate_and_complete_product_counts(self) -> None:
        measurement = pd.read_csv(TABLES / "v3_measurement_point_ranking.csv")
        objects = pd.read_csv(TABLES / "v3_object_point_ranking.csv")
        alternates = pd.read_csv(TABLES / "v3_alternate_measurement_sensitivity.csv")
        followup = pd.read_csv(TABLES / "v3_followup_priority.csv")
        caveats = pd.read_csv(TABLES / "v3_source_caveat_summary.csv")
        coverage = pd.read_csv(TABLES / "v3_all_object_visual_coverage.csv")

        self.assertEqual(int(measurement["primary_growth_ranking_flag"].sum()), 234)
        self.assertEqual(int(objects["primary_growth_ranking_flag"].sum()), 227)
        self.assertEqual(len(alternates), 7)
        self.assertEqual((len(followup), len(caveats), len(coverage)), (340, 32, 680))
        self.assertEqual(
            coverage.groupby("product_kind").size().to_dict(),
            {"fedd_mass_map": 340, "seedredshift_mass_map": 340},
        )

    def test_jades_8083_identity_merge_retains_one_preferred_measurement(self) -> None:
        measurements = pd.read_csv(
            ROOT / "data/processed/v3/v3_accreting_measurements.csv",
            low_memory=False,
        )
        rows = measurements.loc[measurements["physical_object_id"].eq("HZA-GS-8083")]

        self.assertEqual(len(rows), 2)
        self.assertEqual(int(rows["preferred_measurement_flag"].sum()), 1)
        self.assertEqual(
            set(rows["source_key"]),
            {"juodzbalis25_jades_blagn", "scholtz25_jades_narrow_line_agn"},
        )


if __name__ == "__main__":
    unittest.main()
