"""Generate the v6 THRILS same-class BLAGN catalogue."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.v6_catalogue import build_v6_catalogues


ROOT = Path(__file__).resolve().parents[1]
V5_MEASUREMENTS = ROOT / "data/processed/v5/v5_blagn_measurements.csv"
THRILS_RAW = ROOT / "data/raw/davis26_thrils_blagn_table5.csv"
OUTPUTS = {
    "measurements": ROOT / "data/processed/v6/v6_blagn_measurements.csv",
    "objects": ROOT / "data/processed/v6/v6_blagn_objects.csv",
    "links": ROOT / "data/crossmatch/v6/v6_measurement_object_links.csv",
    "aliases": ROOT / "data/crossmatch/v6/v6_object_aliases.csv",
    "candidates": ROOT / "data/crossmatch/v6/v6_reviewed_match_candidates.csv",
}


def build_outputs() -> dict[str, pd.DataFrame]:
    values = build_v6_catalogues(pd.read_csv(V5_MEASUREMENTS), pd.read_csv(THRILS_RAW))
    return dict(zip(OUTPUTS, values, strict=True))


def main() -> None:
    outputs = build_outputs()
    for name, frame in outputs.items():
        frame.to_csv(OUTPUTS[name], index=False)
        print(f"Wrote {len(frame):3d} rows: {OUTPUTS[name].relative_to(ROOT)}")
    print("v6 release: 112 measurements / 105 physical objects; 6 new THRILS objects")


if __name__ == "__main__":
    main()
