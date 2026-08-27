"""Regression tests for the catalogue-only v7.2 GNIRS-50 release."""

from __future__ import annotations

import io
import json
import sys
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.process_v7_2_catalogue import OUTPUTS, build_outputs
from scripts.reproduction import assert_frames_semantically_equal
from scripts.verify_v7_2_catalogue import MANIFEST_PATH, verify_manifest_metadata
from src.v7_2_catalogue import CATALOGUE_RELEASE
from src.v7_admission import validate_v7_admission, validate_v7_observables
from src.v7_batch import validate_standardized_compatibility
from src.v7_shen19 import SOURCE_KEY, validate_shen19_sources


class V72CatalogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sample = pd.read_csv(ROOT / "data/raw/shen19_gnirs_table1.csv")
        cls.catalog = pd.read_csv(ROOT / "data/raw/shen19_gnirs_table3.csv")
        cls.outputs = build_outputs()
        cls.measurements = cls.outputs["measurements"]
        cls.gnirs = cls.measurements[cls.measurements["source_key"].eq(SOURCE_KEY)]

    def test_complete_source_tables_and_caveats(self) -> None:
        sample, catalog = validate_shen19_sources(self.sample, self.catalog)
        self.assertEqual(len(sample), 50)
        self.assertEqual(len(catalog), 50)
        self.assertEqual(sample["comment"].fillna("").str.contains(r"\bBAL\b").sum(), 8)
        self.assertEqual(sample["comment"].fillna("").str.contains("radio-loud").sum(), 4)
        self.assertEqual(catalog["log_mbh_fiducial_msun"].notna().sum(), 49)

    def test_exact_release_cardinalities(self) -> None:
        self.assertEqual(len(self.measurements), 211)
        self.assertEqual(self.measurements["physical_object_id"].nunique(), 198)
        self.assertEqual(self.measurements["host_system_id"].nunique(), 197)
        self.assertEqual(len(self.outputs["aliases"]), 253)
        self.assertEqual(len(self.outputs["reviewed_match_candidates"]), 6)
        self.assertEqual(len(self.outputs["observables"]), 993)

    def test_full_family_and_mass_method_semantics(self) -> None:
        self.assertEqual(len(self.gnirs), 50)
        self.assertEqual(self.gnirs["log_mbh_msun_std"].notna().sum(), 49)
        self.assertEqual(self.gnirs["fiducial_mass_line"].value_counts().to_dict(), {
            "MgII": 29, "CIV": 20, "none": 1,
        })
        self.assertTrue(self.gnirs["log_mbh_systematic_dex"].dropna().eq(0.4).all())
        massless = self.gnirs[self.gnirs["object_id"].eq("J0055+0146")].iloc[0]
        self.assertFalse(bool(massless["growth_ranking_eligible_flag"]))
        self.assertEqual(massless["growth_ranking_eligibility_reason"], "missing_numeric_mbh")

    def test_six_reviewed_repeats_preserve_prior_preference(self) -> None:
        decisions = self.outputs["reviewed_match_candidates"]
        self.assertEqual(set(decisions["decision"]), {"accepted"})
        self.assertEqual(set(decisions["match_origin"]), {"threshold_candidate", "manual_assertion"})
        repeated = self.gnirs[self.gnirs["preferred_measurement_flag"].eq(False)]
        self.assertEqual(len(repeated), 6)
        self.assertTrue(repeated["physical_object_id"].str.startswith("HZA-XQR30-").all())
        preferred = self.measurements.groupby("physical_object_id")["preferred_measurement_flag"].sum()
        self.assertTrue(preferred.eq(1).all())

    def test_v7_1_is_inherited_without_scientific_overwrite(self) -> None:
        frozen = pd.read_csv(ROOT / "data/processed/v7_1_accreting_measurements.csv")
        inherited = self.measurements[self.measurements["source_key"].ne(SOURCE_KEY)]
        self.assertEqual(set(inherited["measurement_id"]), set(frozen["measurement_id"]))
        fields = ["ra_deg", "dec_deg", "redshift", "log_mbh_msun_std"]
        pd.testing.assert_frame_equal(
            frozen.set_index("measurement_id")[fields].sort_index(),
            inherited.set_index("measurement_id")[fields].sort_index(),
        )

    def test_admission_and_observable_contracts(self) -> None:
        validate_v7_admission(self.measurements)
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
        broken["catalogue_counts"]["measurements"] = 212
        with self.assertRaisesRegex(AssertionError, "catalogue_counts mismatch"):
            verify_manifest_metadata(broken)

    def test_no_v7_2_figure_outputs_exist(self) -> None:
        self.assertFalse(any((ROOT / "results").glob("v7_2_*.png")))


if __name__ == "__main__":
    unittest.main()
