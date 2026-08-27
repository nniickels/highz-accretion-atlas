"""Generate the non-breaking v3 JADES + CEERS/RUBIES BLAGN release."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.v3_catalogue import build_v3_catalogues, validate_taylor_raw


PROJECT_ROOT = Path(__file__).resolve().parents[1]
V1_PROCESSED_PATH = PROJECT_ROOT / "data/processed/v1/v1_processed.csv"
TAYLOR_RAW_PATH = PROJECT_ROOT / "data" / "raw" / "taylor24_ceers_rubies_blagn_table1.csv"
LINK_PATH = PROJECT_ROOT / "data/crossmatch/v3/v3_measurement_object_links.csv"
MEASUREMENT_OUTPUT_PATH = PROJECT_ROOT / "data/processed/v3/v3_blagn_measurements.csv"
OBJECT_OUTPUT_PATH = PROJECT_ROOT / "data/processed/v3/v3_blagn_objects.csv"


def main() -> None:
    v1 = pd.read_csv(V1_PROCESSED_PATH)
    taylor_raw = pd.read_csv(TAYLOR_RAW_PATH)
    links = pd.read_csv(LINK_PATH)

    validated_taylor = validate_taylor_raw(taylor_raw)
    measurements, objects = build_v3_catalogues(v1, validated_taylor, links)

    MEASUREMENT_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    measurements.to_csv(MEASUREMENT_OUTPUT_PATH, index=False)
    objects.to_csv(OBJECT_OUTPUT_PATH, index=False)

    filtered_taylor = measurements[measurements["source_key"].eq("taylor24_ceers_rubies_blagn")]
    print(f"Verified Taylor Table 1: {len(validated_taylor)} measurements")
    print(
        "Taylor z >= 4: "
        f"{len(filtered_taylor)} measurements / {filtered_taylor['physical_object_id'].nunique()} objects"
    )
    print(
        "v3 release: "
        f"{len(measurements)} measurements / {len(objects)} physical objects"
    )
    print(f"Wrote: {MEASUREMENT_OUTPUT_PATH}")
    print(f"Wrote: {OBJECT_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
