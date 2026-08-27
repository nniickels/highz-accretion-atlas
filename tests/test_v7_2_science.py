"""Regression tests for the class-aware science layer on frozen v7.2."""

from __future__ import annotations

import io
import json
import sys
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.generate_v7_2_class_aware_science import OUTPUT_PATHS, build_outputs
from scripts.reproduction import assert_frames_semantically_equal
from scripts.verify_v7_2_science import MANIFEST_PATH, verify_manifest_metadata
from src.v7_2_science import DEFAULT_N_SAMPLES, DEFAULT_RANDOM_SEED


class V72ClassAwareScienceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.outputs = build_outputs(
            n_samples=DEFAULT_N_SAMPLES, random_seed=DEFAULT_RANDOM_SEED,
        )

    def test_exact_product_cardinalities(self) -> None:
        expected = {
            "measurement_point_ranking": 209,
            "object_point_ranking": 196,
            "measurement_uncertainty_ranking": 209,
            "object_uncertainty_ranking": 196,
            "class_method_summary": 36,
            "exclusion_audit": 4,
            "alternate_measurement_sensitivity": 13,
            "science_policy": 4,
        }
        self.assertEqual({name: len(frame) for name, frame in self.outputs.items()}, expected)

    def test_class_and_method_scopes_are_explicit(self) -> None:
        for name in ["measurement_point_ranking", "object_point_ranking"]:
            frame = self.outputs[name]
            self.assertIn("rank_within_object_class", frame)
            self.assertIn("rank_within_class_mass_group", frame)
            self.assertIn("rank_primary_within_class_mass_group", frame)
            self.assertTrue(frame["global_rank_policy"].eq(
                "navigation_only_no_cross_class_science_claim"
            ).all())
            self.assertFalse(frame["demographic_inference_allowed"].astype(bool).any())

    def test_statistical_and_systematic_uncertainties_stay_separate(self) -> None:
        for name in ["measurement_uncertainty_ranking", "object_uncertainty_ranking"]:
            frame = self.outputs[name]
            self.assertTrue(frame["reported_statistical_errors_sampled"].astype(bool).all())
            self.assertFalse(frame["systematic_combined_with_statistical_error"].astype(bool).any())
            for stem in ["required_fedd_seed1e2", "required_log_mseed_fedd0p3"]:
                self.assertTrue((frame[f"{stem}_p16"] <= frame[f"{stem}_p50"]).all())
                self.assertTrue((frame[f"{stem}_p50"] <= frame[f"{stem}_p84"]).all())

    def test_exclusions_are_retained_and_audited(self) -> None:
        audit = self.outputs["exclusion_audit"]
        self.assertEqual(set(audit["object_id"]), {"J0055+0146", "WISEA J0439+1634"})
        self.assertEqual(set(audit["catalogue_view"]), {"measurement", "physical_object"})
        self.assertTrue(audit["retained_in_catalogue_flag"].astype(bool).all())
        self.assertTrue(audit["excluded_from_science_rank_flag"].astype(bool).all())

    def test_policy_forbids_pooled_demographic_inference(self) -> None:
        policy = self.outputs["science_policy"].set_index("scope")
        self.assertFalse(bool(policy.loc["pooled_demographic_inference", "allowed"]))
        summary = self.outputs["class_method_summary"]
        self.assertFalse(summary["demographic_inference_allowed"].astype(bool).any())

    def test_checked_in_products_reproduce_in_memory(self) -> None:
        for name, frame in self.outputs.items():
            expected = pd.read_csv(OUTPUT_PATHS[name])
            actual = pd.read_csv(io.StringIO(frame.to_csv(index=False)))
            assert_frames_semantically_equal(expected, actual, label=name)

    def test_manifest_metadata_is_enforced(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text())
        verify_manifest_metadata(manifest)
        broken = {**manifest, "n_samples": DEFAULT_N_SAMPLES - 1}
        with self.assertRaisesRegex(AssertionError, "metadata mismatch"):
            verify_manifest_metadata(broken)


if __name__ == "__main__":
    unittest.main()
