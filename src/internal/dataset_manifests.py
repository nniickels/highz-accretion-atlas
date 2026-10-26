"""Build and verify canonical v1/v2/v3 artifact manifests."""

from __future__ import annotations

import hashlib
import json
import csv
from pathlib import Path

from src.datasets import DATASET_SPECS


ROOT = Path(__file__).resolve().parents[2]
MANIFESTS = ROOT / "data/manifests"
LITERATURE_CUTOFF = "2026-09-03"
CATALOGUE_PRODUCT_INPUTS = (
    "data/scenarios/catalogue_growth_comparisons.json",
    "data/publication/identity_exclusions.json",
    "data/publication/evidence_selection.json",
    "data/validation/redshift_identity_checks.json",
    "src/internal/catalogue_products.py",
    "src/internal/publication_selection.py",
    "src/internal/compatibility/v7_science_core.py",
    "src/internal/uncertainty.py",
    "src/internal/early_start_cosmology.py",
    "src/models.py", "src/pbh.py", "src/science.py",
    "src/catalogue_quality.py", "src/standardize_data.py", "src/datasets.py",
    "data/source_provenance_registry.csv",
)


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
    # Shared plots remain covered by every edition that references them.
    coverage = ROOT / 'results' / version / 'tables' / f'{version}_all_object_visual_coverage.csv'
    if coverage.exists():
        with coverage.open() as stream:
            paths.extend(ROOT / row['path'] for row in csv.DictReader(stream) if row['path'])
    from src.internal.shared_results import sensitivity_figure_path
    paths.append(sensitivity_figure_path(ROOT, version))
    return sorted(set(paths))


def build_manifest(version: str) -> dict[str, object]:
    spec = DATASET_SPECS[version]
    artifacts = {
        path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in canonical_artifacts(version)
    }
    manifest = {
        "dataset_version": version,
        "catalogue_release": spec.catalogue_release,
        "literature_cutoff": LITERATURE_CUTOFF,
        "expected_measurements": spec.expected_measurements,
        "expected_objects": spec.expected_objects,
        "expected_hosts": spec.expected_hosts,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    }
    if version == "v3":
        manifest["catalogue_product_inputs_sha256"] = {
            name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in CATALOGUE_PRODUCT_INPUTS
        }
    return manifest


def manifest_path(version: str) -> Path:
    return MANIFESTS / f"{version}-dataset-manifest.json"


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
        expected_inputs = expected.get("catalogue_product_inputs_sha256", {})
        actual_inputs = actual.get("catalogue_product_inputs_sha256", {})
        changed_inputs = sorted(
            key for key in expected_inputs.keys() | actual_inputs.keys()
            if expected_inputs.get(key) != actual_inputs.get(key)
        )
        raise AssertionError(
            f"{version} manifest mismatch; missing={missing[:3]}, "
            f"unexpected={unexpected[:3]}, changed={changed[:3]}, input_changes={changed_inputs[:3]}"
        )


def main() -> None:
    write_manifests()


if __name__ == "__main__":
    main()
