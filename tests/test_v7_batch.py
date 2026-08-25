"""Tests for generic heterogeneous source-family batch assembly."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.v7_batch import (
    SourceAdmissionBundle,
    assemble_source_family_batch,
    load_source_family_registry,
    validate_source_family_registry,
)
from src.v7_catalogue import adapt_v6_measurements
from src.v7_ren import build_ren_admission, build_ren_observables


class V7BatchAssemblyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        v6 = pd.read_csv(ROOT / "data/processed/v6_blagn_measurements.csv")
        table1 = pd.read_csv(ROOT / "data/raw/ren25_alpine_cristal_jwst_table1.csv")
        table2 = pd.read_csv(
            ROOT / "data/raw/ren25_alpine_cristal_jwst_table2_observables.csv"
        )
        cls.prior = adapt_v6_measurements(v6)
        cls.ren = build_ren_admission(table1)
        cls.observables = build_ren_observables(
            table2, cls.ren[["measurement_id", "object_id"]],
        )
        cls.bundle = SourceAdmissionBundle(
            source_key=cls.ren["source_key"].iloc[0],
            evidence_family="host_selected_broad_halpha_candidates",
            measurements=cls.ren,
            observables=cls.observables,
        )

    def test_current_source_assembles_through_generic_batch_gate(self) -> None:
        assembled = assemble_source_family_batch(self.prior, [self.bundle])
        self.assertEqual(len(assembled.measurements), 119)
        self.assertEqual(len(assembled.observables), 70)
        self.assertTrue(assembled.identity_candidates.empty)

    def test_batch_requires_one_evidence_family(self) -> None:
        other = SourceAdmissionBundle(
            source_key="synthetic_other_source",
            evidence_family="xray_candidates",
            measurements=self.ren.assign(source_key="synthetic_other_source"),
        )
        with self.assertRaisesRegex(ValueError, "one coherent evidence family"):
            assemble_source_family_batch(self.prior, [self.bundle, other])

    def test_bundle_observables_cannot_reference_another_release(self) -> None:
        broken = self.observables.copy()
        broken.loc[0, "measurement_id"] = self.prior.iloc[0]["measurement_id"]
        bundle = SourceAdmissionBundle(
            source_key=self.bundle.source_key,
            evidence_family=self.bundle.evidence_family,
            measurements=self.ren,
            observables=broken,
        )
        with self.assertRaisesRegex(ValueError, "unknown measurements"):
            bundle.validate()

    def test_source_family_registry_is_executable_and_controlled(self) -> None:
        registry = load_source_family_registry(
            ROOT / "data/source_family_registry.csv"
        )
        released = registry[registry["status"].eq("released_catalogue_layer")]
        self.assertEqual(released["source_key"].tolist(), [self.bundle.source_key])
        selected = registry[registry["status"].eq("selected_pending_source_audit")]
        self.assertEqual(selected["source_key"].tolist(), ["xqr30_mazzucchelli23"])
        broken = registry.copy()
        broken.loc[0, "admission_module"] = ""
        with self.assertRaisesRegex(ValueError, "require an admission_module"):
            validate_source_family_registry(broken)


if __name__ == "__main__":
    unittest.main()
