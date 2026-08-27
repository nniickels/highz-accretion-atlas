"""Build a deterministic, categorized inventory without moving frozen results."""

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
    match = re.match(r"v(\d+(?:_\d+)?)", path.name)
    if not match:
        match = re.match(r"v(\d+(?:_\d+)?)", path.parts[0])
    return f"v{match.group(1).replace('_', '.')}" if match else "cross_release"


def category(path: Path) -> tuple[str, str]:
    text = path.as_posix()
    if text == "compiled_object_grids/grid_inventory.csv":
        return "table", "compiled_grid_inventory"
    if text.startswith("compiled_object_grids/"):
        return "figure", "compiled_all_object_grids"
    if "main_text_figures" in text:
        return "figure", "main_text_or_appendix_figures"
    if "parameter_maps" in text:
        return "figure", "per_object_parameter_maps"
    if "seed_redshift_maps" in text:
        return "figure", "per_object_seed_redshift_maps"
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
            "path_policy": (
                "immutable_existing_path" if not relative.as_posix().startswith("compiled_object_grids/")
                else "organized_compilation_path"
            ),
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
