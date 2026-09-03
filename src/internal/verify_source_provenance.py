"""Verify the current JWST-identified source-provenance registry and its hash."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from src.internal.release_verification import require_clean_worktree, verify_artifact_manifest
from src.source_provenance import load_source_provenance_registry, validate_catalogue_source_coverage


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "data/source_provenance_registry.csv"
CATALOGUE_PATH = ROOT / "data/processed/v3/v3_accreting_measurements.csv"
MANIFEST_PATH = ROOT / "releases/source-provenance-manifest.json"
ARTIFACTS = {"data/source_provenance_registry.csv"}


def verify_metadata(manifest: dict[str, object], registry: pd.DataFrame) -> None:
    expected = {
        "release": "source-provenance-2026-09-03",
        "scope": "provenance registry for the JWST-identified catalogue",
        "registry_rows": len(registry),
        "catalogue_source_keys": registry["source_key"].nunique(),
        "preprint_records": int((registry["publication_status"] == "preprint").sum()),
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise AssertionError(f"source provenance manifest {key} mismatch")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-clean", action="store_true")
    args = parser.parse_args()
    if args.require_clean:
        require_clean_worktree(ROOT, "source provenance")
    registry = load_source_provenance_registry(REGISTRY_PATH)
    catalogue = pd.read_csv(CATALOGUE_PATH, low_memory=False)
    validate_catalogue_source_coverage(registry, catalogue)
    manifest = json.loads(MANIFEST_PATH.read_text())
    verify_metadata(manifest, registry)
    verify_artifact_manifest(
        root=ROOT, artifacts=manifest.get("artifacts"), expected_paths=ARTIFACTS,
        release_label="source provenance",
    )
    if args.require_clean:
        require_clean_worktree(ROOT, "source provenance")
    print("Verified 20 provenance records covering all 16 final-v3 source families")


if __name__ == "__main__":
    main()
