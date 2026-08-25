"""Verify the catalogue-only v7 manifest and in-memory reproduction."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import pandas as pd

from scripts.process_v7_catalogue import OUTPUTS, build_outputs
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


def worktree_status() -> str:
    return subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def expected_artifact_paths() -> set[str]:
    return {path.relative_to(ROOT).as_posix() for path in OUTPUTS.values()}


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
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        raise AssertionError("v7 catalogue manifest artifacts must be an object")
    expected_paths = expected_artifact_paths()
    if set(artifacts) != expected_paths:
        missing = sorted(expected_paths - set(artifacts))
        unexpected = sorted(set(artifacts) - expected_paths)
        raise AssertionError(
            "v7 catalogue manifest membership mismatch:\n"
            f"missing entries: {missing}\nunexpected entries: {unexpected}"
        )
    failures = []
    for relative, expected in artifacts.items():
        path = ROOT / relative
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "MISSING"
        if actual != expected:
            failures.append(f"{relative}: expected {expected}, found {actual}")
    if failures:
        raise AssertionError("v7 catalogue manifest hash mismatch:\n" + "\n".join(failures))


def verify_reproduction() -> None:
    for name, frame in build_outputs().items():
        assert_csv_reproduction(OUTPUTS[name], frame)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reproduce", action="store_true")
    parser.add_argument("--require-clean", action="store_true")
    args = parser.parse_args()
    if args.require_clean and worktree_status():
        raise AssertionError("v7 catalogue verification requires a clean Git worktree")
    manifest = json.loads(MANIFEST_PATH.read_text())
    verify_manifest_metadata(manifest)
    verify_manifest(manifest)
    if args.reproduce:
        verify_reproduction()
    if args.require_clean and worktree_status():
        raise AssertionError("v7 catalogue verification changed the Git worktree")
    mode = "hashes and in-memory reproduction" if args.reproduce else "artifact hashes"
    print(f"Verified {manifest['catalogue_release']} {mode}; no artifact was written")


if __name__ == "__main__":
    main()
