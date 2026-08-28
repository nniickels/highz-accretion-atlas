"""Verify the organized v7.3 results gallery and high-resolution grid figures."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
from PIL import Image

from scripts.generate_all_object_grid_figures import scenario_sources
from scripts.release_verification import require_clean_worktree, verify_artifact_manifest


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "releases/v7.3-results-gallery-manifest.json"
GRID_DIR = ROOT / "results/past_releases/v7_3/galleries/compiled_object_grids"
RESULTS_INVENTORY = ROOT / "results/results_inventory.csv"
EXPECTED_COUNTS = {
    "parameter_maps": 138,
    "seed_redshift_maps": 23,
    "compiled_grids": 7,
    "panels_across_grids": 161,
    "results_inventory_rows": 881,
}
EXPECTED_GRID_SPEC = {
    "columns": 5,
    "rows": 5,
    "width_px": 6048,
    "height_px": 5648,
    "dpi": 300,
    "format": "lossless_png",
}


def expected_artifact_paths() -> set[str]:
    return {
        *{
            f"results/past_releases/v7_3/galleries/compiled_object_grids/all_objects_{scenario}.png"
            for scenario in scenario_sources()
        },
        "results/past_releases/v7_3/galleries/compiled_object_grids/grid_inventory.csv",
        "results/results_inventory.csv",
    }


def verify_metadata(manifest: dict[str, object]) -> None:
    expected = {
        "release": "v7.3-results-gallery",
        "python": "3.12",
        "source_map_counts": EXPECTED_COUNTS,
        "grid_specification": EXPECTED_GRID_SPEC,
    }
    observed = {key: manifest.get(key) for key in expected}
    if observed != expected:
        raise AssertionError(
            f"v7.3 results-gallery manifest metadata mismatch; expected={expected}, observed={observed}"
        )


def verify_gallery_contract() -> None:
    grid_inventory = pd.read_csv(GRID_DIR / "grid_inventory.csv")
    results_inventory = pd.read_csv(RESULTS_INVENTORY)
    if len(grid_inventory) != 7 or int(grid_inventory["n_object_panels"].sum()) != 161:
        raise AssertionError("Compiled grid inventory must contain seven grids and 161 panels")
    for field, expected in [("width_px", 6048), ("height_px", 5648), ("dpi", 300)]:
        if not grid_inventory[field].eq(expected).all():
            raise AssertionError(f"Compiled grids require {field}={expected}")
    if len(results_inventory) != 881 or not results_inventory["path"].is_unique:
        raise AssertionError("Results inventory must contain 881 unique artifact paths")
    indexed = results_inventory.set_index("path")
    for _, row in grid_inventory.iterrows():
        path = ROOT / row["output_path"]
        with Image.open(path) as image:
            if image.size != (6048, 5648) or image.format != "PNG":
                raise AssertionError(f"Unexpected grid image contract: {path}")
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_hash != row["sha256"] or indexed.loc[row["output_path"], "sha256"] != actual_hash:
            raise AssertionError(f"Grid inventory hash mismatch: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-clean", action="store_true")
    args = parser.parse_args()
    if args.require_clean:
        require_clean_worktree(ROOT, "v7.3 results gallery")
    manifest = json.loads(MANIFEST_PATH.read_text())
    verify_metadata(manifest)
    verify_artifact_manifest(
        root=ROOT, artifacts=manifest.get("artifacts"),
        expected_paths=expected_artifact_paths(), release_label="v7.3 results gallery",
    )
    verify_gallery_contract()
    if args.require_clean:
        require_clean_worktree(ROOT, "v7.3 results gallery")
    print("Verified v7.3-results-gallery membership, hashes, dimensions, and inventories")


if __name__ == "__main__":
    main()
