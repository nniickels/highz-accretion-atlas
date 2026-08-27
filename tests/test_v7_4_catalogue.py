"""Regression tests for the v7.4 Scholtz JADES admission."""

from __future__ import annotations

import io
import json
import sys
import unittest
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.process_v7_4_catalogue import OUTPUTS, build_outputs
from scripts.reproduction import assert_frames_semantically_equal
from scripts.verify_v7_4_catalogue import MANIFEST_PATH, verify_manifest_metadata
from src.v7_4_scholtz import SOURCE_KEY, validate_scholtz_source
from src.v7_admission import validate_v7_admission, validate_v7_observables


class V74CatalogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = pd.read_csv(ROOT / "data/raw/scholtz25_jades_narrow_line_agn_zge4.csv")
        cls.outputs = build_outputs()
        cls.measurements = cls.outputs["measurements"]
        cls.source = cls.measurements[cls.measurements["source_key"].eq(SOURCE_KEY)]

    def test_source_scope_and_published_anchors(self) -> None:
        clean = validate_scholtz_source(self.raw)
        self.assertEqual(len(clean), 20)
        self.assertEqual(int(clean["tentative_flag"].sum()), 3)
        self.assertEqual(int(clean.filter(regex="flux_1e19$").notna().sum().sum()), 7)

    def test_exact_release_cardinalities(self) -> None:
        self.assertEqual((len(self.measurements), len(self.outputs["objects"]), len(self.outputs["host_systems"])), (233, 218, 217))
        self.assertEqual(len(self.outputs["aliases"]), 275)
        self.assertEqual(len(self.outputs["reviewed_match_candidates"]), 1)
        self.assertEqual(len(self.outputs["observables"]), 1102)

    def test_no_black_hole_mass_or_growth_eligibility_is_invented(self) -> None:
        self.assertTrue(self.source["log_mbh_msun_std"].isna().all())
        self.assertTrue(self.source["mass_comparability_group"].eq("no_numeric_mass").all())
        self.assertFalse(self.source["growth_ranking_eligible_flag"].astype(bool).any())

    def test_jades_8083_is_linked_without_replacing_preferred_mass_row(self) -> None:
        linked = self.measurements[self.measurements["physical_object_id"].eq("HZA-GS-8083")]
        self.assertEqual(set(linked["measurement_id"]), {"GS8083_juodzbalis25", "scholtz25_00008083"})
        preferred = linked[linked["preferred_measurement_flag"].astype(bool)]
        self.assertEqual(preferred["measurement_id"].tolist(), ["GS8083_juodzbalis25"])

    def test_frozen_v7_3_rows_are_inherited(self) -> None:
        frozen = pd.read_csv(ROOT / "data/processed/v7_3/v7_3_accreting_measurements.csv")
        inherited = self.measurements[self.measurements["source_key"].ne(SOURCE_KEY)]
        fields = ["ra_deg", "dec_deg", "redshift", "log_mbh_msun_std", "evidence_status"]
        pd.testing.assert_frame_equal(frozen.set_index("measurement_id")[fields].sort_index(), inherited.set_index("measurement_id")[fields].sort_index())

    def test_contracts_and_reproduction(self) -> None:
        validate_v7_admission(self.measurements)
        validate_v7_admission(self.outputs["objects"])
        validate_v7_observables(self.outputs["observables"], self.measurements["measurement_id"])
        for name, frame in self.outputs.items():
            expected = pd.read_csv(OUTPUTS[name])
            actual = pd.read_csv(io.StringIO(frame.to_csv(index=False)))
            assert_frames_semantically_equal(expected, actual, label=name)

    def test_manifest_metadata(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text())
        verify_manifest_metadata(manifest)


if __name__ == "__main__": unittest.main()
