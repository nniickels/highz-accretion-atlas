"""Verify the catalogue-only v7 manifest and in-memory reproduction."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from scripts.process_v7_catalogue import OUTPUTS, build_outputs
from scripts.release_verification import (
    relative_artifact_paths, require_clean_worktree, verify_artifact_manifest,
)
from scripts.reproduction import assert_csv_reproduction
from src.v7_catalogue import CATALOGUE_RELEASE


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "releases" / "v7-catalogue-manifest.json"
EXPECTED_SCOPE = "catalogue-only; no v7 science rankings or figures"
EXPECTED_PYTHON = "3.12"
EXPECTED_COUNTS = {
    "measurements": 119,
    "physical_objects": 112,
    "host_systems": 111,
    "growth_eligible_measurements": 119,
    "primary_measurements": 112,
    "growth_eligible_physical_objects": 112,
    "primary_physical_objects": 105,
    "measurement_object_links": 119,
    "object_host_links": 112,
    "aliases": 119,
    "reviewed_match_records": 0,
    "source_observables": 70,
}


def expected_artifact_paths() -> set[str]:
    return relative_artifact_paths(ROOT, OUTPUTS.values())


def observed_catalogue_counts() -> dict[str, int]:
    frames = {name: pd.read_csv(path) for name, path in OUTPUTS.items()}
    measurements = frames["measurements"]
    objects = frames["objects"]
    return {
        "measurements": len(measurements),
        "physical_objects": measurements["physical_object_id"].nunique(),
        "host_systems": measurements["host_system_id"].nunique(),
        "growth_eligible_measurements": int(
            measurements["growth_ranking_eligible_flag"].astype(bool).sum()
        ),
        "primary_measurements": int(
            measurements["primary_growth_ranking_flag"].astype(bool).sum()
        ),
        "growth_eligible_physical_objects": int(
            objects["growth_ranking_eligible_flag"].astype(bool).sum()
        ),
        "primary_physical_objects": int(
            objects["primary_growth_ranking_flag"].astype(bool).sum()
        ),
        "measurement_object_links": len(frames["measurement_object_links"]),
        "object_host_links": len(frames["object_host_links"]),
        "aliases": len(frames["aliases"]),
        "reviewed_match_records": len(frames["reviewed_match_candidates"]),
        "source_observables": len(frames["observables"]),
    }


def verify_manifest_metadata(manifest: dict[str, object]) -> None:
    expected = {
        "catalogue_release": CATALOGUE_RELEASE,
        "scope": EXPECTED_SCOPE,
        "python": EXPECTED_PYTHON,
        "catalogue_counts": EXPECTED_COUNTS,
    }
    for field, value in expected.items():
        if manifest.get(field) != value:
            raise AssertionError(
                f"v7 catalogue manifest {field} mismatch: "
                f"expected {value!r}, found {manifest.get(field)!r}"
            )
    observed = observed_catalogue_counts()
    if observed != EXPECTED_COUNTS:
        raise AssertionError(
            f"v7 checked-in catalogue counts mismatch: "
            f"expected {EXPECTED_COUNTS!r}, found {observed!r}"
        )


def verify_manifest(manifest: dict[str, object]) -> None:
    verify_artifact_manifest(
        root=ROOT, artifacts=manifest.get("artifacts"),
        expected_paths=expected_artifact_paths(), release_label="v7 catalogue",
    )


def verify_reproduction() -> None:
    for name, frame in build_outputs().items():
        assert_csv_reproduction(OUTPUTS[name], frame)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reproduce", action="store_true")
    parser.add_argument("--require-clean", action="store_true")
    args = parser.parse_args()
    if args.require_clean:
        require_clean_worktree(ROOT, "v7 catalogue")
    manifest = json.loads(MANIFEST_PATH.read_text())
    verify_manifest_metadata(manifest)
    verify_manifest(manifest)
    if args.reproduce:
        verify_reproduction()
    if args.require_clean:
        require_clean_worktree(ROOT, "v7 catalogue")
    mode = "hashes and in-memory reproduction" if args.reproduce else "artifact hashes"
    print(f"Verified {manifest['catalogue_release']} {mode}; no artifact was written")


if __name__ == "__main__":
    main()
