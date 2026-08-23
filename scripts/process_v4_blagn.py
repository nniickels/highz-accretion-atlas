"""Generate the non-breaking v4 BLAGN catalogue and identity products."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.v4_catalogue import ASPIRE_SOURCE_KEY, MATTHEE_SOURCE_KEY, build_v4_catalogues


PROJECT_ROOT = Path(__file__).resolve().parents[1]
V3_MEASUREMENTS = PROJECT_ROOT / "data" / "processed" / "v3_blagn_measurements.csv"
MATTHEE_RAW = PROJECT_ROOT / "data" / "raw" / "matthee23_eiger_fresco_blagn_tables1_3.csv"
ASPIRE_RAW = PROJECT_ROOT / "data" / "raw" / "lin24_aspire_blagn_tables1_3.csv"

OUTPUTS = {
    "measurements": PROJECT_ROOT / "data" / "processed" / "v4_blagn_measurements.csv",
    "objects": PROJECT_ROOT / "data" / "processed" / "v4_blagn_objects.csv",
    "links": PROJECT_ROOT / "data" / "crossmatch" / "v4_measurement_object_links.csv",
    "aliases": PROJECT_ROOT / "data" / "crossmatch" / "v4_object_aliases.csv",
    "candidates": PROJECT_ROOT / "data" / "crossmatch" / "v4_reviewed_match_candidates.csv",
}


def build_outputs() -> dict[str, pd.DataFrame]:
    values = build_v4_catalogues(
        pd.read_csv(V3_MEASUREMENTS),
        pd.read_csv(MATTHEE_RAW),
        pd.read_csv(ASPIRE_RAW),
    )
    return dict(zip(OUTPUTS, values, strict=True))


def main() -> None:
    outputs = build_outputs()
    for name, frame in outputs.items():
        OUTPUTS[name].parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(OUTPUTS[name], index=False)
        print(f"Wrote {len(frame):3d} rows: {OUTPUTS[name].relative_to(PROJECT_ROOT)}")

    measurements = outputs["measurements"]
    objects = outputs["objects"]
    print(f"v4 release: {len(measurements)} measurements / {len(objects)} physical objects")
    for source in [MATTHEE_SOURCE_KEY, ASPIRE_SOURCE_KEY]:
        subset = measurements[measurements["source_key"].eq(source)]
        print(f"{source}: {len(subset)} measurements / {subset['physical_object_id'].nunique()} physical objects")
    print("Reviewed cross-paper match: GOODS-S-13971 = GS-204851")


if __name__ == "__main__":
    main()
