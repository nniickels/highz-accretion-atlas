"""Regression tests for the machine-readable source-provenance supplement."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import pandas as pd

from src.internal.verify_source_provenance import MANIFEST_PATH, verify_metadata
from src.internal.verify_manual_extractions import load_and_verify_audit
from src.selection_completeness import build_selection_summary, load_selection_registry
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
        self.assertEqual(len(self.registry), 38)
        self.assertEqual(self.registry["source_key"].nunique(), 32)
        catalogue = pd.read_csv(CATALOGUE_PATH, low_memory=False)
        validate_catalogue_source_coverage(self.registry, catalogue)

    def test_juodzbalis_backfill_is_explicitly_non_destructive(self) -> None:
        row = self.registry.set_index("provenance_id").loc["juodzbalis25_primary"]
        self.assertEqual(row["source_doi"], "10.1093/mnras/stag086")
        self.assertEqual(row["source_archive_sha256"], "0347b4942f1a3cb417d626bd5ba76ab0af25e59ab8013b3ed4ac0a61a04e0efd")
        self.assertEqual(row["catalogue_extraction_date"], "not_recorded_in_frozen_v1_source_layer")
        self.assertEqual(row["catalogue_value_policy"], "supplement_only_frozen_rows_unchanged")

    def test_zs7_is_pinned_to_the_matching_source_archive(self) -> None:
        row = self.registry.set_index("provenance_id").loc["ubler24_primary"]
        self.assertIn("arXiv:2312.03589v2", row["source_paper_version"])
        self.assertEqual(row["source_archive_url"], "https://arxiv.org/e-print/2312.03589v2")
        self.assertEqual(
            row["source_archive_sha256"],
            "830ecf743046d0f848e83e0905972b0a8c16d86ddbb1a92c3e61816057642344",
        )

    def test_preprints_have_review_schedule(self) -> None:
        preprints = self.registry[self.registry["publication_status"] == "preprint"]
        self.assertEqual(set(preprints["provenance_id"]), {
            "davis26_primary", "hutchison25_coordinates", "skyfire26_primary",
            "meow26_primary", "chavezortiz26_primary", "mascia26_primary",
            "zhuang25_primary",
        })
        expected_due = {
            "davis26_primary": "2026-12-03", "hutchison25_coordinates": "2026-12-03",
            "skyfire26_primary": "2026-12-03",
            "meow26_primary": "2026-12-03", "chavezortiz26_primary": "2026-12-03",
            "mascia26_primary": "2026-12-03", "zhuang25_primary": "2026-12-03",
        }
        self.assertEqual(preprints.set_index("provenance_id")["status_review_due"].to_dict(), expected_due)
        zou = self.registry.set_index("provenance_id").loc["zou26_reanalysis"]
        self.assertEqual(zou["publication_status"], "accepted")
        self.assertEqual(zou["source_paper_version"], "arXiv:2603.24893v2 accepted by ApJ")

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
        audit = load_and_verify_audit()
        selection = load_selection_registry(ROOT / "data/selection_function_registry.csv")
        verify_metadata(json.loads(MANIFEST_PATH.read_text()), self.registry, selection, audit)

    def test_manual_extraction_and_selection_registries(self) -> None:
        audit = load_and_verify_audit()
        self.assertEqual(len(audit), 26)
        selection = load_selection_registry(ROOT / "data/selection_function_registry.csv")
        self.assertEqual(set(selection["source_key"]), set(self.registry["source_key"]))

    def test_selection_summary_parses_serialized_boolean_flags(self) -> None:
        measurements = pd.DataFrame({
            "measurement_id": ["a", "b"],
            "physical_object_id": ["a", "b"],
            "source_key": ["juodzbalis25_jades_blagn"] * 2,
            "growth_ranking_eligible_flag": ["True", "False"],
        })
        selection = load_selection_registry(ROOT / "data/selection_function_registry.csv")
        summary = build_selection_summary(measurements, selection)
        self.assertEqual(int(summary.loc[0, "growth_plottable_measurements"]), 1)
        self.assertEqual(int(summary.loc[0, "growth_plottable_objects"]), 1)

    def test_revised_ghz2_source_is_pinned_to_v2(self) -> None:
        row = self.registry.set_index("provenance_id").loc["chavezortiz26_primary"]
        self.assertEqual(row["source_paper_version"], "arXiv:2511.03035v2")
        self.assertEqual(row["source_archive_url"], "https://arxiv.org/e-print/2511.03035v2")
        self.assertEqual(
            row["source_archive_sha256"],
            "1e8def5725a3639afb6ba15e1f4e8b8b95e28f36501b7a974595f9f0b5c87c4a",
        )


if __name__ == "__main__":
    unittest.main()
