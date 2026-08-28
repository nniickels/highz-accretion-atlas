"""Verify exact membership and hashes of the canonical v5 paper figures."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "releases" / "v5-figures-manifest.json"
OUTPUT = ROOT / "results/past_releases/v5/figures/main_text"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def worktree_status() -> str:
    return subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def verify_manifest_membership(manifest: dict[str, object]) -> None:
    artifacts = manifest["artifacts"]
    assert isinstance(artifacts, dict)
    expected = set(artifacts)
    actual = {
        path.relative_to(ROOT).as_posix()
        for path in OUTPUT.glob("*.png")
        if path.is_file()
    }
    if actual != expected:
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        raise AssertionError(
            "Figure-manifest membership mismatch:\n"
            f"missing files: {missing}\nunexpected files: {unexpected}"
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
        raise AssertionError("Figure-manifest mismatch:\n" + "\n".join(failures))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-clean", action="store_true",
        help="Require a clean Git worktree before and after verification",
    )
    args = parser.parse_args()
    if args.require_clean and worktree_status():
        raise AssertionError("Figure verification requires a clean Git worktree")
    manifest = json.loads(MANIFEST_PATH.read_text())
    verify_manifest_membership(manifest)
    verify_manifest_hashes(manifest)
    if args.require_clean and worktree_status():
        raise AssertionError("Figure verification changed the Git worktree")
    print(f"Verified {manifest['science_release']} canonical paper-figure membership and hashes")


if __name__ == "__main__":
    main()
