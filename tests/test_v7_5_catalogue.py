"""Regression tests for the v7.5 provenance and evidence-policy release."""

from __future__ import annotations

import io
import json
import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.process_v7_5_catalogue import FULL_TABLE, OUTPUTS, build_outputs
from scripts.reproduction import assert_frames_semantically_equal
from scripts.verify_v7_5_catalogue import MANIFEST_PATH, verify_manifest_metadata
from src.v7_4_scholtz import SOURCE_KEY, validate_full_table_selection
from src.v7_5_catalogue import OBJECT_EVIDENCE_POLICY
from src.v7_admission import validate_v7_admission, validate_v7_observables


class V75CatalogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.outputs = build_outputs()
        cls.measurements = cls.outputs["measurements"]
        cls.objects = cls.outputs["objects"]

    def test_full_source_table_proves_exact_zge4_membership(self) -> None:
        raw = pd.concat([
            pd.read_csv(ROOT / "data/raw/scholtz25_jades_narrow_line_agn_zge4.csv"),
            pd.read_csv(ROOT / "data/raw/scholtz25_jades_narrow_line_agn_v7_5_correction.csv"),
        ], ignore_index=True)
        full = validate_full_table_selection(FULL_TABLE, raw)
        self.assertEqual((len(full), int(full["redshift"].ge(4).sum())), (41, 21))

    def test_release_cardinalities_and_correction(self) -> None:
        self.assertEqual((len(self.measurements), len(self.objects), len(self.outputs["host_systems"])), (234, 219, 218))
        self.assertEqual((len(self.outputs["aliases"]), len(self.outputs["observables"])), (276, 1106))
        source = self.measurements[self.measurements["source_key"].eq(SOURCE_KEY)]
        self.assertEqual(len(source), 21)
        corrected = source[source["object_id"].eq("JADES-NS-GS00099671")].iloc[0]
        self.assertEqual((corrected["redshift"], corrected["log_mstar_msun_std"]), (5.936, 7.5))
        self.assertTrue(pd.isna(corrected["log_mbh_msun_std"]))

    def test_preferred_measurement_controls_object_evidence(self) -> None:
        row = self.objects.set_index("physical_object_id").loc["HZA-GS-8083"]
        self.assertEqual(row["evidence_status"], "secure")
        self.assertTrue(bool(row["primary_growth_ranking_flag"]))
        self.assertEqual(row["object_evidence_aggregation_policy"], OBJECT_EVIDENCE_POLICY)
        self.assertIn("candidate", row["all_measurement_evidence_statuses"])
        uzh1 = self.objects.set_index("physical_object_id").loc["HZA-UHZ1"]
        self.assertEqual(uzh1["evidence_status"], "disputed")

    def test_frozen_v74_rows_are_numerically_inherited(self) -> None:
        frozen = pd.read_csv(ROOT / "data/processed/v7_4/v7_4_accreting_measurements.csv")
        inherited = self.measurements[self.measurements["measurement_id"].isin(frozen["measurement_id"])]
        fields = ["ra_deg", "dec_deg", "redshift", "log_mbh_msun_std", "evidence_status"]
        pd.testing.assert_frame_equal(
            frozen.set_index("measurement_id")[fields].sort_index(),
            inherited.set_index("measurement_id")[fields].sort_index(),
        )

    def test_contracts_reproduction_and_manifest(self) -> None:
        validate_v7_admission(self.measurements)
        validate_v7_admission(self.objects)
        validate_v7_observables(self.outputs["observables"], self.measurements["measurement_id"])
        for name, frame in self.outputs.items():
            expected = pd.read_csv(OUTPUTS[name])
            actual = pd.read_csv(io.StringIO(frame.to_csv(index=False)))
            assert_frames_semantically_equal(expected, actual, label=name)
        verify_manifest_metadata(json.loads(MANIFEST_PATH.read_text()))


if __name__ == "__main__":
    unittest.main()
