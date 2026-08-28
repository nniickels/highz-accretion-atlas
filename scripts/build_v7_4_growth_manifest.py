"""Build the deterministic manifest for the v7.4 growth-product release."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.generate_v7_4_growth_products import (
    COMPATIBILITY_FIGURE_PATH,
    COMPATIBILITY_PATH,
    COVERAGE_PATH,
    GALLERY_INVENTORY_PATH,
    ROOT,
    UNAVAILABLE_PATH,
    class_slug,
    eligible_objects,
    load_catalogue,
    object_product_paths,
)


MANIFEST_PATH = ROOT / "releases/v7.4-growth-visualization-manifest.json"
RESULTS_INVENTORY = ROOT / "results/results_inventory.csv"


def expected_artifact_paths() -> set[str]:
    eligible = eligible_objects(load_catalogue())
    paths = {
        COVERAGE_PATH,
        UNAVAILABLE_PATH,
        COMPATIBILITY_PATH,
        GALLERY_INVENTORY_PATH,
        COMPATIBILITY_FIGURE_PATH,
        RESULTS_INVENTORY,
    }
    for _, obj in eligible.iterrows():
        paths.update(object_product_paths(obj).values())
    for object_class in sorted(eligible["object_class"].unique()):
        slug = class_slug(object_class)
        for kind in ("parameter_map", "seed_redshift_map", "growth_track"):
            paths.add(
                ROOT / "results/past_releases/v7_4/galleries/compiled_by_class"
                / f"v7_4_all_{slug}_{kind}s.png"
            )
    return {path.relative_to(ROOT).as_posix() for path in paths}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_manifest() -> dict[str, object]:
    expected = expected_artifact_paths()
    missing = sorted(path for path in expected if not (ROOT / path).is_file())
    if missing:
        raise FileNotFoundError(f"Missing v7.4 growth artifacts: {missing}")
    return {
        "release": "v7.4-growth-visualization",
        "scope": "class-stratified growth visualizations for every eligible v7.4 object plus explicit unavailable-object records",
        "python": "3.12",
        "input_catalogue_release": "v7.4-accreting-atlas-catalogue",
        "counts": {
            "catalogue_objects": 218,
            "growth_eligible_objects": 196,
            "growth_unavailable_objects": 22,
            "per_object_parameter_sheets": 196,
            "per_object_seed_redshift_maps": 196,
            "per_object_growth_tracks": 196,
            "compiled_class_grids": 6,
            "compatibility_rows": 288,
            "manifest_artifacts": 600,
        },
        "eligible_class_counts": {
            "broad_line_agn": 112,
            "luminous_quasar_comparison": 84,
        },
        "interpretation_policy": {
            "compatibility_scope": "within_object_class_descriptive_only",
            "pooled_heterogeneous_fraction_allowed": False,
            "missing_mass_inference_allowed": False,
        },
        "artifacts": {path: sha256(ROOT / path) for path in sorted(expected)},
    }


def main() -> None:
    manifest = build_manifest()
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Wrote {len(manifest['artifacts'])} artifact hashes: {MANIFEST_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
