"""Regression tests for the Davis/THRILS v6 catalogue expansion."""

from __future__ import annotations

import hashlib
import io
import json
import sys
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.v6_catalogue import (
    THRILS_ARCHIVE_SHA256, THRILS_MASS_METHOD, THRILS_PROGRAM_ARCHIVE_SHA256,
    THRILS_SOURCE_KEY, build_v6_catalogues,
)


class V6PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = pd.read_csv(ROOT / "data/raw/davis26_thrils_blagn_table5.csv")
        cls.measurements = pd.read_csv(ROOT / "data/processed/v6/v6_blagn_measurements.csv")
        cls.objects = pd.read_csv(ROOT / "data/processed/v6/v6_blagn_objects.csv")
        cls.links = pd.read_csv(ROOT / "data/crossmatch/v6/v6_measurement_object_links.csv")
        cls.candidates = pd.read_csv(ROOT / "data/crossmatch/v6/v6_reviewed_match_candidates.csv")

    def test_authoritative_table_and_release_counts(self) -> None:
        self.assertEqual(len(self.raw), 7)
        self.assertEqual(int(self.raw["redshift"].ge(4).sum()), 6)
        self.assertEqual(len(self.measurements), 112)
        self.assertEqual(len(self.objects), 105)
        self.assertTrue(self.measurements["catalogue_release"].eq("v6-blagn").all())
        self.assertEqual(self.measurements["source_key"].value_counts()[THRILS_SOURCE_KEY], 6)

    def test_published_table_anchors_and_z_filter(self) -> None:
        indexed = self.raw.set_index("thrils_id")
        self.assertEqual(indexed.loc[101567, "log_mbh_msun"], 6.55)
        self.assertEqual(indexed.loc[101567, "log_mbh_err"], 0.17)
        self.assertEqual(indexed.loc[40467, "halpha_broad_fwhm_km_s"], 1696)
        self.assertEqual(indexed.loc[40467, "halpha_broad_fwhm_err"], 51)
        self.assertIn(46155, indexed.index)
        self.assertNotIn("THRILS46155_davis26", set(self.measurements["measurement_id"]))

    def test_no_retained_identity_overlap(self) -> None:
        self.assertTrue(self.candidates.empty)
        thrils = self.measurements[self.measurements["source_key"].eq(THRILS_SOURCE_KEY)]
        self.assertEqual(thrils["physical_object_id"].nunique(), 6)
        self.assertTrue(thrils["match_reference"].str.contains("no v5 candidate").all())

    def test_known_below_cut_source_history_is_preserved(self) -> None:
        row = self.raw.set_index("thrils_id").loc[46155]
        self.assertLess(row["redshift"], 4)
        self.assertIn("duplicate_measurement_of_rubies_egs_50812", row["source_caveat_tags"])

    def test_missing_values_are_not_inferred(self) -> None:
        thrils = self.measurements[self.measurements["source_key"].eq(THRILS_SOURCE_KEY)]
        for field in ["log_mstar_msun_std", "log_lbol_erg_s_std", "edd_ratio_std", "lrd_flag"]:
            self.assertTrue(thrils[field].isna().all(), field)
        self.assertEqual(thrils["halpha_broad_fwhm_km_s"].notna().sum(), 1)
        self.assertTrue(thrils["halpha_absorption_fit_flag"].isna().all())
        self.assertFalse(thrils["missing_optional_fields"].str.contains("mbh").any())

    def test_mass_systematic_and_provenance_are_separate(self) -> None:
        thrils = self.measurements[self.measurements["source_key"].eq(THRILS_SOURCE_KEY)]
        self.assertTrue(thrils["mbh_method"].eq(THRILS_MASS_METHOD).all())
        self.assertTrue(thrils["log_mbh_systematic_dex"].eq(0.5).all())
        applied = thrils["mbh_systematic_applied_flag"].map(
            lambda value: str(value).strip().lower() in {"1", "true", "yes", "y"}
        )
        self.assertFalse(applied.any())
        self.assertTrue(thrils["source_archive_sha256"].eq(THRILS_ARCHIVE_SHA256).all())
        self.assertTrue(thrils["coordinate_source_archive_sha256"].eq(THRILS_PROGRAM_ARCHIVE_SHA256).all())
        self.assertTrue(thrils["source_table"].str.contains("Appendix Table 5").all())

    def test_taxonomy_and_default_measurements(self) -> None:
        thrils = self.measurements[self.measurements["source_key"].eq(THRILS_SOURCE_KEY)]
        self.assertTrue(thrils["object_class"].eq("broad-line-agn").all())
        self.assertTrue(thrils["spectroscopic_type"].eq("type1_broad_line").all())
        self.assertTrue(thrils["primary_growth_ranking_flag"].astype(bool).all())
        self.assertTrue(thrils["phenotype_tags"].fillna("").eq("").all())
        counts = self.links.groupby("physical_object_id")["preferred_measurement_flag"].sum()
        self.assertTrue(counts.eq(1).all())

    def test_rebuild_is_exact_for_committed_catalogues(self) -> None:
        outputs = build_v6_catalogues(
            pd.read_csv(ROOT / "data/processed/v5/v5_blagn_measurements.csv"), self.raw,
        )
        expected = [self.measurements, self.objects, self.links]
        for actual, committed in zip(outputs[:3], expected, strict=True):
            round_tripped = pd.read_csv(io.StringIO(actual.to_csv(index=False)))
            pd.testing.assert_frame_equal(round_tripped, committed, check_dtype=False)

    def test_v5_manifest_anchors_remain_unchanged(self) -> None:
        manifest = json.loads((ROOT / "releases/v5-manifest.json").read_text())
        entries = manifest.get("artifacts", manifest.get("files", {}))
        pairs = entries.items() if isinstance(entries, dict) else (
            (entry["path"], entry["sha256"]) for entry in entries
        )
        for path_value, digest in pairs:
            self.assertEqual(hashlib.sha256((ROOT / path_value).read_bytes()).hexdigest(), digest)


if __name__ == "__main__":
    unittest.main()
