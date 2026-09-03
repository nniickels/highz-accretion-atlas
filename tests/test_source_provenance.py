"""Regression tests for the machine-readable source-provenance supplement."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import pandas as pd

from src.internal.verify_source_provenance import MANIFEST_PATH, verify_metadata
from src.source_provenance import (
    load_source_provenance_registry, validate_catalogue_source_coverage,
    validate_source_provenance_registry,
)


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data/source_provenance_registry.csv"
CATALOGUE_PATH = ROOT / "data/processed/v3/v3_accreting_measurements.csv"


class SourceProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = load_source_provenance_registry(REGISTRY_PATH)

    def test_registry_contract_and_current_catalogue_coverage(self) -> None:
        self.assertEqual(len(self.registry), 20)
        self.assertEqual(self.registry["source_key"].nunique(), 16)
        catalogue = pd.read_csv(CATALOGUE_PATH, low_memory=False)
        validate_catalogue_source_coverage(self.registry, catalogue)

    def test_juodzbalis_backfill_is_explicitly_non_destructive(self) -> None:
        row = self.registry.set_index("provenance_id").loc["juodzbalis25_primary"]
        self.assertEqual(row["source_doi"], "10.1093/mnras/stag086")
        self.assertEqual(row["source_archive_sha256"], "0347b4942f1a3cb417d626bd5ba76ab0af25e59ab8013b3ed4ac0a61a04e0efd")
        self.assertEqual(row["catalogue_extraction_date"], "not_recorded_in_frozen_v1_source_layer")
        self.assertEqual(row["catalogue_value_policy"], "supplement_only_frozen_rows_unchanged")

    def test_preprints_have_review_schedule(self) -> None:
        preprints = self.registry[self.registry["publication_status"] == "preprint"]
        self.assertEqual(set(preprints["provenance_id"]), {"davis26_primary", "hutchison25_coordinates", "zou26_reanalysis", "skyfire26_primary"})
        expected_due = {
            "davis26_primary": "2026-11-27", "hutchison25_coordinates": "2026-11-27",
            "zou26_reanalysis": "2026-11-27", "skyfire26_primary": "2026-12-03",
        }
        self.assertEqual(preprints.set_index("provenance_id")["status_review_due"].to_dict(), expected_due)

    def test_dataset_and_supporting_source_roles(self) -> None:
        rows = self.registry.set_index("provenance_id")
        self.assertEqual(rows.loc["goulding23_context", "source_role"], "context_source")
        self.assertEqual(rows.loc["bogdan23_primary", "evidence_status"], "candidate")
        self.assertEqual(rows.loc["scholtz25_primary", "evidence_status"], "candidate")

    def test_invalid_controlled_value_and_hash_fail(self) -> None:
        broken = self.registry.copy()
        broken.loc[0, "publication_status"] = "published"
        with self.assertRaises(AssertionError):
            validate_source_provenance_registry(broken)
        broken = self.registry.copy()
        broken.loc[0, "source_archive_sha256"] = "unknown"
        with self.assertRaises(AssertionError):
            validate_source_provenance_registry(broken)

    def test_manifest_metadata(self) -> None:
        verify_metadata(json.loads(MANIFEST_PATH.read_text()), self.registry)


if __name__ == "__main__":
    unittest.main()
