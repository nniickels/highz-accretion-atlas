"""Shared non-writing helpers for immutable release verification."""

from __future__ import annotations

import hashlib
import subprocess
from collections.abc import Iterable, Mapping
from pathlib import Path


def worktree_status(root: Path) -> str:
    return subprocess.run(
        ["git", "status", "--porcelain"], cwd=root, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def relative_artifact_paths(root: Path, paths: Iterable[Path]) -> set[str]:
    return {path.relative_to(root).as_posix() for path in paths}


def verify_artifact_manifest(
    *,
    root: Path,
    artifacts: object,
    expected_paths: set[str],
    release_label: str,
) -> None:
    """Require exact membership and byte hashes for a release artifact map."""
    if not isinstance(artifacts, Mapping):
        raise AssertionError(f"{release_label} manifest artifacts must be an object")
    actual_paths = set(artifacts)
    if actual_paths != expected_paths:
        missing = sorted(expected_paths - actual_paths)
        unexpected = sorted(actual_paths - expected_paths)
        raise AssertionError(
            f"{release_label} manifest membership mismatch:\n"
            f"missing entries: {missing}\nunexpected entries: {unexpected}"
        )
    failures = []
    for relative, expected in artifacts.items():
        path = root / relative
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "MISSING"
        if actual != expected:
            failures.append(f"{relative}: expected {expected}, found {actual}")
    if failures:
        raise AssertionError(
            f"{release_label} manifest hash mismatch:\n" + "\n".join(failures)
        )


def require_clean_worktree(root: Path, release_label: str) -> None:
    if worktree_status(root):
        raise AssertionError(f"{release_label} verification requires a clean Git worktree")
