"""Generate the v5 Harikane measurement-version BLAGN catalogue."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.v5_catalogue import build_v5_catalogues


ROOT = Path(__file__).resolve().parents[1]
V4_MEASUREMENTS = ROOT / "data/processed/v4/v4_blagn_measurements.csv"
HARIKANE_RAW = ROOT / "data/raw/harikane23_nirspec_blagn_tables1_3.csv"
OVERRIDES = ROOT / "data/crossmatch/v5/v5_reviewed_identity_overrides.csv"
OUTPUTS = {
    "measurements": ROOT / "data/processed/v5/v5_blagn_measurements.csv",
    "objects": ROOT / "data/processed/v5/v5_blagn_objects.csv",
    "links": ROOT / "data/crossmatch/v5/v5_measurement_object_links.csv",
    "aliases": ROOT / "data/crossmatch/v5/v5_object_aliases.csv",
    "candidates": ROOT / "data/crossmatch/v5/v5_reviewed_match_candidates.csv",
}


def build_outputs() -> dict[str, pd.DataFrame]:
    values = build_v5_catalogues(
        pd.read_csv(V4_MEASUREMENTS), pd.read_csv(HARIKANE_RAW), pd.read_csv(OVERRIDES),
    )
    return dict(zip(OUTPUTS, values, strict=True))


def main() -> None:
    outputs = build_outputs()
    for name, frame in outputs.items():
        frame.to_csv(OUTPUTS[name], index=False)
        print(f"Wrote {len(frame):3d} rows: {OUTPUTS[name].relative_to(ROOT)}")
    print("v5 release: 106 measurements / 99 physical objects; 5 Harikane overlaps / 5 new objects")


if __name__ == "__main__":
    main()

