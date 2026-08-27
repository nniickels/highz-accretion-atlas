"""Regression tests for current v7.5 class-aware science."""

from __future__ import annotations

import io
import json
import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.generate_v7_5_class_aware_science import OUTPUT_PATHS, build_outputs
from scripts.reproduction import assert_frames_semantically_equal
from scripts.verify_v7_5_science import MANIFEST_PATH, verify_manifest_metadata
from src.v7_5_science import DEFAULT_N_SAMPLES, DEFAULT_RANDOM_SEED, SCIENCE_RELEASE


class V75ScienceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.outputs = build_outputs(n_samples=DEFAULT_N_SAMPLES, random_seed=DEFAULT_RANDOM_SEED)

    def test_counts_metadata_and_policy(self) -> None:
        self.assertEqual({name: len(frame) for name, frame in self.outputs.items()}, {
            "measurement_point_ranking": 209, "object_point_ranking": 196,
            "measurement_uncertainty_ranking": 209, "object_uncertainty_ranking": 196,
            "class_method_summary": 36, "exclusion_audit": 48,
            "alternate_measurement_sensitivity": 13, "science_policy": 4,
        })
        for frame in self.outputs.values():
            self.assertTrue(frame["science_release"].eq(SCIENCE_RELEASE).all())
        policy = self.outputs["science_policy"].set_index("scope")
        self.assertFalse(bool(policy.loc["pooled_demographic_inference", "allowed"]))

    def test_catalogue_only_objects_are_explicitly_excluded(self) -> None:
        audit = self.outputs["exclusion_audit"]
        corrected = audit[audit["object_id"].eq("JADES-NS-GS00099671")]
        self.assertEqual(len(corrected), 2)
        self.assertTrue(corrected["growth_ranking_eligibility_reason"].eq("missing_numeric_mbh").all())

    def test_preferred_evidence_restores_primary_object(self) -> None:
        objects = self.outputs["object_point_ranking"]
        row = objects.set_index("physical_object_id").loc["HZA-GS-8083"]
        self.assertTrue(bool(row["primary_growth_ranking_flag"]))
        self.assertFalse(pd.isna(row["rank_primary_within_class_mass_group"]))

    def test_uncertainty_intervals_and_reproduction(self) -> None:
        for name in ["measurement_uncertainty_ranking", "object_uncertainty_ranking"]:
            frame = self.outputs[name]
            self.assertTrue((frame["required_fedd_seed1e2_p16"] <= frame["required_fedd_seed1e2_p50"]).all())
            self.assertTrue((frame["required_fedd_seed1e2_p50"] <= frame["required_fedd_seed1e2_p84"]).all())
        for name, frame in self.outputs.items():
            expected = pd.read_csv(OUTPUT_PATHS[name])
            actual = pd.read_csv(io.StringIO(frame.to_csv(index=False)))
            assert_frames_semantically_equal(expected, actual, label=name)

    def test_manifest(self) -> None:
        verify_manifest_metadata(json.loads(MANIFEST_PATH.read_text()))


if __name__ == "__main__":
    unittest.main()
