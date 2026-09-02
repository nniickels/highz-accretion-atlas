"""Build and verify canonical v1/v2/v3 artifact manifests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from src.datasets import DATASET_SPECS


ROOT = Path(__file__).resolve().parents[2]
RELEASES = ROOT / "releases"
LITERATURE_CUTOFF = "2026-08-27"


def canonical_artifacts(version: str) -> list[Path]:
    """Return the exact public artifact set for one dataset version."""
    roots = (
        ROOT / "data/processed" / version,
        ROOT / "data/crossmatch" / version,
        ROOT / "results" / version,
    )
    paths: list[Path] = []
    for base in roots:
        if not base.is_dir():
            raise FileNotFoundError(f"Missing canonical artifact directory: {base}")
        for path in base.rglob("*"):
            if not path.is_file() or path.name == ".DS_Store":
                continue
            relative = path.relative_to(ROOT)
            if relative.parts[0] == "data" and not path.name.startswith(f"{version}_"):
                continue
            paths.append(path)
    return sorted(paths)


def build_manifest(version: str) -> dict[str, object]:
    spec = DATASET_SPECS[version]
    artifacts = {
        path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in canonical_artifacts(version)
    }
    return {
        "dataset_version": version,
        "catalogue_release": spec.catalogue_release,
        "literature_cutoff": LITERATURE_CUTOFF,
        "expected_measurements": spec.expected_measurements,
        "expected_objects": spec.expected_objects,
        "expected_hosts": spec.expected_hosts,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    }


def manifest_path(version: str) -> Path:
    return RELEASES / f"{version}-dataset-manifest.json"


def write_manifests() -> None:
    for version in DATASET_SPECS:
        manifest = build_manifest(version)
        path = manifest_path(version)
        path.write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n")
        print(f"Wrote {manifest['artifact_count']:4d} artifacts: {path.relative_to(ROOT)}")


def verify_manifest(version: str) -> None:
    path = manifest_path(version)
    expected = json.loads(path.read_text())
    actual = build_manifest(version)
    if expected != actual:
        expected_paths = set(expected.get("artifacts", {}))
        actual_paths = set(actual["artifacts"])
        missing = sorted(expected_paths - actual_paths)
        unexpected = sorted(actual_paths - expected_paths)
        changed = sorted(
            key for key in expected_paths & actual_paths
            if expected["artifacts"][key] != actual["artifacts"][key]
        )
        raise AssertionError(
            f"{version} manifest mismatch; missing={missing[:3]}, "
            f"unexpected={unexpected[:3]}, changed={changed[:3]}"
        )


def main() -> None:
    write_manifests()


if __name__ == "__main__":
    main()
