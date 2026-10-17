"""Verify the current JWST-identified source-provenance registry and its hash."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from src.internal.release_verification import (
    require_clean_worktree,
    verify_artifact_manifest,
)
from src.internal.verify_manual_extractions import load_and_verify_audit
from src.selection_completeness import load_selection_registry
from src.source_provenance import (
    load_source_provenance_registry,
    validate_catalogue_source_coverage,
)


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "data/source_provenance_registry.csv"
CATALOGUE_PATH = ROOT / "data/processed/v3/v3_accreting_measurements.csv"
MANIFEST_PATH = ROOT / "data/manifests/source-provenance-manifest.json"
SELECTION_PATH = ROOT / "data/selection_function_registry.csv"
AUDIT_PATH = ROOT / "data/manual_extraction_audit.csv"
ARTIFACTS = {
    "data/assembly/reconciled_identity_pairs.json",
    "data/source_provenance_registry.csv",
    "data/selection_function_registry.csv",
    "data/manual_extraction_audit.csv",
    "data/validation/primary_source_checks.json",
    "data/validation/primary_family_anchors.json",
    "data/validation/complete_mass_checks.json",
    "data/validation/redshift_identity_checks.json",
    "data/validation/source_inputs/killi-published-crossref.json",
    "data/validation/source_inputs/baccus_published_table1.txt",
}

ARTIFACTS.update(
    {
        "data/validation/source_inputs/sapphires_z847_v1_extract.html",
        "data/validation/source_inputs/takechi26_macs0416_y1_tamura18v2_astrometry.tex",
        "data/validation/takechi26_macs0416_y1_crossmatch.json",
        "data/validation/capers_lrd_z9_expected_values.json",
        "data/validation/source_inputs/capers_lrd_z9_v4_extract.html",
        "data/validation/source_inputs/sapphires_z847_v1_main.tex",
        "data/validation/canucs_adapter_check.py",
        "data/validation/source_inputs/schindler25_j1007_published_table3.jpg",
        "data/validation/source_inputs/canucs_morishita25_v2_extract.txt",
        "data/validation/canucs_expected_values.json",
        "data/validation/takechi26_macs0416_y1_expected.json",
        "data/validation/source_inputs/schindler25_j1007_published_methods.txt",
        "data/validation/source_inputs/canucs_tripodi25_published_extract.txt",
        "data/validation/source_inputs/canucs_tripodi24_v1_extract.txt",
        "data/validation/sapphires_z847_source_manifest.json",
        "data/validation/source_inputs/capers_lrd_z9_published_crossref.json",
        "data/validation/source_inputs/schindler25_j1007_published_table1.jpg",
        "data/validation/source_inputs/takechi26_macs0416_y1_arxiv_metadata.html",
        "data/validation/source_inputs/schindler25_j1007_arxiv_v2_tables.html",
        "data/validation/sapphires_z847_catalogue_crossmatch.csv",
        "data/validation/source_inputs/capers_lrd_z9_v4_figure6_legend.txt",
        "data/validation/source_inputs/takechi26_macs0416_y1_provenance.json",
        "data/validation/source_inputs/schindler25_j1007_published_table2.jpg",
        "data/validation/source_inputs/takechi26_macs0416_y1_v1_extract.tex",
        "data/validation/canucs_identity_screen.json",
        "data/validation/capers_lrd_z9_identity_checks.json",
        "data/validation/takechi26_macs0416_y1_adapter.py",
        "data/validation/source_inputs/schindler25_j1007_provenance.json",
        "data/validation/schindler25_j1007_expected.json",
        "data/validation/sapphires_z847_macs0416_context_crossmatch.csv",
        "data/validation/sapphires_z847_expected_values.json",
        "data/validation/source_inputs/canucs_tripodi25_supplement_tables.txt",
        "data/validation/source_inputs/sapphires_z847_version_history.html",
        "data/validation/source_inputs/capers_lrd_z9_v4_main.tex",
        "data/validation/canucs_source_payloads.json",
        "data/validation/capers_lrd_z9_validate.py",
        "data/validation/source_inputs/canucs_morishita25_v1_mass_passage.txt",
        "data/validation/capers_lrd_z9_source_manifest.json",
    }
)


def manifest_metadata(
    registry: pd.DataFrame,
    selection: pd.DataFrame,
    audit: pd.DataFrame,
) -> dict[str, object]:
    """Return the release metadata derived from the validated registries."""
    return {
        "release": "source-provenance-2026-10-17",
        "scope": "provenance, extraction, and selection records for the JWST-identified catalogue",
        "registry_rows": len(registry),
        "catalogue_source_keys": registry["source_key"].nunique(),
        "preprint_records": int((registry["publication_status"] == "preprint").sum()),
        "selection_registry_rows": len(selection),
        "manual_extraction_artifacts": len(audit),
    }


def build_manifest(
    registry: pd.DataFrame,
    selection: pd.DataFrame,
    audit: pd.DataFrame,
) -> dict[str, object]:
    """Build the deterministic manifest for the evidence registries and independent source fixtures."""
    manifest = manifest_metadata(registry, selection, audit)
    manifest["artifacts"] = {
        relative: hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        for relative in sorted(ARTIFACTS)
    }
    return manifest


def verify_metadata(
    manifest: dict[str, object],
    registry: pd.DataFrame,
    selection: pd.DataFrame,
    audit: pd.DataFrame,
) -> None:
    expected = manifest_metadata(registry, selection, audit)
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise AssertionError(f"source provenance manifest {key} mismatch")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-clean", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.require_clean:
        require_clean_worktree(ROOT, "source provenance")
    registry = load_source_provenance_registry(REGISTRY_PATH)
    selection = load_selection_registry(SELECTION_PATH)
    audit = load_and_verify_audit(AUDIT_PATH)
    catalogue = pd.read_csv(CATALOGUE_PATH, low_memory=False)
    validate_catalogue_source_coverage(registry, catalogue)
    if args.write:
        MANIFEST_PATH.write_text(
            json.dumps(build_manifest(registry, selection, audit), indent=2) + "\n"
        )
    manifest = json.loads(MANIFEST_PATH.read_text())
    verify_metadata(manifest, registry, selection, audit)
    verify_artifact_manifest(
        root=ROOT,
        artifacts=manifest.get("artifacts"),
        expected_paths=ARTIFACTS,
        release_label="source provenance",
    )
    if args.require_clean:
        require_clean_worktree(ROOT, "source provenance")
    print(
        f"Verified {len(registry)} provenance records, {len(selection)} selection records, "
        f"and {len(audit)} extraction artifacts covering all "
        f"{registry['source_key'].nunique()} final-v3 source families"
    )


if __name__ == "__main__":
    main()
