"""Regression tests for complete v7.4 eligible-object growth products."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_v7_4_growth_manifest import MANIFEST_PATH
from scripts.generate_v7_4_growth_products import (
    COMPILED_CAPTIONS,
    COMPATIBILITY_PATH,
    COVERAGE_PATH,
    GALLERY_INVENTORY_PATH,
    UNAVAILABLE_PATH,
    build_class_compatibility,
    build_coverage_table,
    build_unavailable_table,
    eligible_objects,
    load_catalogue,
    verify_outputs,
)
from scripts.verify_v7_4_growth_products import verify_growth_contract, verify_metadata


class V74GrowthProductTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalogue = load_catalogue()
        cls.eligible = eligible_objects(cls.catalogue)
        cls.coverage = pd.read_csv(COVERAGE_PATH, keep_default_na=False)
        cls.unavailable = pd.read_csv(UNAVAILABLE_PATH)
        cls.compatibility = pd.read_csv(COMPATIBILITY_PATH)
        cls.gallery = pd.read_csv(GALLERY_INVENTORY_PATH, keep_default_na=False)

    def test_exact_eligible_and_unavailable_membership(self) -> None:
        self.assertEqual(len(self.eligible), 196)
        self.assertEqual(self.eligible["object_class"].value_counts().to_dict(), {
            "broad_line_agn": 112,
            "luminous_quasar_comparison": 84,
        })
        self.assertEqual(len(self.unavailable), 22)
        self.assertEqual(set(self.unavailable["physical_object_id"]), set(
            self.catalogue.loc[
                ~self.catalogue["growth_ranking_eligible_flag"].astype(bool),
                "physical_object_id",
            ]
        ))

    def test_every_eligible_object_has_three_figures(self) -> None:
        complete = self.coverage[self.coverage["growth_product_status"].eq("complete")]
        self.assertEqual(len(complete), 196)
        for column in ("parameter_map_path", "seed_redshift_map_path", "growth_track_path"):
            self.assertTrue(complete[column].map(lambda value: (ROOT / value).is_file()).all(), column)
        self.assertEqual(
            self.gallery["artifact_kind"].value_counts().to_dict(),
            {"per_object_figure": 588, "compiled_class_grid": 6},
        )
        grids = self.gallery[self.gallery["artifact_kind"].eq("compiled_class_grid")]
        self.assertTrue(grids["caption_policy"].eq("one_shared_gallery_footer").all())
        self.assertEqual(set(grids["product_kind"]), set(COMPILED_CAPTIONS))

    def test_compatibility_is_class_stratified_and_bounded(self) -> None:
        self.assertEqual(len(self.compatibility), 288)
        self.assertEqual(set(self.compatibility["object_class"]), {
            "broad_line_agn", "luminous_quasar_comparison",
        })
        self.assertTrue(self.compatibility["compatible_object_fraction"].between(0, 1).all())
        self.assertFalse(self.compatibility["demographic_inference_allowed"].astype(bool).any())

    def test_tables_rebuild_deterministically(self) -> None:
        rebuilt_coverage = build_coverage_table(self.catalogue)
        rebuilt_unavailable = build_unavailable_table(self.catalogue)
        rebuilt_compatibility = build_class_compatibility(self.eligible)
        verify_outputs(
            self.catalogue, rebuilt_coverage, rebuilt_unavailable,
            rebuilt_compatibility, self.gallery,
        )
        pd.testing.assert_frame_equal(rebuilt_coverage, self.coverage, check_dtype=False)
        pd.testing.assert_frame_equal(rebuilt_unavailable, self.unavailable, check_dtype=False)
        pd.testing.assert_frame_equal(
            rebuilt_compatibility, self.compatibility,
            check_dtype=False, check_exact=False, rtol=1e-12, atol=1e-12,
        )

    def test_manifest_and_image_contract(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text())
        verify_metadata(manifest)
        verify_growth_contract()


if __name__ == "__main__":
    unittest.main()
