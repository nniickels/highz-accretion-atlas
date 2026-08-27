"""Generate the catalogue-only v7.3 UHZ1 X-ray evidence-history extension."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.v7_3_catalogue import build_v7_3_catalogues


ROOT = Path(__file__).resolve().parents[1]
INPUTS = {
    "v7_2_measurements": ROOT / "data/processed/v7_2/v7_2_accreting_measurements.csv",
    "v7_2_observables": ROOT / "data/processed/v7_2/v7_2_source_observables.csv",
    "v7_2_aliases": ROOT / "data/crossmatch/v7_2/v7_2_object_aliases.csv",
    "uhz1_history": ROOT / "data/raw/uhz1_xray_evidence_history.csv",
    "miri_table3": ROOT / "data/raw/zou26_uhz1_miri_table3.csv",
}
OUTPUTS = {
    "measurements": ROOT / "data/processed/v7_3/v7_3_accreting_measurements.csv",
    "objects": ROOT / "data/processed/v7_3/v7_3_accreting_objects.csv",
    "host_systems": ROOT / "data/processed/v7_3/v7_3_host_systems.csv",
    "measurement_object_links": ROOT / "data/crossmatch/v7_3/v7_3_measurement_object_links.csv",
    "object_host_links": ROOT / "data/crossmatch/v7_3/v7_3_object_host_links.csv",
    "aliases": ROOT / "data/crossmatch/v7_3/v7_3_object_aliases.csv",
    "reviewed_match_candidates": ROOT / "data/crossmatch/v7_3/v7_3_reviewed_match_candidates.csv",
    "observables": ROOT / "data/processed/v7_3/v7_3_source_observables.csv",
    "strata": ROOT / "data/processed/v7_3/v7_3_catalogue_strata.csv",
}


def build_outputs() -> dict[str, pd.DataFrame]:
    return build_v7_3_catalogues(**{
        name: pd.read_csv(path) for name, path in INPUTS.items()
    })


def main() -> None:
    outputs = build_outputs()
    for name, frame in outputs.items():
        frame.to_csv(OUTPUTS[name], index=False)
        print(f"Wrote {len(frame):4d} rows: {OUTPUTS[name].relative_to(ROOT)}")
    print(
        "v7.3 catalogue-only layer: 213 measurements / 199 physical objects / "
        "198 host systems; UHZ1 remains growth-ineligible without a canonical numeric mass"
    )


if __name__ == "__main__":
    main()
