"""Regression tests for v4 source ingestion and identity handling."""

from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.process_v4_blagn import build_outputs
from scripts.reproduction import assert_csv_reproduction
from src.identity import (
    apply_reviewed_identity_overrides, candidate_matches, cross_source_candidate_matches,
    stable_object_id,
)
from src.v4_catalogue import ASPIRE_SOURCE_KEY, MASS_METHOD, MATTHEE_SOURCE_KEY, validate_source_raw


RAW_MATTHEE = ROOT / "data/raw/matthee23_eiger_fresco_blagn_tables1_3.csv"
RAW_ASPIRE = ROOT / "data/raw/lin24_aspire_blagn_tables1_3.csv"
V3_MEASUREMENTS = ROOT / "data/processed/v3/v3_blagn_measurements.csv"
V3_OBJECTS = ROOT / "data/processed/v3/v3_blagn_objects.csv"
V3_MEASUREMENTS_SHA256 = "7df69c0a0c18631ebbe56a17a4453316bee86e7f0631dd13bedfa70c1d2e1b76"
V3_OBJECTS_SHA256 = "5c67d8a8cdf7250027c14f5fff7891a7e361b0d6c5ed851a0b322443713e2126"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class V4CatalogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.matthee = validate_source_raw(pd.read_csv(RAW_MATTHEE), MATTHEE_SOURCE_KEY)
        cls.aspire = validate_source_raw(pd.read_csv(RAW_ASPIRE), ASPIRE_SOURCE_KEY)
        cls.outputs = build_outputs()
        cls.measurements = cls.outputs["measurements"]
        cls.objects = cls.outputs["objects"]

    def test_authoritative_source_counts_and_markers(self) -> None:
        self.assertEqual(len(self.matthee), 20)
        self.assertEqual(len(self.aspire), 16)
        self.assertEqual(int(self.matthee["lrd_flag"].sum()), 20)
        self.assertEqual(int(self.aspire["lrd_flag"].sum()), 16)
        self.assertEqual(int(self.matthee["halpha_absorption_fit_flag"].sum()), 2)
        self.assertEqual(int(self.aspire["halpha_absorption_fit_flag"].sum()), 3)

    def test_exact_published_anchor_values(self) -> None:
        matthee = self.matthee.set_index("object_id").loc["GOODS-N-9771"]
        self.assertAlmostEqual(matthee["redshift"], 5.538)
        self.assertAlmostEqual(matthee["halpha_lum_broad_1e42"], 44.7)
        self.assertEqual(int(matthee["halpha_broad_fwhm_km_s"]), 3739)
        self.assertAlmostEqual(matthee["log_mbh_msun"], 8.55)
        aspire = self.aspire.set_index("object_id").loc["J0923P0402-BHAE-1"]
        self.assertAlmostEqual(aspire["redshift"], 4.8688)
        self.assertAlmostEqual(aspire["halpha_lum_total_1e42"], 21.63)
        self.assertAlmostEqual(aspire["log_lbol_erg_s"], 45.55)

    def test_v4_counts_and_release_metadata(self) -> None:
        self.assertEqual(len(self.measurements), 96)
        self.assertEqual(len(self.objects), 94)
        self.assertEqual(self.measurements["physical_object_id"].nunique(), 94)
        self.assertTrue(self.measurements["catalogue_release"].eq("v4-blagn").all())
        self.assertTrue(self.objects["catalogue_release"].eq("v4-blagn").all())

    def test_crosspaper_duplicate_is_linked_without_deletion(self) -> None:
        rows = self.measurements[self.measurements["physical_object_id"].eq("HZA-GS-204851")]
        self.assertEqual(set(rows["measurement_id"]), {"GS204851_juodzbalis25", "GOODSS13971_matthee23"})
        self.assertEqual(int(rows["preferred_measurement_flag"].sum()), 1)
        self.assertTrue(rows.set_index("measurement_id").loc["GS204851_juodzbalis25", "preferred_measurement_flag"])
        candidate = self.outputs["candidates"].iloc[0]
        self.assertLess(candidate["separation_arcsec"], 0.03)
        self.assertLess(candidate["redshift_delta"], 0.002)
        self.assertEqual(candidate["decision"], "accepted")
        self.assertEqual(candidate["match_scope"], "prior_release")

    def test_existing_taylor_duplicate_and_ids_remain_stable(self) -> None:
        rows = self.measurements[self.measurements["physical_object_id"].eq("HZA-CEERS-2782")]
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows.loc[rows["preferred_measurement_flag"], "measurement_id"].iloc[0], "RUBIESEGS50052_taylor24")

    def test_lrd_is_phenotype_and_object_level_aggregation(self) -> None:
        new = self.measurements[self.measurements["source_key"].isin([MATTHEE_SOURCE_KEY, ASPIRE_SOURCE_KEY])]
        self.assertTrue(new["object_class"].eq("broad-line-agn").all())
        self.assertTrue(new["lrd_flag"].astype(bool).all())
        duplicate = self.objects.set_index("physical_object_id").loc["HZA-GS-204851"]
        self.assertTrue(bool(duplicate["lrd_flag"]))
        self.assertIn("GOODSS13971_matthee23", duplicate["lrd_evidence_measurement_ids"])
        self.assertEqual(duplicate["lrd_evidence_source_keys"], MATTHEE_SOURCE_KEY)
        self.assertTrue(pd.isna(duplicate["preferred_measurement_lrd_flag"]))

    def test_optional_fields_and_mass_systematics(self) -> None:
        new = self.measurements[self.measurements["source_key"].isin([MATTHEE_SOURCE_KEY, ASPIRE_SOURCE_KEY])]
        self.assertTrue(new["log_mstar_msun_std"].isna().all())
        self.assertTrue(new["edd_ratio_std"].isna().all())
        self.assertTrue(new["mbh_method"].eq(MASS_METHOD).all())
        self.assertTrue(new["log_mbh_systematic_dex"].eq(0.5).all())
        self.assertFalse(new["mbh_systematic_applied_flag"].astype(bool).any())
        self.assertTrue(new["edd_ratio_from_mbh_lbol"].notna().all())

    def test_committed_products_match_builder(self) -> None:
        for name, path in {
            "measurements": ROOT / "data/processed/v4/v4_blagn_measurements.csv",
            "objects": ROOT / "data/processed/v4/v4_blagn_objects.csv",
            "links": ROOT / "data/crossmatch/v4/v4_measurement_object_links.csv",
            "aliases": ROOT / "data/crossmatch/v4/v4_object_aliases.csv",
            "candidates": ROOT / "data/crossmatch/v4/v4_reviewed_match_candidates.csv",
        }.items():
            assert_csv_reproduction(path, self.outputs[name])

    def test_v3_catalogues_are_byte_identical(self) -> None:
        self.assertEqual(sha256(V3_MEASUREMENTS), V3_MEASUREMENTS_SHA256)
        self.assertEqual(sha256(V3_OBJECTS), V3_OBJECTS_SHA256)

    def test_ambiguous_candidate_helper_rejects_silent_choice(self) -> None:
        new = pd.DataFrame([{"measurement_id": "new", "ra_deg": 10.0, "dec_deg": 10.0, "redshift": 5.0}])
        refs = pd.DataFrame([
            {"measurement_id": "a", "object_id": "a", "physical_object_id": "HZA-A", "ra_deg": 10.0, "dec_deg": 10.0, "redshift": 5.0},
            {"measurement_id": "b", "object_id": "b", "physical_object_id": "HZA-B", "ra_deg": 10.00001, "dec_deg": 10.0, "redshift": 5.0},
        ])
        self.assertEqual(len(candidate_matches(new, refs)), 2)

    def test_same_release_sources_are_pairwise_checked(self) -> None:
        rows = pd.DataFrame([
            {"measurement_id": "left", "object_id": "L", "source_key": "one", "ra_deg": 10.0, "dec_deg": 10.0, "redshift": 5.0},
            {"measurement_id": "right", "object_id": "R", "source_key": "two", "ra_deg": 10.00001, "dec_deg": 10.0, "redshift": 5.001},
        ])
        candidates = cross_source_candidate_matches(rows)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates.iloc[0]["match_scope"], "same_release_cross_source")

    def test_candidate_requires_explicit_review_decision(self) -> None:
        candidates = self.outputs["candidates"].drop(columns=[
            "decision", "physical_object_id", "review_basis", "review_reference", "review_date",
        ])
        empty_registry = pd.DataFrame(columns=[
            "measurement_id", "candidate_measurement_id", "decision", "physical_object_id",
            "review_basis", "review_reference", "review_date", "match_origin",
        ])
        with self.assertRaisesRegex(ValueError, "Unreviewed identity candidates"):
            apply_reviewed_identity_overrides(candidates, empty_registry)

    def test_stable_id_collision_is_namespaced_or_rejected(self) -> None:
        self.assertEqual(stable_object_id("same label"), "HZA-SAME-LABEL")
        self.assertEqual(
            stable_object_id("same label", source_key="paper_b", reserved_ids={"HZA-SAME-LABEL"}),
            "HZA-PAPER-B-SAME-LABEL",
        )
        with self.assertRaisesRegex(ValueError, "source_key is required"):
            stable_object_id("same label", reserved_ids={"HZA-SAME-LABEL"})

    def test_documented_manual_assertion_can_fall_outside_thresholds(self) -> None:
        candidates = pd.DataFrame(columns=[
            "measurement_id", "candidate_measurement_id", "candidate_object_id",
            "candidate_physical_object_id", "separation_arcsec", "redshift_delta",
            "match_scope", "candidate_source_key",
        ])
        registry = pd.DataFrame([{
            "measurement_id": "new", "candidate_measurement_id": "old",
            "decision": "accepted", "physical_object_id": "HZA-OLD",
            "review_basis": "published alias and imaging review",
            "review_reference": "source appendix", "review_date": "2026-08-23",
            "match_origin": "manual_assertion",
        }])
        reviewed, accepted = apply_reviewed_identity_overrides(
            candidates, registry, known_measurement_ids={"new", "old"},
        )
        self.assertEqual(len(reviewed), 1)
        self.assertEqual(accepted, {"new": "HZA-OLD", "old": "HZA-OLD"})



if __name__ == "__main__":
    unittest.main()
