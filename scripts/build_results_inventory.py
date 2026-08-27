"""Build a deterministic inventory of release-organized result artifacts."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUTPUT = RESULTS / "results_inventory.csv"
EXCLUDED = {"README.md", OUTPUT.name}


def release_label(path: Path) -> str:
    if len(path.parts) >= 2 and path.parts[0] == "releases":
        return path.parts[1].replace("_", ".")
    match = re.match(r"v(\d+(?:_\d+)?)", path.name)
    if not match:
        match = re.match(r"v(\d+(?:_\d+)?)", path.parts[0])
    return f"v{match.group(1).replace('_', '.')}" if match else "cross_release"


def category(path: Path) -> tuple[str, str]:
    text = path.as_posix()
    if text.endswith("/galleries/compiled_object_grids/grid_inventory.csv"):
        return "table", "compiled_grid_inventory"
    if "/galleries/compiled_object_grids/" in text:
        return "figure", "compiled_all_object_grids"
    if "/galleries/compiled_by_class/" in text:
        return "figure", "compiled_class_growth_grids"
    if text.endswith("/galleries/v7_4_growth_gallery_inventory.csv"):
        return "table", "growth_gallery_inventory"
    if "/figures/main_text/" in text:
        return "figure", "main_text_or_appendix_figures"
    if "parameter_maps" in text:
        return "figure", "per_object_parameter_maps"
    if "seed_redshift_maps" in text:
        return "figure", "per_object_seed_redshift_maps"
    if "growth_tracks" in text:
        return "figure", "per_object_growth_tracks"
    if "3d_tests" in text:
        return "figure", "exploratory_3d"
    if path.suffix.lower() == ".png":
        return "figure", "standalone_figures"
    if path.suffix.lower() == ".csv":
        return "table", "science_tables"
    return "other", "other"


def build_inventory() -> pd.DataFrame:
    rows = []
    for path in sorted(item for item in RESULTS.rglob("*") if item.is_file()):
        relative = path.relative_to(RESULTS)
        if relative.as_posix() in EXCLUDED:
            continue
        artifact_kind, collection = category(relative)
        rows.append({
            "release": release_label(relative),
            "artifact_kind": artifact_kind,
            "collection": collection,
            "path": (Path("results") / relative).as_posix(),
            "size_bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "path_policy": "release_organized_path",
        })
    result = pd.DataFrame(rows).sort_values(
        ["release", "artifact_kind", "collection", "path"],
    ).reset_index(drop=True)
    result.to_csv(OUTPUT, index=False)
    return result


def main() -> None:
    inventory = build_inventory()
    print(f"Indexed {len(inventory)} result artifacts: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
