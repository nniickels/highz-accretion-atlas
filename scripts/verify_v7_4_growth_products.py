"""Verify v7.4 growth-product membership, coverage, dimensions, and hashes."""

from __future__ import annotations

import argparse
import json

import pandas as pd
from PIL import Image

from scripts.build_v7_4_growth_manifest import MANIFEST_PATH, expected_artifact_paths
from scripts.generate_v7_4_growth_products import (
    COMPATIBILITY_PATH,
    COVERAGE_PATH,
    GALLERY_INVENTORY_PATH,
    ROOT,
    UNAVAILABLE_PATH,
    load_catalogue,
    verify_outputs,
)
from scripts.release_verification import require_clean_worktree, verify_artifact_manifest


# The largest checked-in contact sheet is intentionally about 105 megapixels.
# Its manifest hash and exact dimensions are verified below before use.
Image.MAX_IMAGE_PIXELS = 120_000_000
EXPECTED_METADATA = {
    "release": "v7.4-growth-visualization",
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
}


def verify_metadata(manifest: dict[str, object]) -> None:
    observed = {key: manifest.get(key) for key in EXPECTED_METADATA}
    if observed != EXPECTED_METADATA:
        raise AssertionError(
            f"v7.4 growth manifest metadata mismatch; expected={EXPECTED_METADATA}, observed={observed}"
        )


def verify_growth_contract() -> None:
    catalogue = load_catalogue()
    coverage = pd.read_csv(COVERAGE_PATH, keep_default_na=False)
    unavailable = pd.read_csv(UNAVAILABLE_PATH)
    compatibility = pd.read_csv(COMPATIBILITY_PATH)
    gallery = pd.read_csv(GALLERY_INVENTORY_PATH, keep_default_na=False)
    verify_outputs(catalogue, coverage, unavailable, compatibility, gallery)

    indexed = gallery.set_index("path")
    for path_text, row in indexed.iterrows():
        path = ROOT / path_text
        if not path.is_file():
            raise AssertionError(f"Missing growth-gallery artifact: {path_text}")
        with Image.open(path) as image:
            if image.format != "PNG" or image.size != (int(row["width_px"]), int(row["height_px"])):
                raise AssertionError(f"Growth-gallery image contract mismatch: {path_text}")
    grids = gallery[gallery["artifact_kind"].eq("compiled_class_grid")]
    if not grids["width_px"].ge(5_000).all() or not grids["height_px"].ge(12_000).all():
        raise AssertionError("Compiled class grids must remain high-resolution and zoomable")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-clean", action="store_true")
    args = parser.parse_args()
    if args.require_clean:
        require_clean_worktree(ROOT, "v7.4 growth products")
    manifest = json.loads(MANIFEST_PATH.read_text())
    verify_metadata(manifest)
    verify_artifact_manifest(
        root=ROOT,
        artifacts=manifest.get("artifacts"),
        expected_paths=expected_artifact_paths(),
        release_label="v7.4 growth products",
    )
    verify_growth_contract()
    if args.require_clean:
        require_clean_worktree(ROOT, "v7.4 growth products")
    print("Verified v7.4 growth-product membership, coverage, dimensions, and hashes")


if __name__ == "__main__":
    main()
