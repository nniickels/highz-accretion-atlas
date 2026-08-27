"""Regression tests for results organization and all-object grid figures."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import pandas as pd
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.generate_all_object_grid_figures import ordered_sources, scenario_sources
from scripts.verify_v7_3_results_gallery import (
    MANIFEST_PATH, verify_gallery_contract, verify_metadata,
)


class V73ResultsGalleryTests(unittest.TestCase):
    def test_every_scenario_has_all_23_objects_in_catalogue_order(self) -> None:
        for scenario, directory in scenario_sources().items():
            self.assertEqual(len(ordered_sources(directory, scenario)), 23, scenario)

    def test_seven_lossless_high_resolution_grids_exist(self) -> None:
        grids = sorted((ROOT / "results/releases/v7_3/galleries/compiled_object_grids").glob("all_objects_*.png"))
        self.assertEqual(len(grids), 7)
        for path in grids:
            with Image.open(path) as image:
                self.assertEqual(image.size, (6048, 5648), path.name)
                self.assertEqual(image.format, "PNG", path.name)
                self.assertGreater(image.width * image.height, 30_000_000)

    def test_results_inventory_is_unique_and_categorized(self) -> None:
        inventory = pd.read_csv(ROOT / "results/results_inventory.csv")
        self.assertEqual(len(inventory), 868)
        self.assertTrue(inventory["path"].is_unique)
        v1_inventory = inventory[inventory["release"].eq("v1")]
        self.assertEqual(
            int(inventory["collection"].eq("compiled_all_object_grids").sum()), 7,
        )
        self.assertEqual(
            int(v1_inventory["collection"].eq("per_object_parameter_maps").sum()), 138,
        )
        self.assertEqual(
            int(v1_inventory["collection"].eq("per_object_seed_redshift_maps").sum()), 23,
        )

    def test_manifest_and_cross_inventory_hashes_are_enforced(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text())
        verify_metadata(manifest)
        verify_gallery_contract()
        broken = {**manifest, "grid_specification": dict(manifest["grid_specification"])}
        broken["grid_specification"]["width_px"] = 1000
        with self.assertRaisesRegex(AssertionError, "metadata mismatch"):
            verify_metadata(broken)


if __name__ == "__main__":
    unittest.main()
