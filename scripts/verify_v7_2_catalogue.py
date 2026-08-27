"""Verify the catalogue-only v7.2 manifest and in-memory reproduction."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import pandas as pd

from scripts.process_v7_2_catalogue import OUTPUTS, build_outputs
from scripts.reproduction import assert_csv_reproduction
from src.v7_2_catalogue import CATALOGUE_RELEASE


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "releases/v7.2-catalogue-manifest.json"
EXPECTED_SCOPE = "catalogue-only GNIRS-50 extension; no v7.2 science rankings or figures"
EXPECTED_PYTHON = "3.12"
EXPECTED_COUNTS = {
    "measurements": 211,
    "physical_objects": 198,
    "host_systems": 197,
    "growth_eligible_measurements": 209,
    "primary_measurements": 182,
    "growth_eligible_physical_objects": 196,
    "primary_physical_objects": 171,
    "measurement_object_links": 211,
    "object_host_links": 198,
    "aliases": 253,
    "reviewed_identity_records": 6,
    "source_observables": 993,
    "gnirs50_measurements": 50,
    "gnirs50_numeric_masses": 49,
    "gnirs50_mgii_primary_measurements": 29,
}
EXPECTED_SOURCE_ARCHIVES = {
    "arXiv:1809.05584v1": "2b4376dc136873c4b8db0e5016568b9b1d4692042f6bb035e61fa8bd76b980ef",
    "CDS J/ApJ/873/35 table1.dat": "40ed1598d8c6d4d4a4aa580c578742f9e0334c26bb9dd762a9a0375231a7239f",
    "CDS J/ApJ/873/35 table3.dat": "e1eae3266b9ccfc966303c6e389e9c16141678199924a67ab4c786fed3240323",
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
    gnirs = measurements["source_key"].eq("shen19_gnirs50")
    return {
        "measurements": len(measurements),
        "physical_objects": measurements["physical_object_id"].nunique(),
        "host_systems": measurements["host_system_id"].nunique(),
        "growth_eligible_measurements": int(measurements["growth_ranking_eligible_flag"].astype(bool).sum()),
        "primary_measurements": int(measurements["primary_growth_ranking_flag"].astype(bool).sum()),
        "growth_eligible_physical_objects": int(objects["growth_ranking_eligible_flag"].astype(bool).sum()),
        "primary_physical_objects": int(objects["primary_growth_ranking_flag"].astype(bool).sum()),
        "measurement_object_links": len(frames["measurement_object_links"]),
        "object_host_links": len(frames["object_host_links"]),
        "aliases": len(frames["aliases"]),
        "reviewed_identity_records": len(frames["reviewed_match_candidates"]),
        "source_observables": len(frames["observables"]),
        "gnirs50_measurements": int(gnirs.sum()),
        "gnirs50_numeric_masses": int(measurements.loc[gnirs, "log_mbh_msun_std"].notna().sum()),
        "gnirs50_mgii_primary_measurements": int(measurements.loc[gnirs, "primary_growth_ranking_flag"].astype(bool).sum()),
    }


def verify_manifest_metadata(manifest: dict[str, object]) -> None:
    expected = {
        "catalogue_release": CATALOGUE_RELEASE,
        "parent_catalogue_release": "v7.1-accreting-atlas-catalogue",
        "scope": EXPECTED_SCOPE,
        "python": EXPECTED_PYTHON,
        "catalogue_counts": EXPECTED_COUNTS,
        "source_archives": EXPECTED_SOURCE_ARCHIVES,
    }
    for field, value in expected.items():
        if manifest.get(field) != value:
            raise AssertionError(
                f"v7.2 catalogue manifest {field} mismatch: expected {value!r}, "
                f"found {manifest.get(field)!r}"
            )
    observed = observed_catalogue_counts()
    if observed != EXPECTED_COUNTS:
        raise AssertionError(
            f"v7.2 checked-in catalogue counts mismatch: expected {EXPECTED_COUNTS!r}, "
            f"found {observed!r}"
        )


def verify_manifest(manifest: dict[str, object]) -> None:
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        raise AssertionError("v7.2 catalogue manifest artifacts must be an object")
    expected_paths = expected_artifact_paths()
    if set(artifacts) != expected_paths:
        raise AssertionError(
            f"v7.2 manifest membership mismatch; missing={sorted(expected_paths - set(artifacts))}, "
            f"unexpected={sorted(set(artifacts) - expected_paths)}"
        )
    failures = []
    for relative, expected in artifacts.items():
        path = ROOT / relative
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "MISSING"
        if actual != expected:
            failures.append(f"{relative}: expected {expected}, found {actual}")
    if failures:
        raise AssertionError("v7.2 catalogue manifest hash mismatch:\n" + "\n".join(failures))


def verify_reproduction() -> None:
    for name, frame in build_outputs().items():
        assert_csv_reproduction(OUTPUTS[name], frame)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reproduce", action="store_true")
    parser.add_argument("--require-clean", action="store_true")
    args = parser.parse_args()
    if args.require_clean and worktree_status():
        raise AssertionError("v7.2 catalogue verification requires a clean Git worktree")
    manifest = json.loads(MANIFEST_PATH.read_text())
    verify_manifest_metadata(manifest)
    verify_manifest(manifest)
    if args.reproduce:
        verify_reproduction()
    if args.require_clean and worktree_status():
        raise AssertionError("v7.2 catalogue verification changed the Git worktree")
    mode = "hashes and in-memory reproduction" if args.reproduce else "artifact hashes"
    print(f"Verified {manifest['catalogue_release']} {mode}; no artifact was written")


if __name__ == "__main__":
    main()
