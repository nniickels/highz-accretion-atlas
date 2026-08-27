"""Generate the catalogue-only v7.1 XQR-30 extension."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.v7_1_catalogue import build_v7_1_catalogues


ROOT = Path(__file__).resolve().parents[1]
INPUTS = {
    "v7_measurements": ROOT / "data/processed/v7/v7_accreting_measurements.csv",
    "v7_observables": ROOT / "data/processed/v7/v7_source_observables.csv",
    "raw_xqr30": ROOT / "data/raw/xqr30_mazzucchelli23_table1.csv",
    "xqr30_coordinates": ROOT / "data/raw/xqr30_dodorico23_coordinates.csv",
    "identity_overrides": ROOT / "data/crossmatch/v7_1/v7_1_reviewed_identity_overrides.csv",
    "external_identity_audit": ROOT / "data/crossmatch/v7_1/v7_1_external_literature_identity_audit.csv",
}
OUTPUTS = {
    "measurements": ROOT / "data/processed/v7_1/v7_1_accreting_measurements.csv",
    "objects": ROOT / "data/processed/v7_1/v7_1_accreting_objects.csv",
    "host_systems": ROOT / "data/processed/v7_1/v7_1_host_systems.csv",
    "measurement_object_links": ROOT / "data/crossmatch/v7_1/v7_1_measurement_object_links.csv",
    "object_host_links": ROOT / "data/crossmatch/v7_1/v7_1_object_host_links.csv",
    "aliases": ROOT / "data/crossmatch/v7_1/v7_1_object_aliases.csv",
    "reviewed_match_candidates": ROOT / "data/crossmatch/v7_1/v7_1_reviewed_match_candidates.csv",
    "external_literature_identity_audit": ROOT / "data/crossmatch/v7_1/v7_1_released_external_literature_identity_audit.csv",
    "observables": ROOT / "data/processed/v7_1/v7_1_source_observables.csv",
    "strata": ROOT / "data/processed/v7_1/v7_1_catalogue_strata.csv",
}


def build_outputs() -> dict[str, pd.DataFrame]:
    frames = {name: pd.read_csv(path) for name, path in INPUTS.items()}
    return build_v7_1_catalogues(**frames)


def main() -> None:
    outputs = build_outputs()
    for name, frame in outputs.items():
        frame.to_csv(OUTPUTS[name], index=False)
        print(f"Wrote {len(frame):3d} rows: {OUTPUTS[name].relative_to(ROOT)}")
    print(
        "v7.1 catalogue-only layer: 161 measurements / 154 physical objects / "
        "153 host systems; no science rankings or figures generated"
    )


if __name__ == "__main__":
    main()
