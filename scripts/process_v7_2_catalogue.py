"""Generate the catalogue-only v7.2 GNIRS-50 extension."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.v7_2_catalogue import build_v7_2_catalogues


ROOT = Path(__file__).resolve().parents[1]
INPUTS = {
    "v7_1_measurements": ROOT / "data/processed/v7_1/v7_1_accreting_measurements.csv",
    "v7_1_observables": ROOT / "data/processed/v7_1/v7_1_source_observables.csv",
    "v7_1_aliases": ROOT / "data/crossmatch/v7_1/v7_1_object_aliases.csv",
    "sample_table": ROOT / "data/raw/shen19_gnirs_table1.csv",
    "catalog_table": ROOT / "data/raw/shen19_gnirs_table3.csv",
    "identity_overrides": ROOT / "data/crossmatch/v7_2/v7_2_reviewed_identity_overrides.csv",
}
OUTPUTS = {
    "measurements": ROOT / "data/processed/v7_2/v7_2_accreting_measurements.csv",
    "objects": ROOT / "data/processed/v7_2/v7_2_accreting_objects.csv",
    "host_systems": ROOT / "data/processed/v7_2/v7_2_host_systems.csv",
    "measurement_object_links": ROOT / "data/crossmatch/v7_2/v7_2_measurement_object_links.csv",
    "object_host_links": ROOT / "data/crossmatch/v7_2/v7_2_object_host_links.csv",
    "aliases": ROOT / "data/crossmatch/v7_2/v7_2_object_aliases.csv",
    "reviewed_match_candidates": ROOT / "data/crossmatch/v7_2/v7_2_reviewed_match_candidates.csv",
    "observables": ROOT / "data/processed/v7_2/v7_2_source_observables.csv",
    "strata": ROOT / "data/processed/v7_2/v7_2_catalogue_strata.csv",
}


def build_outputs() -> dict[str, pd.DataFrame]:
    frames = {name: pd.read_csv(path) for name, path in INPUTS.items()}
    return build_v7_2_catalogues(**frames)


def main() -> None:
    outputs = build_outputs()
    for name, frame in outputs.items():
        frame.to_csv(OUTPUTS[name], index=False)
        print(f"Wrote {len(frame):4d} rows: {OUTPUTS[name].relative_to(ROOT)}")
    print(
        "v7.2 catalogue-only layer: 211 measurements / 198 physical objects / "
        "197 host systems; no science rankings or figures generated"
    )


if __name__ == "__main__":
    main()
