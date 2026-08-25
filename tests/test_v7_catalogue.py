"""Regression tests for the catalogue-only v7 assembly."""

from __future__ import annotations

import io
import json
import sys
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.process_v7_catalogue import OUTPUTS, build_outputs
from scripts.reproduction import assert_frames_semantically_equal
from scripts.verify_v7_catalogue import MANIFEST_PATH, verify_manifest_metadata
from src.v7_batch import validate_standardized_compatibility
from src.v7_admission import validate_v7_admission, validate_v7_observables
from src.v7_ren import SOURCE_KEY as REN_SOURCE_KEY


class V7CatalogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.outputs = build_outputs()
        cls.measurements = cls.outputs["measurements"]
        cls.objects = cls.outputs["objects"]
        cls.hosts = cls.outputs["host_systems"]

    def test_exact_catalogue_cardinalities(self) -> None:
        self.assertEqual(len(self.measurements), 119)
        self.assertEqual(self.measurements["physical_object_id"].nunique(), 112)
        self.assertEqual(self.measurements["host_system_id"].nunique(), 111)
        self.assertEqual(len(self.objects), 112)
        self.assertEqual(len(self.hosts), 111)
        self.assertEqual(len(self.outputs["measurement_object_links"]), 119)
        self.assertEqual(len(self.outputs["object_host_links"]), 112)
        self.assertEqual(len(self.outputs["aliases"]), 119)
        self.assertTrue(self.outputs["reviewed_match_candidates"].empty)

    def test_v6_rows_are_inherited_without_overwriting_v6(self) -> None:
        frozen = pd.read_csv(ROOT / "data/processed/v6_blagn_measurements.csv")
        inherited = self.measurements[self.measurements["source_key"].ne(REN_SOURCE_KEY)]
        self.assertEqual(set(inherited["measurement_id"]), set(frozen["measurement_id"]))
        shared_numeric = [
            "ra_deg", "dec_deg", "redshift", "log_mbh_msun_std",
            "log_mbh_err_plus_std", "log_mbh_err_minus_std",
        ]
        left = frozen.set_index("measurement_id")[shared_numeric].sort_index()
        right = inherited.set_index("measurement_id")[shared_numeric].sort_index()
        pd.testing.assert_frame_equal(left, right)
        self.assertEqual(len(list((ROOT / "data/processed").glob("v6_*.csv"))), 2)

    def test_ren_identity_and_host_system_semantics(self) -> None:
        ren = self.measurements[self.measurements["source_key"].eq(REN_SOURCE_KEY)]
        self.assertEqual(len(ren), 7)
        self.assertEqual(ren["physical_object_id"].nunique(), 7)
        self.assertEqual(ren["host_system_id"].nunique(), 6)
        pair = ren[ren["host_system_id"].eq("HZS-DC-848185")]
        self.assertEqual(pair["physical_object_id"].nunique(), 2)
        self.assertTrue(pair["host_property_scope"].eq("shared_host_system_total").all())
        host = self.hosts.set_index("host_system_id").loc["HZS-DC-848185"]
        self.assertEqual(host["n_physical_objects"], 2)
        self.assertEqual(host["n_measurements"], 2)
        self.assertEqual(host["log_mstar_msun_std"], 10.37)

    def test_eligibility_tiers_are_exact(self) -> None:
        self.assertEqual(int(self.measurements["growth_ranking_eligible_flag"].sum()), 119)
        self.assertEqual(int(self.measurements["primary_growth_ranking_flag"].sum()), 112)
        self.assertEqual(int(self.objects["growth_ranking_eligible_flag"].sum()), 112)
        self.assertEqual(int(self.objects["primary_growth_ranking_flag"].sum()), 105)
        ren = self.measurements[self.measurements["source_key"].eq(REN_SOURCE_KEY)]
        self.assertEqual(int(ren["primary_growth_ranking_flag"].sum()), 1)
        candidates = ren[ren["evidence_status"].eq("candidate")]
        self.assertTrue(candidates["conditional_mass_flag"].astype(bool).all())
        self.assertTrue(candidates["primary_growth_ranking_reason"].eq(
            "candidate_evidence_excluded"
        ).all())

    def test_one_preferred_measurement_per_object_is_preserved(self) -> None:
        preferred = self.measurements.groupby("physical_object_id")[
            "preferred_measurement_flag"
        ].sum()
        self.assertTrue(preferred.eq(1).all())
        duplicate = self.measurements[
            self.measurements["physical_object_id"].eq("HZA-CEERS-2782")
        ]
        self.assertEqual(duplicate.loc[
            duplicate["preferred_measurement_flag"].astype(bool), "measurement_id"
        ].tolist(), ["RUBIESEGS50052_taylor24"])

    def test_observables_and_strata_are_separate_catalogue_products(self) -> None:
        observables = self.outputs["observables"]
        self.assertEqual(len(observables), 70)
        self.assertEqual(int(observables["censoring"].eq("upper_limit").sum()), 12)
        validate_v7_observables(observables, self.measurements["measurement_id"])
        overall = self.outputs["strata"].query(
            "stratum_dimension == 'all'"
        ).set_index("entity_level")
        self.assertEqual(overall.loc["measurement", "count"], 119)
        self.assertEqual(overall.loc["physical_object", "count"], 112)

    def test_combined_measurements_pass_admission_gate(self) -> None:
        validate_v7_admission(self.measurements)
        validate_standardized_compatibility(self.measurements)

    def test_checked_in_products_reproduce_in_memory(self) -> None:
        for name, frame in self.outputs.items():
            expected = pd.read_csv(OUTPUTS[name])
            actual = pd.read_csv(io.StringIO(frame.to_csv(index=False)))
            assert_frames_semantically_equal(expected, actual, label=name)

    def test_manifest_metadata_and_counts_are_enforced(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text())
        verify_manifest_metadata(manifest)
        broken = {**manifest, "catalogue_counts": dict(manifest["catalogue_counts"])}
        broken["catalogue_counts"]["measurements"] = 120
        with self.assertRaisesRegex(AssertionError, "catalogue_counts mismatch"):
            verify_manifest_metadata(broken)

    def test_no_v7_science_or_figure_outputs_exist(self) -> None:
        self.assertFalse(any((ROOT / "results").glob("v7_*.csv")))
        self.assertFalse(any((ROOT / "results").glob("v7_*.png")))


if __name__ == "__main__":
    unittest.main()
