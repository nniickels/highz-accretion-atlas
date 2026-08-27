"""Regression tests for the catalogue-only v7.1 XQR-30 release."""

from __future__ import annotations

import io
import json
import sys
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.process_v7_1_catalogue import OUTPUTS, build_outputs
from scripts.reproduction import assert_frames_semantically_equal
from scripts.verify_v7_1_catalogue import MANIFEST_PATH, verify_manifest_metadata
from src.v7_1_catalogue import CATALOGUE_RELEASE
from src.v7_admission import validate_v7_admission, validate_v7_observables
from src.v7_batch import validate_standardized_compatibility
from src.v7_xqr30 import SOURCE_KEY, build_xqr30_admission, validate_xqr30_sources


class V71CatalogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = pd.read_csv(ROOT / "data/raw/xqr30_mazzucchelli23_table1.csv")
        cls.coordinates = pd.read_csv(ROOT / "data/raw/xqr30_dodorico23_coordinates.csv")
        cls.outputs = build_outputs()
        cls.measurements = cls.outputs["measurements"]
        cls.xqr30 = cls.measurements[cls.measurements["source_key"].eq(SOURCE_KEY)]

    def test_complete_source_tables_and_caveats(self) -> None:
        table, coordinates = validate_xqr30_sources(self.raw, self.coordinates)
        self.assertEqual(len(table), 42)
        self.assertEqual(len(coordinates), 42)
        self.assertEqual(int(table["mgii_telluric_caveat_flag"].sum()), 7)
        self.assertEqual(int(table["civ_low_snr_caveat_flag"].sum()), 1)
        self.assertEqual(int(table["lensed_flag"].sum()), 1)

    def test_exact_release_cardinalities(self) -> None:
        self.assertEqual(len(self.measurements), 161)
        self.assertEqual(self.measurements["physical_object_id"].nunique(), 154)
        self.assertEqual(self.measurements["host_system_id"].nunique(), 153)
        self.assertEqual(len(self.outputs["objects"]), 154)
        self.assertEqual(len(self.outputs["host_systems"]), 153)
        self.assertEqual(len(self.outputs["aliases"]), 203)
        self.assertEqual(len(self.outputs["observables"]), 364)
        self.assertTrue(self.outputs["reviewed_match_candidates"].empty)
        self.assertEqual(len(self.outputs["external_literature_identity_audit"]), 23)

    def test_v7_is_inherited_without_overwriting_frozen_files(self) -> None:
        frozen = pd.read_csv(ROOT / "data/processed/v7_accreting_measurements.csv")
        inherited = self.measurements[self.measurements["source_key"].ne(SOURCE_KEY)]
        self.assertEqual(set(inherited["measurement_id"]), set(frozen["measurement_id"]))
        fields = ["ra_deg", "dec_deg", "redshift", "log_mbh_msun_std"]
        pd.testing.assert_frame_equal(
            frozen.set_index("measurement_id")[fields].sort_index(),
            inherited.set_index("measurement_id")[fields].sort_index(),
        )

    def test_xqr30_is_a_separate_luminous_comparison_stratum(self) -> None:
        self.assertEqual(len(self.xqr30), 42)
        self.assertTrue(self.xqr30["object_class"].eq("luminous_quasar_comparison").all())
        self.assertTrue(self.xqr30["mass_comparability_group"].eq("virial_uv_single_epoch").all())
        self.assertTrue(self.xqr30["log_mbh_systematic_dex"].eq(0.55).all())
        self.assertTrue(self.xqr30["project_version"].eq("v7.1").all())
        self.assertTrue(self.xqr30["catalogue_release"].eq(CATALOGUE_RELEASE).all())

    def test_lensing_and_published_consistency_issues_are_explicit(self) -> None:
        lensed = self.xqr30[self.xqr30["lensing_status"].eq("lensed")]
        self.assertEqual(lensed["object_id"].tolist(), ["WISEA J0439+1634"])
        self.assertEqual(lensed.iloc[0]["lensing_mu"], 51.3)
        self.assertEqual(lensed.iloc[0]["lensing_mass_correction_status"], "not_applied")
        self.assertFalse(bool(lensed.iloc[0]["growth_ranking_eligible_flag"]))
        self.assertEqual(
            lensed.iloc[0]["growth_ranking_eligibility_reason"],
            "lensing_correction_not_applied",
        )
        inconsistent = self.xqr30[self.xqr30["edd_ratio_consistency_flag"].eq("inconsistent")]
        self.assertEqual(set(inconsistent["object_id"]), {
            "VST-ATLAS J025-33", "WISEA J0439+1634",
            "ULAS J1319+0950", "CFHQS J1509-1749",
        })
        self.assertTrue(inconsistent["source_caveat_tags"].str.contains(
            "published_mgii_edd_ratio_internal_inconsistency"
        ).all())

    def test_admission_and_observable_contracts(self) -> None:
        validate_v7_admission(self.measurements)
        validate_standardized_compatibility(self.measurements)
        validate_v7_observables(
            self.outputs["observables"], self.measurements["measurement_id"],
        )

    def test_checked_in_products_reproduce_in_memory(self) -> None:
        for name, frame in self.outputs.items():
            expected = pd.read_csv(OUTPUTS[name])
            actual = pd.read_csv(io.StringIO(frame.to_csv(index=False)))
            assert_frames_semantically_equal(expected, actual, label=name)

    def test_manifest_metadata_and_counts_are_enforced(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text())
        verify_manifest_metadata(manifest)
        broken = {**manifest, "catalogue_counts": dict(manifest["catalogue_counts"])}
        broken["catalogue_counts"]["measurements"] = 162
        with self.assertRaisesRegex(AssertionError, "catalogue_counts mismatch"):
            verify_manifest_metadata(broken)

    def test_no_v7_1_science_or_figure_outputs_exist(self) -> None:
        self.assertFalse(any((ROOT / "results").glob("v7_1_*.csv")))
        self.assertFalse(any((ROOT / "results").glob("v7_1_*.png")))


if __name__ == "__main__":
    unittest.main()
