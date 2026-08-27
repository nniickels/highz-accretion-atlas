"""Regression tests for the v7.5 figures and gallery coverage."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.generate_v7_5_figures import OUTPUT_PATHS
from scripts.verify_v7_5_figures import MANIFEST_PATH, verify_figure_contract, verify_metadata


class V75FigureTests(unittest.TestCase):
    def test_high_resolution_figures_and_gallery_paths(self) -> None:
        verify_figure_contract()

    def test_exact_coverage(self) -> None:
        coverage = pd.read_csv(OUTPUT_PATHS["gallery_coverage"])
        self.assertEqual(len(coverage), 219)
        self.assertEqual(int(coverage["growth_product_status"].eq("complete_inherited_v7_4").sum()), 196)
        self.assertEqual(int(coverage["growth_product_status"].eq("unavailable").sum()), 23)

    def test_manifest(self) -> None:
        verify_metadata(json.loads(MANIFEST_PATH.read_text()))


if __name__ == "__main__":
    unittest.main()
