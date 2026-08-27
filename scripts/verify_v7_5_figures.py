"""Verify v7.5 paper figures and inherited complete growth-gallery coverage."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
from PIL import Image

from scripts.generate_v7_5_figures import OUTPUT_PATHS, ROOT, build_gallery_coverage
from scripts.release_verification import relative_artifact_paths, require_clean_worktree, verify_artifact_manifest


MANIFEST_PATH = ROOT / "releases/v7.5-figures-manifest.json"
PARENT_MANIFEST = ROOT / "releases/v7.4-growth-visualization-manifest.json"


def expected_artifact_paths() -> set[str]:
    return relative_artifact_paths(ROOT, OUTPUT_PATHS.values())


def verify_metadata(manifest: dict[str, object]) -> None:
    expected = {
        "release": "v7.5-figures-and-gallery",
        "input_catalogue_release": "v7.5-accreting-atlas-catalogue",
        "input_science_release": "v7.5-class-aware-science",
        "parent_gallery_manifest_sha256": hashlib.sha256(PARENT_MANIFEST.read_bytes()).hexdigest(),
        "counts": {
            "paper_figures": 4, "catalogue_objects": 219,
            "complete_inherited_gallery_objects": 196, "unavailable_objects": 23,
            "inherited_per_object_images": 588, "inherited_compiled_class_grids": 6,
        },
    }
    observed = {key: manifest.get(key) for key in expected}
    if observed != expected:
        raise AssertionError(f"v7.5 figure metadata mismatch; expected={expected}, observed={observed}")


def verify_figure_contract() -> None:
    for name, path in OUTPUT_PATHS.items():
        if name == "gallery_coverage":
            continue
        with Image.open(path) as image:
            if image.format != "PNG" or image.width < 4_000 or image.height < 2_000:
                raise AssertionError(f"v7.5 paper figure is not high-resolution PNG: {path}")
    objects = pd.read_csv(ROOT / "data/processed/v7_5/v7_5_accreting_objects.csv")
    expected = build_gallery_coverage(objects)
    observed = pd.read_csv(OUTPUT_PATHS["gallery_coverage"], keep_default_na=False)
    pd.testing.assert_frame_equal(expected.fillna(""), observed.fillna(""), check_dtype=False)
    inherited = observed[observed["growth_product_status"].eq("complete_inherited_v7_4")]
    for column in ["parameter_map_path", "seed_redshift_map_path", "growth_track_path"]:
        missing = [value for value in inherited[column] if not (ROOT / value).is_file()]
        if missing:
            raise AssertionError(f"Missing inherited gallery paths in {column}: {missing[:3]}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-clean", action="store_true")
    args = parser.parse_args()
    if args.require_clean:
        require_clean_worktree(ROOT, "v7.5 figures")
    manifest = json.loads(MANIFEST_PATH.read_text())
    verify_metadata(manifest)
    verify_artifact_manifest(
        root=ROOT, artifacts=manifest.get("artifacts"),
        expected_paths=expected_artifact_paths(), release_label="v7.5 figures",
    )
    verify_figure_contract()
    if args.require_clean:
        require_clean_worktree(ROOT, "v7.5 figures")
    print("Verified four high-resolution v7.5 figures and complete inherited gallery coverage")


if __name__ == "__main__":
    main()
