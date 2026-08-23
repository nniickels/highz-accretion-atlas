"""Verify v4.0.1 hashes and optionally reproduce every frozen v4 CSV in memory."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from scripts.generate_v4_blagn_science import OUTPUT_PATHS as SCIENCE_PATHS
from scripts.generate_v4_blagn_science import build_outputs as build_science_outputs
from scripts.process_v4_blagn import OUTPUTS as CATALOGUE_PATHS
from scripts.process_v4_blagn import build_outputs as build_catalogue_outputs


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "releases" / "v4.0.1-manifest.json"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def worktree_status() -> str:
    return subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


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
    expected_hashes = manifest["artifacts"]
    assert isinstance(expected_hashes, dict)
    catalogue = build_catalogue_outputs()
    for name, frame in catalogue.items():
        relative = str(CATALOGUE_PATHS[name].relative_to(ROOT))
        actual = sha256_bytes(frame.to_csv(index=False).encode())
        if actual != expected_hashes[relative]:
            raise AssertionError(f"In-memory catalogue reproduction differs: {relative}")
    science = build_science_outputs(
        n_samples=int(manifest["monte_carlo_samples"]),
        random_seed=int(manifest["random_seed"]),
    )
    for name, frame in science.items():
        relative = str(SCIENCE_PATHS[name].relative_to(ROOT))
        actual = sha256_bytes(frame.to_csv(index=False).encode())
        if actual != expected_hashes[relative]:
            raise AssertionError(f"In-memory science reproduction differs: {relative}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reproduce", action="store_true", help="Rebuild all catalogue and science CSVs in memory")
    parser.add_argument("--require-clean", action="store_true", help="Require a clean Git worktree before and after verification")
    args = parser.parse_args()
    if args.require_clean and worktree_status():
        raise AssertionError("Release verification requires a clean Git worktree")
    manifest = json.loads(MANIFEST_PATH.read_text())
    verify_manifest_hashes(manifest)
    if args.reproduce:
        verify_reproduction(manifest)
    if args.require_clean and worktree_status():
        raise AssertionError("Release verification changed the Git worktree")
    mode = "hashes and in-memory reproduction" if args.reproduce else "artifact hashes"
    print(f"Verified {manifest['maintenance_release']} {mode}; no release artifact was written")


if __name__ == "__main__":
    main()

