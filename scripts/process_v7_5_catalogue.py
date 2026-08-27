"""Generate the v7.5 provenance and object-evidence-policy catalogue."""

from __future__ import annotations

from pathlib import Path
import pandas as pd

from src.v7_5_catalogue import build_v7_5_catalogues


ROOT = Path(__file__).resolve().parents[1]
INPUTS = {
    "v7_4_measurements": ROOT / "data/processed/v7_4/v7_4_accreting_measurements.csv",
    "v7_4_observables": ROOT / "data/processed/v7_4/v7_4_source_observables.csv",
    "v7_4_aliases": ROOT / "data/crossmatch/v7_4/v7_4_object_aliases.csv",
    "v7_4_reviewed_candidates": ROOT / "data/crossmatch/v7_4/v7_4_reviewed_match_candidates.csv",
    "scholtz_admitted": ROOT / "data/raw/scholtz25_jades_narrow_line_agn_zge4.csv",
    "scholtz_correction": ROOT / "data/raw/scholtz25_jades_narrow_line_agn_v7_5_correction.csv",
}
FULL_TABLE = ROOT / "data/raw/scholtz25_jades_table_sample_full.tex"
OUTPUTS = {
    "measurements": ROOT / "data/processed/v7_5/v7_5_accreting_measurements.csv",
    "objects": ROOT / "data/processed/v7_5/v7_5_accreting_objects.csv",
    "host_systems": ROOT / "data/processed/v7_5/v7_5_host_systems.csv",
    "measurement_object_links": ROOT / "data/crossmatch/v7_5/v7_5_measurement_object_links.csv",
    "object_host_links": ROOT / "data/crossmatch/v7_5/v7_5_object_host_links.csv",
    "aliases": ROOT / "data/crossmatch/v7_5/v7_5_object_aliases.csv",
    "reviewed_match_candidates": ROOT / "data/crossmatch/v7_5/v7_5_reviewed_match_candidates.csv",
    "observables": ROOT / "data/processed/v7_5/v7_5_source_observables.csv",
    "strata": ROOT / "data/processed/v7_5/v7_5_catalogue_strata.csv",
}


def build_outputs() -> dict[str, pd.DataFrame]:
    frames = {name: pd.read_csv(path) for name, path in INPUTS.items()}
    return build_v7_5_catalogues(
        **frames, scholtz_full_table_path=str(FULL_TABLE),
    )


def main() -> None:
    outputs = build_outputs()
    for path in OUTPUTS.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    for name, frame in outputs.items():
        frame.to_csv(OUTPUTS[name], index=False)
        print(f"Wrote {len(frame):4d} rows: {OUTPUTS[name].relative_to(ROOT)}")
    print("v7.5: 234 measurements / 219 objects / 218 hosts; 171 primary objects")


if __name__ == "__main__":
    main()
