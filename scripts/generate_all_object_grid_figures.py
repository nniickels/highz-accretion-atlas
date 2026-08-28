"""Compile every per-object map into high-resolution, lossless grid figures."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pandas as pd
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUTPUT_DIR = RESULTS / "past_releases/v7_3/galleries/compiled_object_grids"
CATALOGUE = ROOT / "data/processed/v1/v1_processed.csv"
N_COLUMNS = 5
CELL_WIDTH = 1200
CELL_HEIGHT = 1120
GUTTER = 12
BACKGROUND = (255, 255, 255)


def scenario_sources() -> dict[str, Path]:
    base = RESULTS / "past_releases/v1/galleries/parameter_maps"
    return {
        "parameter_spin_minus1_eps0p038_no_merger_boost": base / "spin_minus1_eps0p038/no_merger_boost",
        "parameter_spin_minus1_eps0p038_merger_boost_x2": base / "spin_minus1_eps0p038/merger_boost_x2",
        "parameter_spin_0_eps0p057_no_merger_boost": base / "spin_0_eps0p057/no_merger_boost",
        "parameter_spin_0_eps0p057_merger_boost_x2": base / "spin_0_eps0p057/merger_boost_x2",
        "parameter_spin_plus1_eps0p423_no_merger_boost": base / "spin_plus1_eps0p423/no_merger_boost",
        "parameter_spin_plus1_eps0p423_merger_boost_x2": base / "spin_plus1_eps0p423/merger_boost_x2",
        "seed_redshift_baseline": RESULTS / "past_releases/v1/galleries/seed_redshift_maps",
    }


def expected_stems() -> list[str]:
    catalogue = pd.read_csv(CATALOGUE).sort_values(["redshift", "object_id"])
    return [
        re.sub(r"[^A-Za-z0-9]+", "-", str(measurement_id)).strip("-").lower()
        for measurement_id in catalogue["measurement_id"]
    ]


def ordered_sources(directory: Path, scenario: str) -> list[Path]:
    prefix = "v1_seed_redshift_map_" if scenario == "seed_redshift_baseline" else "v1_parameter_map_"
    by_stem = {
        path.stem.removeprefix(prefix): path
        for path in directory.glob(f"{prefix}*.png")
    }
    stems = expected_stems()
    if set(by_stem) != set(stems):
        missing = sorted(set(stems) - set(by_stem))
        unexpected = sorted(set(by_stem) - set(stems))
        raise ValueError(
            f"{scenario} object-map membership mismatch; missing={missing}, unexpected={unexpected}"
        )
    return [by_stem[stem] for stem in stems]


def make_grid(paths: list[Path], output: Path) -> tuple[int, int]:
    n_rows = (len(paths) + N_COLUMNS - 1) // N_COLUMNS
    width = N_COLUMNS * CELL_WIDTH + (N_COLUMNS - 1) * GUTTER
    height = n_rows * CELL_HEIGHT + (n_rows - 1) * GUTTER
    canvas = Image.new("RGB", (width, height), BACKGROUND)
    for index, path in enumerate(paths):
        with Image.open(path) as source:
            panel = source.convert("RGB")
            panel.thumbnail((CELL_WIDTH, CELL_HEIGHT), Image.Resampling.LANCZOS)
        row, column = divmod(index, N_COLUMNS)
        x = column * (CELL_WIDTH + GUTTER) + (CELL_WIDTH - panel.width) // 2
        y = row * (CELL_HEIGHT + GUTTER) + (CELL_HEIGHT - panel.height) // 2
        canvas.paste(panel, (x, y))
    canvas.save(output, format="PNG", compress_level=9, dpi=(300, 300))
    return canvas.size


def build_grids() -> pd.DataFrame:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    expected_outputs = {
        f"all_objects_{scenario}.png" for scenario in scenario_sources()
    }
    for old in OUTPUT_DIR.glob("all_objects_*.png"):
        if old.name not in expected_outputs:
            raise ValueError(f"Unexpected compiled grid requires review before removal: {old}")
    records = []
    for scenario, directory in scenario_sources().items():
        paths = ordered_sources(directory, scenario)
        output = OUTPUT_DIR / f"all_objects_{scenario}.png"
        width, height = make_grid(paths, output)
        records.append({
            "collection": scenario,
            "output_path": output.relative_to(ROOT).as_posix(),
            "source_directory": directory.relative_to(ROOT).as_posix(),
            "n_object_panels": len(paths),
            "grid_columns": N_COLUMNS,
            "grid_rows": (len(paths) + N_COLUMNS - 1) // N_COLUMNS,
            "width_px": width,
            "height_px": height,
            "dpi": 300,
            "format": "lossless_png",
            "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        })
        print(f"Wrote {width}x{height}: {output.relative_to(ROOT)}")
    index = pd.DataFrame(records)
    index.to_csv(OUTPUT_DIR / "grid_inventory.csv", index=False)
    return index


def main() -> None:
    index = build_grids()
    print(f"Compiled {len(index)} grids containing {int(index['n_object_panels'].sum())} panels")


if __name__ == "__main__":
    main()
