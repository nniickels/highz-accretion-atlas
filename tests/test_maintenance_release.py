"""Regression tests for v4.0.1 reproducibility and metadata infrastructure."""

from __future__ import annotations

import contextlib
import io
import json
import sys
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.generate_v2_uncertainty_rankings import verify_outputs
from scripts.reproduction import assert_frames_semantically_equal
from scripts.verify_v4_release import MANIFEST_PATH, verify_manifest_hashes
from src.mass_systematics import load_mass_method_registry, validate_catalogue_method_coverage


class MaintenanceReleaseTests(unittest.TestCase):
    def test_manifest_hashes_match_committed_release_artifacts(self) -> None:
        verify_manifest_hashes(json.loads(MANIFEST_PATH.read_text()))

    def test_every_v4_source_method_pair_is_registered(self) -> None:
        catalogue = pd.read_csv(ROOT / "data/processed/v4_blagn_measurements.csv")
        registry = load_mass_method_registry(ROOT / "data/mass_method_registry.csv")
        validate_catalogue_method_coverage(catalogue, registry)
        jades_halpha = registry.set_index(["source_key", "mbh_method"]).loc[
            ("juodzbalis25_jades_blagn", "single-epoch-virial-halpha")
        ]
        self.assertEqual(jades_halpha["calibration_tag"], "reines-volonteri2015-halpha")
        self.assertAlmostEqual(jades_halpha["reported_systematic_dex"], 0.3)
        jades_hbeta = registry.set_index(["source_key", "mbh_method"]).loc[
            ("juodzbalis25_jades_blagn", "single-epoch-virial-hbeta")
        ]
        self.assertTrue(pd.isna(jades_hbeta["reported_systematic_dex"]))

    def test_in_memory_v2_verifier_does_not_claim_to_write_files(self) -> None:
        # Existing pipeline tests exercise the detailed verifier.  This test
        # guards only its user-facing verb: verification is not file output.
        source = Path(ROOT / "scripts/generate_v2_uncertainty_rankings.py").read_text()
        verifier = source[source.index("def verify_outputs"):source.index("def build_outputs", source.index("def verify_outputs"))]
        self.assertNotIn("Wrote uncertainty", verifier)
        self.assertIn("Verified uncertainty products in memory", verifier)

    def test_reproduction_comparison_allows_only_tiny_float_variation(self) -> None:
        expected = pd.DataFrame({"id": ["a", "b"], "value": [0.010434002921364333, 2.0]})
        final_bit_variant = expected.copy()
        final_bit_variant.loc[0, "value"] = 0.010434002921364332
        assert_frames_semantically_equal(expected, final_bit_variant, label="platform variant")

        meaningful_change = expected.copy()
        meaningful_change.loc[0, "value"] += 1e-6
        with self.assertRaisesRegex(AssertionError, "column 'value' differs"):
            assert_frames_semantically_equal(expected, meaningful_change, label="bad numeric change")

    def test_reproduction_comparison_scopes_coordinate_tolerance(self) -> None:
        expected = pd.DataFrame({"separation_arcsec": [0.056339745988412]})
        linux_x86_variant = pd.DataFrame({"separation_arcsec": [0.0562558446075508]})
        assert_frames_semantically_equal(expected, linux_x86_variant, label="platform variant")

        material_coordinate_change = pd.DataFrame({"separation_arcsec": [0.056139745988412]})
        with self.assertRaisesRegex(AssertionError, "column 'separation_arcsec' differs"):
            assert_frames_semantically_equal(
                expected, material_coordinate_change, label="bad coordinate change",
            )

    def test_reproduction_comparison_keeps_text_and_order_exact(self) -> None:
        expected = pd.DataFrame({"id": ["a", "b"], "value": [1.0, 2.0]})
        changed_text = expected.copy()
        changed_text.loc[1, "id"] = "B"
        with self.assertRaisesRegex(AssertionError, "column 'id' differs"):
            assert_frames_semantically_equal(expected, changed_text, label="bad text change")

        with self.assertRaisesRegex(AssertionError, "column order or membership differs"):
            assert_frames_semantically_equal(expected, expected[["value", "id"]])


if __name__ == "__main__":
    unittest.main()
