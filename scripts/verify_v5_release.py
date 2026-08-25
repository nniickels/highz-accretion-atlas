"""Verify v5 hashes and cross-platform reproduction of every current CSV."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from scripts.generate_v5_blagn_science import OUTPUT_PATHS as SCIENCE_PATHS
from scripts.generate_v5_blagn_science import build_outputs as build_science_outputs
from scripts.process_v5_blagn import OUTPUTS as CATALOGUE_PATHS
from scripts.process_v5_blagn import build_outputs as build_catalogue_outputs
from scripts.reproduction import assert_csv_reproduction, csv_round_trip


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "releases" / "v5-manifest.json"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def worktree_status() -> str:
    return subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def expected_artifact_paths() -> set[str]:
    """Return the exact catalogue and science artifact set for the v5 release."""
    return {
        path.relative_to(ROOT).as_posix()
        for path in (*CATALOGUE_PATHS.values(), *SCIENCE_PATHS.values())
    }


def verify_manifest_membership(manifest: dict[str, object]) -> None:
    artifacts = manifest["artifacts"]
    assert isinstance(artifacts, dict)
    actual = set(artifacts)
    expected = expected_artifact_paths()
    if actual != expected:
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        raise AssertionError(
            "Release-manifest membership mismatch:\n"
            f"missing entries: {missing}\nunexpected entries: {unexpected}"
        )


def verify_manifest_hashes(manifest: dict[str, object]) -> None:
    artifacts = manifest["artifacts"]
    assert isinstance(artifacts, dict)
    failures = []
    for relative, expected in artifacts.items():
        path = ROOT / relative
        actual = sha256_bytes(path.read_bytes()) if path.is_file() else "MISSING"
        if actual != expected:
            failures.append(f"{relative}: expected {expected}, found {actual}")
    if failures:
        raise AssertionError("Release-manifest mismatch:\n" + "\n".join(failures))


def verify_reproduction(manifest: dict[str, object]) -> None:
    catalogue = build_catalogue_outputs()
    for name, frame in catalogue.items():
        assert_csv_reproduction(CATALOGUE_PATHS[name], frame)
    science = build_science_outputs(
        n_samples=int(manifest["monte_carlo_samples"]),
        random_seed=int(manifest["random_seed"]),
        measurements=csv_round_trip(catalogue["measurements"]),
        objects=csv_round_trip(catalogue["objects"]),
    )
    for name, frame in science.items():
        assert_csv_reproduction(SCIENCE_PATHS[name], frame)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reproduce", action="store_true", help="Rebuild all v5 CSVs in memory")
    parser.add_argument("--require-clean", action="store_true", help="Require a clean Git worktree before and after verification")
    args = parser.parse_args()
    if args.require_clean and worktree_status():
        raise AssertionError("Release verification requires a clean Git worktree")
    manifest = json.loads(MANIFEST_PATH.read_text())
    verify_manifest_membership(manifest)
    verify_manifest_hashes(manifest)
    if args.reproduce:
        verify_reproduction(manifest)
    if args.require_clean and worktree_status():
        raise AssertionError("Release verification changed the Git worktree")
    mode = "hashes and cross-platform in-memory reproduction" if args.reproduce else "artifact hashes"
    print(f"Verified {manifest['science_release']} {mode}; no release artifact was written")


if __name__ == "__main__":
    main()
