"""Regression checks for the source-isolated Taylor CEERS/RUBIES expansion."""

from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path

import pandas as pd
from pandas.testing import assert_frame_equal


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.v3_catalogue import (
    TAYLOR_MASS_METHOD,
    TAYLOR_PAPER_VERSION,
    TAYLOR_SOURCE_KEY,
    build_v3_catalogues,
    standardize_taylor,
    validate_taylor_raw,
)


TAYLOR_RAW_PATH = REPO_ROOT / "data" / "raw" / "taylor24_ceers_rubies_blagn_table1.csv"
V1_RAW_PATH = REPO_ROOT / "data" / "raw" / "v1_raw.csv"
V1_PROCESSED_PATH = REPO_ROOT / "data" / "processed" / "v1_processed.csv"
LINK_PATH = REPO_ROOT / "data" / "crossmatch" / "v3_measurement_object_links.csv"
MEASUREMENT_OUTPUT_PATH = REPO_ROOT / "data" / "processed" / "v3_blagn_measurements.csv"
OBJECT_OUTPUT_PATH = REPO_ROOT / "data" / "processed" / "v3_blagn_objects.csv"

V1_RAW_SHA256 = "56644ea68912ea136149509202df5f618dae084e20a58d457d7b798ea79ffc7c"
V1_PROCESSED_SHA256 = "c8bdff0c1d2af56475850402f3a0548d865131286d7413bbcc06755d7d1d0bb8"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TaylorSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = pd.read_csv(TAYLOR_RAW_PATH)
        cls.links = pd.read_csv(LINK_PATH)
        cls.validated = validate_taylor_raw(cls.raw)
        cls.filtered = standardize_taylor(cls.raw)

    def test_authoritative_table_counts(self) -> None:
        self.assertEqual(len(self.validated), 63)
        taylor_ids = set(self.validated["measurement_id"])
        source_links = self.links[self.links["measurement_id"].isin(taylor_ids)]
        self.assertEqual(source_links["physical_object_id"].nunique(), 62)
        self.assertEqual(int(self.validated["lrd_flag"].sum()), 21)
        self.assertEqual(int(self.validated["halpha_absorption_fit_flag"].sum()), 4)

    def test_processing_layer_applies_redshift_filter(self) -> None:
        self.assertEqual(len(self.filtered), 37)
        self.assertTrue(self.filtered["redshift"].ge(4.0).all())
        filtered_ids = set(self.filtered["measurement_id"])
        filtered_links = self.links[self.links["measurement_id"].isin(filtered_ids)]
        self.assertEqual(filtered_links["physical_object_id"].nunique(), 36)
        self.assertEqual(int(self.filtered["lrd_flag"].sum()), 17)
        self.assertEqual(int(self.filtered["halpha_absorption_fit_flag"].sum()), 3)

    def test_duplicate_measurements_link_to_one_object(self) -> None:
        duplicate = self.links[
            self.links["measurement_id"].isin(
                ["CEERS2782_taylor24", "RUBIESEGS50052_taylor24"]
            )
        ].set_index("measurement_id")
        self.assertEqual(duplicate["physical_object_id"].nunique(), 1)
        self.assertEqual(duplicate.iloc[0]["physical_object_id"], "HZA-CEERS-2782")
        self.assertEqual(int(duplicate.loc["CEERS2782_taylor24", "preferred_measurement_flag"]), 0)
        self.assertEqual(int(duplicate.loc["RUBIESEGS50052_taylor24", "preferred_measurement_flag"]), 1)

    def test_published_values_are_preserved(self) -> None:
        rows = self.validated.set_index("object_id")
        low_z = rows.loc["RUBIES-UDS-44043"]
        self.assertAlmostEqual(low_z["redshift"], 3.499)
        self.assertAlmostEqual(low_z["ra_deg"], 34.241817)
        self.assertAlmostEqual(low_z["halpha_flux_total_1e18_erg_s_cm2"], 31.53)
        self.assertAlmostEqual(low_z["halpha_flux_broad_1e18_erg_s_cm2"], 23.25)
        self.assertEqual(int(low_z["halpha_broad_fwhm_km_s"]), 2728)
        self.assertAlmostEqual(low_z["log_mbh_msun"], 7.66)

        duplicate = rows.loc["RUBIES-EGS-50052"]
        self.assertAlmostEqual(duplicate["redshift"], 5.240)
        self.assertAlmostEqual(duplicate["halpha_flux_total_1e18_erg_s_cm2"], 37.85)
        self.assertEqual(int(duplicate["halpha_broad_fwhm_km_s"]), 2129)
        self.assertAlmostEqual(duplicate["log_mbh_msun"], 7.58)

    def test_unpublished_optional_quantities_remain_missing(self) -> None:
        raw_fields = [
            "log_mstar_msun",
            "log_lbol_erg_s",
            "edd_ratio_reported",
        ]
        self.assertTrue(self.validated[raw_fields].isna().all().all())
        processed_fields = [
            "log_mstar_msun_std",
            "log_lbol_erg_s_std",
            "edd_ratio_std",
            "edd_ratio_from_mbh_lbol",
        ]
        self.assertTrue(self.filtered[processed_fields].isna().all().all())
        self.assertTrue(self.filtered["missing_mstar_flag"].all())
        self.assertTrue(self.filtered["missing_lbol_flag"].all())
        self.assertTrue(self.filtered["missing_edd_ratio_flag"].all())

    def test_lrd_is_a_phenotype_not_an_object_class(self) -> None:
        self.assertTrue(self.validated["object_class"].eq("broad-line-agn").all())
        self.assertGreater(int(self.validated["lrd_flag"].sum()), 0)
        self.assertLess(int(self.validated["lrd_flag"].sum()), len(self.validated))

    def test_provenance_and_mass_systematic_are_explicit(self) -> None:
        self.assertTrue(self.validated["source_key"].eq(TAYLOR_SOURCE_KEY).all())
        self.assertTrue(self.validated["source_paper_version"].eq(TAYLOR_PAPER_VERSION).all())
        self.assertTrue(self.validated["source_url"].str.contains("add15b", regex=False).all())
        self.assertTrue(self.validated["source_doi"].eq("10.3847/1538-4357/add15b").all())
        self.assertTrue(self.validated["source_archive_url"].str.contains("2409.06772v2", regex=False).all())
        self.assertTrue(self.validated["source_archive_sha256"].str.len().eq(64).all())
        self.assertTrue(self.validated["extraction_date"].eq("2026-08-17").all())
        self.assertTrue(self.validated["mbh_method"].eq(TAYLOR_MASS_METHOD).all())
        self.assertTrue(self.validated["log_mbh_systematic_dex"].eq(0.5).all())
        self.assertFalse(self.validated["mbh_systematic_applied_flag"].any())


class V3ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.v1 = pd.read_csv(V1_PROCESSED_PATH)
        cls.raw = pd.read_csv(TAYLOR_RAW_PATH)
        cls.links = pd.read_csv(LINK_PATH)
        cls.measurements, cls.objects = build_v3_catalogues(cls.v1, cls.raw, cls.links)

    def test_expected_combined_counts(self) -> None:
        self.assertEqual(len(self.measurements), 60)
        self.assertEqual(self.measurements["physical_object_id"].nunique(), 59)
        self.assertEqual(len(self.objects), 59)
        self.assertEqual(int(self.objects["n_measurements"].sum()), 60)

    def test_release_metadata_maps_v1_and_v3_rows(self) -> None:
        self.assertTrue(self.measurements["catalogue_release"].eq("v3-blagn").all())
        taylor = self.measurements[self.measurements["source_key"].eq(TAYLOR_SOURCE_KEY)]
        jades = self.measurements[self.measurements["source_key"].eq("juodzbalis25_jades_blagn")]
        self.assertTrue(taylor["project_version"].eq("v3").all())
        self.assertTrue(jades["project_version"].eq("v1").all())

    def test_object_view_selects_preferred_duplicate(self) -> None:
        row = self.objects.set_index("physical_object_id").loc["HZA-CEERS-2782"]
        self.assertEqual(row["measurement_id"], "RUBIESEGS50052_taylor24")
        self.assertEqual(int(row["n_measurements"]), 2)
        self.assertIn("CEERS2782_taylor24", row["available_measurement_ids"])
        self.assertIn("RUBIESEGS50052_taylor24", row["available_measurement_ids"])

    def test_committed_outputs_match_the_deterministic_builder(self) -> None:
        committed_measurements = pd.read_csv(MEASUREMENT_OUTPUT_PATH)
        committed_objects = pd.read_csv(OBJECT_OUTPUT_PATH)
        assert_frame_equal(committed_measurements, self.measurements, check_dtype=False)
        assert_frame_equal(committed_objects, self.objects, check_dtype=False)

    def test_v1_release_anchors_are_byte_identical(self) -> None:
        self.assertEqual(sha256(V1_RAW_PATH), V1_RAW_SHA256)
        self.assertEqual(sha256(V1_PROCESSED_PATH), V1_PROCESSED_SHA256)
        self.assertEqual(len(self.v1), 23)
        v1_in_expansion = self.measurements[
            self.measurements["source_key"].eq("juodzbalis25_jades_blagn")
        ]
        self.assertEqual(len(v1_in_expansion), 23)


if __name__ == "__main__":
    unittest.main()
