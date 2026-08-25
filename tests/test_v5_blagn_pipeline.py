"""Regression tests for the Harikane v5 catalogue expansion."""

from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.v5_catalogue import HARIKANE_MASS_METHOD, HARIKANE_SOURCE_KEY


class V5PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = pd.read_csv(ROOT / "data/raw/harikane23_nirspec_blagn_tables1_3.csv")
        cls.measurements = pd.read_csv(ROOT / "data/processed/v5_blagn_measurements.csv")
        cls.objects = pd.read_csv(ROOT / "data/processed/v5_blagn_objects.csv")
        cls.links = pd.read_csv(ROOT / "data/crossmatch/v5_measurement_object_links.csv")
        cls.candidates = pd.read_csv(ROOT / "data/crossmatch/v5_reviewed_match_candidates.csv")

    def test_authoritative_source_and_release_counts(self) -> None:
        self.assertEqual(len(self.raw), 10)
        self.assertEqual(len(self.measurements), 106)
        self.assertEqual(len(self.objects), 99)
        self.assertTrue(self.measurements["catalogue_release"].eq("v5-blagn").all())
        self.assertEqual(self.measurements["source_key"].value_counts()[HARIKANE_SOURCE_KEY], 10)

    def test_selection_and_published_anchors(self) -> None:
        self.assertTrue(self.raw["redshift"].between(4.015, 6.936).all())
        self.assertTrue((self.raw["halpha_broad_snr"] > 5).all())
        self.assertTrue((self.raw["delta_aic"] > 20).all())
        self.assertTrue((self.raw["halpha_broad_fwhm_km_s"] > 1000).all())
        indexed = self.raw.set_index("object_id")
        self.assertEqual(indexed.loc["CEERS-02782", "mbh_msun"], 4.2e7)
        self.assertEqual(indexed.loc["CEERS-00717", "halpha_broad_fwhm_km_s"], 6279)

    def test_reviewed_cross_source_identity(self) -> None:
        accepted = self.candidates[self.candidates["decision"].eq("accepted")]
        self.assertEqual(len(self.candidates), 6)
        self.assertEqual(accepted["measurement_id"].nunique(), 5)
        self.assertEqual(
            set(accepted["measurement_id"]),
            {"CEERS01244_harikane23", "CEERS00746_harikane23", "CEERS00672_harikane23", "CEERS02782_harikane23", "CEERS00397_harikane23"},
        )
        duplicate = self.measurements[self.measurements["physical_object_id"].eq("HZA-CEERS-2782")]
        self.assertEqual(len(duplicate), 3)
        self.assertEqual(int(duplicate["preferred_measurement_flag"].sum()), 1)

    def test_missingness_and_mass_metadata_are_not_inferred(self) -> None:
        harikane = self.measurements[self.measurements["source_key"].eq(HARIKANE_SOURCE_KEY)]
        upper_limits = harikane[harikane["log_mstar_upper_limit_msun"].notna()]
        self.assertEqual(len(upper_limits), 4)
        self.assertTrue(upper_limits["log_mstar_msun_std"].isna().all())
        self.assertTrue(harikane["log_mbh_systematic_dex"].isna().all())
        self.assertTrue(harikane["mbh_method"].eq(HARIKANE_MASS_METHOD).all())
        self.assertTrue(harikane["source_archive_sha256"].str.len().eq(64).all())
        self.assertTrue(harikane["lrd_flag"].isna().all())

    def test_taxonomy_is_orthogonal_and_growth_eligible(self) -> None:
        self.assertTrue(self.measurements["spectroscopic_type"].eq("type1_broad_line").all())
        self.assertTrue(self.measurements["object_class"].eq("broad-line-agn").all())
        self.assertTrue(self.measurements["growth_ranking_eligible_flag"].astype(bool).all())
        red = self.measurements[self.measurements["measurement_id"].eq("CEERS00746_harikane23")].iloc[0]
        self.assertIn("red_agn", red["phenotype_tags"])
        self.assertNotIn("lrd", red["phenotype_tags"])
        alternative = self.measurements[
            self.measurements["measurement_id"].eq("RUBIESEGS49140_taylor24")
        ].iloc[0]
        self.assertEqual(alternative["evidence_status"], "candidate_accreting_mbh")
        self.assertTrue(bool(alternative["growth_ranking_eligible_flag"]))

    def test_object_phenotypes_union_linked_measurements(self) -> None:
        triple = self.objects[self.objects["physical_object_id"].eq("HZA-CEERS-2782")].iloc[0]
        self.assertIn("compact_source", triple["phenotype_tags"])
        self.assertIn("CEERS02782_harikane23", triple["phenotype_evidence_measurement_ids"])
        linked = self.objects[self.objects["physical_object_id"].eq("HZA-CEERS-672")].iloc[0]
        self.assertIn("red_agn", linked["phenotype_tags"])
        self.assertIn("compact_source", linked["phenotype_tags"])

    def test_harikane_host_systematic_is_separate(self) -> None:
        harikane = self.measurements[self.measurements["source_key"].eq(HARIKANE_SOURCE_KEY)]
        self.assertTrue(harikane["log_mstar_systematic_dex"].eq(0.2).all())
        self.assertFalse(harikane["mstar_systematic_applied_flag"].astype(bool).any())

    def test_every_object_has_one_default_measurement(self) -> None:
        counts = self.links.groupby("physical_object_id")["preferred_measurement_flag"].sum()
        self.assertTrue(counts.eq(1).all())

    def test_v4_manifest_anchors_remain_unchanged(self) -> None:
        manifest = json.loads((ROOT / "releases/v4.0.1-manifest.json").read_text())
        entries = manifest.get("artifacts", manifest.get("files", {}))
        if isinstance(entries, dict):
            pairs = entries.items()
        else:
            pairs = ((entry["path"], entry["sha256"]) for entry in entries)
        checked = 0
        for path_value, digest in pairs:
            actual = hashlib.sha256((ROOT / path_value).read_bytes()).hexdigest()
            self.assertEqual(actual, digest, path_value)
            checked += 1
        self.assertEqual(checked, 18)


if __name__ == "__main__":
    unittest.main()
