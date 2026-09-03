"""Build a deterministic inventory of canonical v1/v2/v3 result artifacts."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results"
OUTPUT = RESULTS / "results_inventory.csv"
EXCLUDED = {OUTPUT.name}


def release_label(path: Path) -> str:
    match = re.match(r"v(\d+(?:_\d+)?)", path.name)
    if not match:
        match = re.match(r"v(\d+(?:_\d+)?)", path.parts[0])
    return f"v{match.group(1).replace('_', '.')}" if match else "cross_release"


def category(path: Path) -> tuple[str, str]:
    text = path.as_posix()
    if "gallery/fedd_mass_maps/" in text:
        return "figure", "per_object_fedd_mass_maps"
    if "gallery/seedredshift_mass_maps/" in text:
        return "figure", "per_object_seedredshift_mass_maps"
    if path.suffix.lower() == ".png":
        return "figure", "standalone_figures"
    if path.suffix.lower() == ".csv":
        return "table", "science_tables"
    return "other", "other"


def collect_inventory() -> pd.DataFrame:
    """Return the canonical inventory without modifying the repository."""
    rows = []
    for path in sorted(item for item in RESULTS.rglob("*") if item.is_file()):
        relative = path.relative_to(RESULTS)
        if relative.name == "README.md" or relative.as_posix() in EXCLUDED:
            continue
        artifact_kind, collection = category(relative)
        rows.append({
            "release": release_label(relative),
            "artifact_kind": artifact_kind,
            "collection": collection,
            "path": (Path("results") / relative).as_posix(),
            "size_bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "path_policy": "canonical_dataset_product",
        })
    return pd.DataFrame(rows).sort_values(
        ["release", "artifact_kind", "collection", "path"],
    ).reset_index(drop=True)


def build_inventory() -> pd.DataFrame:
    result = collect_inventory()
    result.to_csv(OUTPUT, index=False)
    return result


def main() -> None:
    inventory = build_inventory()
    print(f"Indexed {len(inventory)} result artifacts: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
