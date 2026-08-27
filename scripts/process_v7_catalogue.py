"""Generate the catalogue-only v7 heterogeneous atlas products."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.v7_catalogue import build_v7_catalogues


ROOT = Path(__file__).resolve().parents[1]
V6_MEASUREMENTS = ROOT / "data/processed/v6/v6_blagn_measurements.csv"
REN_TABLE1 = ROOT / "data/raw/ren25_alpine_cristal_jwst_table1.csv"
REN_TABLE2 = ROOT / "data/raw/ren25_alpine_cristal_jwst_table2_observables.csv"
OUTPUTS = {
    "measurements": ROOT / "data/processed/v7/v7_accreting_measurements.csv",
    "objects": ROOT / "data/processed/v7/v7_accreting_objects.csv",
    "host_systems": ROOT / "data/processed/v7/v7_host_systems.csv",
    "measurement_object_links": ROOT / "data/crossmatch/v7/v7_measurement_object_links.csv",
    "object_host_links": ROOT / "data/crossmatch/v7/v7_object_host_links.csv",
    "aliases": ROOT / "data/crossmatch/v7/v7_object_aliases.csv",
    "reviewed_match_candidates": ROOT / "data/crossmatch/v7/v7_reviewed_match_candidates.csv",
    "observables": ROOT / "data/processed/v7/v7_source_observables.csv",
    "strata": ROOT / "data/processed/v7/v7_catalogue_strata.csv",
}


def build_outputs() -> dict[str, pd.DataFrame]:
    return build_v7_catalogues(
        pd.read_csv(V6_MEASUREMENTS), pd.read_csv(REN_TABLE1), pd.read_csv(REN_TABLE2),
    )


def main() -> None:
    outputs = build_outputs()
    for name, frame in outputs.items():
        frame.to_csv(OUTPUTS[name], index=False)
        print(f"Wrote {len(frame):3d} rows: {OUTPUTS[name].relative_to(ROOT)}")
    print(
        "v7 catalogue-only layer: 119 measurements / 112 physical objects / "
        "111 host systems; no science rankings or figures generated"
    )


if __name__ == "__main__":
    main()
