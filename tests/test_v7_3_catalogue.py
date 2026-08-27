"""Regression tests for the catalogue-only v7.3 UHZ1 evidence history."""

from __future__ import annotations

import io
import json
import sys
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.process_v7_3_catalogue import OUTPUTS, build_outputs
from scripts.reproduction import assert_frames_semantically_equal
from scripts.verify_v7_3_catalogue import MANIFEST_PATH, verify_manifest_metadata
from src.v7_3_uhz1 import SOURCE_KEY, validate_uhz1_sources
from src.v7_admission import validate_v7_admission, validate_v7_observables
from src.v7_batch import validate_standardized_compatibility


class V73CatalogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.history = pd.read_csv(ROOT / "data/raw/uhz1_xray_evidence_history.csv")
        cls.miri = pd.read_csv(ROOT / "data/raw/zou26_uhz1_miri_table3.csv")
        cls.outputs = build_outputs()
        cls.measurements = cls.outputs["measurements"]
        cls.objects = cls.outputs["objects"]
        cls.uhz1 = cls.measurements[cls.measurements["source_key"].eq(SOURCE_KEY)]

    def test_source_history_and_miri_table_are_complete(self) -> None:
        history, miri = validate_uhz1_sources(self.history, self.miri)
        self.assertEqual(len(history), 2)
        self.assertEqual(len(miri), 9)
        self.assertEqual(set(history["evidence_status"]), {"candidate", "disputed"})

    def test_exact_release_cardinalities(self) -> None:
        self.assertEqual(len(self.measurements), 213)
        self.assertEqual(len(self.objects), 199)
        self.assertEqual(len(self.outputs["host_systems"]), 198)
        self.assertEqual(len(self.outputs["aliases"]), 255)
        self.assertTrue(self.outputs["reviewed_match_candidates"].empty)
        self.assertEqual(len(self.outputs["observables"]), 1015)

    def test_two_versions_one_object_and_latest_is_preferred(self) -> None:
        self.assertEqual(len(self.uhz1), 2)
        self.assertEqual(self.uhz1["physical_object_id"].nunique(), 1)
        preferred = self.uhz1[self.uhz1["preferred_measurement_flag"].astype(bool)]
        self.assertEqual(preferred["measurement_id"].tolist(), ["UHZ1_zou26"])
        obj = self.objects[self.objects["physical_object_id"].eq("HZA-UHZ1")].iloc[0]
        self.assertEqual(obj["evidence_status"], "disputed")
        self.assertEqual(obj["n_measurements"], 2)

    def test_no_point_mass_is_inferred_from_assumption_dependent_range(self) -> None:
        self.assertTrue(self.uhz1["log_mbh_msun_std"].isna().all())
        self.assertTrue(self.uhz1["mass_comparability_group"].eq("no_numeric_mass").all())
        self.assertFalse(self.uhz1["growth_ranking_eligible_flag"].astype(bool).any())
        observables = self.outputs["observables"]
        mass_range = observables[observables["observable_name"].str.startswith(
            "assumed_log_mbh_range"
        )]
        self.assertEqual(set(mass_range["censoring"]), {"lower_limit", "upper_limit"})

    def test_reanalysis_limits_and_original_claim_remain_auditable(self) -> None:
        observables = self.outputs["observables"]
        new = observables[observables["measurement_id"].isin(self.uhz1["measurement_id"])]
        self.assertEqual(len(new), 22)
        self.assertEqual(int(new["censoring"].eq("upper_limit").sum()), 11)
        self.assertIn("miri_f560w_flux_density", set(new["observable_name"]))
        self.assertIn("hard_xray_significance_high", set(new["observable_name"]))

    def test_frozen_v7_2_rows_are_inherited_without_scientific_overwrite(self) -> None:
        frozen = pd.read_csv(ROOT / "data/processed/v7_2_accreting_measurements.csv")
        inherited = self.measurements[self.measurements["source_key"].ne(SOURCE_KEY)]
        self.assertEqual(set(inherited["measurement_id"]), set(frozen["measurement_id"]))
        fields = ["ra_deg", "dec_deg", "redshift", "log_mbh_msun_std", "evidence_status"]
        pd.testing.assert_frame_equal(
            frozen.set_index("measurement_id")[fields].sort_index(),
            inherited.set_index("measurement_id")[fields].sort_index(),
        )

    def test_admission_and_observable_contracts(self) -> None:
        validate_v7_admission(self.measurements)
        validate_v7_admission(self.objects)
        validate_standardized_compatibility(self.measurements)
        validate_v7_observables(self.outputs["observables"], self.measurements["measurement_id"])

    def test_checked_in_products_reproduce_in_memory(self) -> None:
        for name, frame in self.outputs.items():
            expected = pd.read_csv(OUTPUTS[name])
            actual = pd.read_csv(io.StringIO(frame.to_csv(index=False)))
            assert_frames_semantically_equal(expected, actual, label=name)

    def test_manifest_metadata_and_counts_are_enforced(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text())
        verify_manifest_metadata(manifest)
        broken = {**manifest, "catalogue_counts": dict(manifest["catalogue_counts"])}
        broken["catalogue_counts"]["measurements"] = 214
        with self.assertRaisesRegex(AssertionError, "metadata mismatch"):
            verify_manifest_metadata(broken)


if __name__ == "__main__":
    unittest.main()
