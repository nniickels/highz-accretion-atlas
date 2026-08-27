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

    def test_reviewed_prior_identity_is_applied_before_release(self) -> None:
        row = self.ren.iloc[[0]].copy()
        prior = self.prior.iloc[0]
        row["measurement_id"] = "reviewed_repeat_synthetic"
        row["ra_deg"] = prior["ra_deg"]
        row["dec_deg"] = prior["dec_deg"]
        row["redshift"] = prior["redshift"]
        row["preferred_measurement_flag"] = False
        row["preferred_measurement_reason"] = "prior-release preferred measurement retained"
        bundle = SourceAdmissionBundle(
            source_key=self.bundle.source_key,
            evidence_family=self.bundle.evidence_family,
            measurements=row,
        )
        overrides = pd.DataFrame([{
            "measurement_id": "reviewed_repeat_synthetic",
            "candidate_measurement_id": prior["measurement_id"],
            "decision": "accepted",
            "physical_object_id": prior["physical_object_id"],
            "review_basis": "synthetic regression fixture",
            "review_reference": "tests/test_v7_batch.py",
            "review_date": "2026-08-26",
            "match_origin": "threshold_candidate",
        }])
        assembled = assemble_source_family_batch(
            self.prior, [bundle], identity_overrides=overrides,
        )
        admitted = assembled.measurements.set_index("measurement_id").loc[
            "reviewed_repeat_synthetic"
        ]
        self.assertEqual(admitted["physical_object_id"], prior["physical_object_id"])
        self.assertEqual(admitted["host_system_id"], prior["host_system_id"])
        self.assertEqual(assembled.identity_candidates.iloc[0]["decision"], "accepted")

    def test_reviewed_rejection_preserves_distinct_identity(self) -> None:
        row = self.ren.iloc[[0]].copy()
        prior = self.prior.iloc[0]
        row["measurement_id"] = "reviewed_rejection_synthetic"
        row["ra_deg"] = prior["ra_deg"]
        row["dec_deg"] = prior["dec_deg"]
        row["redshift"] = prior["redshift"]
        original_id = row.iloc[0]["physical_object_id"]
        bundle = SourceAdmissionBundle(
            source_key=self.bundle.source_key,
            evidence_family=self.bundle.evidence_family,
            measurements=row,
        )
        overrides = pd.DataFrame([{
            "measurement_id": "reviewed_rejection_synthetic",
            "candidate_measurement_id": prior["measurement_id"],
            "decision": "rejected",
            "physical_object_id": "",
            "review_basis": "synthetic regression fixture",
            "review_reference": "tests/test_v7_batch.py",
            "review_date": "2026-08-26",
            "match_origin": "threshold_candidate",
        }])
        assembled = assemble_source_family_batch(
            self.prior, [bundle], identity_overrides=overrides,
        )
        admitted = assembled.measurements.set_index("measurement_id").loc[
            "reviewed_rejection_synthetic"
        ]
        self.assertEqual(admitted["physical_object_id"], original_id)

    def test_missing_review_decision_remains_fail_closed(self) -> None:
        row = self.ren.iloc[[0]].copy()
        prior = self.prior.iloc[0]
        row["measurement_id"] = "unreviewed_repeat_synthetic"
        row["ra_deg"] = prior["ra_deg"]
        row["dec_deg"] = prior["dec_deg"]
        row["redshift"] = prior["redshift"]
        bundle = SourceAdmissionBundle(
            source_key=self.bundle.source_key,
            evidence_family=self.bundle.evidence_family,
            measurements=row,
        )
        empty = pd.DataFrame(columns=[
            "measurement_id", "candidate_measurement_id", "decision",
            "physical_object_id", "review_basis", "review_reference",
            "review_date", "match_origin",
        ])
        with self.assertRaisesRegex(ValueError, "Unreviewed identity candidates"):
            assemble_source_family_batch(
                self.prior, [bundle], identity_overrides=empty,
            )

    def test_source_family_registry_is_executable_and_controlled(self) -> None:
        registry = load_source_family_registry(
            ROOT / "data/source_family_registry.csv"
        )
        released = registry[registry["status"].eq("released_catalogue_layer")]
        self.assertEqual(released["source_key"].tolist(), [
            self.bundle.source_key, "xqr30_mazzucchelli23", "shen19_gnirs50",
            "uhz1_xray_evidence_history",
        ])
        selected = registry[registry["status"].eq("selected_pending_source_audit")]
        self.assertTrue(selected.empty)
        broken = registry.copy()
        broken.loc[0, "admission_module"] = ""
        with self.assertRaisesRegex(ValueError, "require an admission_module"):
            validate_source_family_registry(broken)


if __name__ == "__main__":
    unittest.main()
