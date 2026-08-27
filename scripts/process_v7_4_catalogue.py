"""Generate the catalogue-only v7.4 JADES narrow-line AGN extension."""

from __future__ import annotations

from pathlib import Path
import pandas as pd

from src.v7_4_catalogue import build_v7_4_catalogues


ROOT = Path(__file__).resolve().parents[1]
INPUTS = {
    "v7_3_measurements": ROOT / "data/processed/v7_3_accreting_measurements.csv",
    "v7_3_observables": ROOT / "data/processed/v7_3_source_observables.csv",
    "v7_3_aliases": ROOT / "data/crossmatch/v7_3_object_aliases.csv",
    "scholtz_source": ROOT / "data/raw/scholtz25_jades_narrow_line_agn_zge4.csv",
    "identity_overrides": ROOT / "data/crossmatch/v7_4_reviewed_identity_overrides.csv",
}
OUTPUTS = {
    "measurements": ROOT / "data/processed/v7_4_accreting_measurements.csv",
    "objects": ROOT / "data/processed/v7_4_accreting_objects.csv",
    "host_systems": ROOT / "data/processed/v7_4_host_systems.csv",
    "measurement_object_links": ROOT / "data/crossmatch/v7_4_measurement_object_links.csv",
    "object_host_links": ROOT / "data/crossmatch/v7_4_object_host_links.csv",
    "aliases": ROOT / "data/crossmatch/v7_4_object_aliases.csv",
    "reviewed_match_candidates": ROOT / "data/crossmatch/v7_4_reviewed_match_candidates.csv",
    "observables": ROOT / "data/processed/v7_4_source_observables.csv",
    "strata": ROOT / "data/processed/v7_4_catalogue_strata.csv",
}


def build_outputs() -> dict[str, pd.DataFrame]:
    return build_v7_4_catalogues(**{name: pd.read_csv(path) for name, path in INPUTS.items()})


def main() -> None:
    outputs = build_outputs()
    for name, frame in outputs.items():
        frame.to_csv(OUTPUTS[name], index=False)
        print(f"Wrote {len(frame):4d} rows: {OUTPUTS[name].relative_to(ROOT)}")
    print("v7.4: 233 measurements / 218 objects / 217 hosts; 20 Scholtz rows, no added numeric BH masses")


if __name__ == "__main__":
    main()
