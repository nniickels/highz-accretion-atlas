"""Generate class-aware science products from the frozen v7.2 catalogue."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.v7_2_science import (
    DEFAULT_N_SAMPLES,
    DEFAULT_RANDOM_SEED,
    build_alternate_measurement_sensitivity,
    build_class_method_summary,
    build_exclusion_audit,
    build_point_ranking,
    build_science_policy,
    build_uncertainty_ranking,
    prepare_science_view,
    verify_science_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
MEASUREMENTS = ROOT / "data/processed/v7_2/v7_2_accreting_measurements.csv"
OBJECTS = ROOT / "data/processed/v7_2/v7_2_accreting_objects.csv"
OUTPUT_PATHS = {
    "measurement_point_ranking": ROOT / "results/past_releases/v7_2/tables/v7_2_class_aware_measurement_point_ranking.csv",
    "object_point_ranking": ROOT / "results/past_releases/v7_2/tables/v7_2_class_aware_object_point_ranking.csv",
    "measurement_uncertainty_ranking": ROOT / "results/past_releases/v7_2/tables/v7_2_class_aware_measurement_uncertainty_ranking.csv",
    "object_uncertainty_ranking": ROOT / "results/past_releases/v7_2/tables/v7_2_class_aware_object_uncertainty_ranking.csv",
    "class_method_summary": ROOT / "results/past_releases/v7_2/tables/v7_2_class_aware_class_method_summary.csv",
    "exclusion_audit": ROOT / "results/past_releases/v7_2/tables/v7_2_class_aware_exclusion_audit.csv",
    "alternate_measurement_sensitivity": ROOT / "results/past_releases/v7_2/tables/v7_2_class_aware_alternate_measurement_sensitivity.csv",
    "science_policy": ROOT / "results/past_releases/v7_2/tables/v7_2_class_aware_science_policy.csv",
}


def build_outputs(
    *,
    n_samples: int,
    random_seed: int,
    measurements: pd.DataFrame | None = None,
    objects: pd.DataFrame | None = None,
) -> dict[str, pd.DataFrame]:
    raw_measurements = pd.read_csv(MEASUREMENTS) if measurements is None else measurements
    raw_objects = pd.read_csv(OBJECTS) if objects is None else objects
    measurement_view = prepare_science_view(raw_measurements, view="measurement")
    object_view = prepare_science_view(raw_objects, view="physical_object")
    measurement_point = build_point_ranking(measurement_view)
    object_point = build_point_ranking(object_view)
    outputs = {
        "measurement_point_ranking": measurement_point,
        "object_point_ranking": object_point,
        "measurement_uncertainty_ranking": build_uncertainty_ranking(
            measurement_view, n_samples=n_samples, random_seed=random_seed,
        ),
        "object_uncertainty_ranking": build_uncertainty_ranking(
            object_view, n_samples=n_samples, random_seed=random_seed,
        ),
        "class_method_summary": build_class_method_summary(measurement_point, object_point),
        "exclusion_audit": build_exclusion_audit(raw_measurements, raw_objects),
        "alternate_measurement_sensitivity": build_alternate_measurement_sensitivity(
            raw_measurements, raw_objects,
        ),
        "science_policy": build_science_policy(),
    }
    verify_science_outputs(outputs, n_samples=n_samples)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-samples", type=int, default=DEFAULT_N_SAMPLES)
    parser.add_argument("--seed", type=int, default=DEFAULT_RANDOM_SEED)
    args = parser.parse_args()
    outputs = build_outputs(n_samples=args.n_samples, random_seed=args.seed)
    for name, frame in outputs.items():
        frame.to_csv(OUTPUT_PATHS[name], index=False)
        print(f"Wrote {len(frame):4d} rows: {OUTPUT_PATHS[name].relative_to(ROOT)}")


if __name__ == "__main__":
    main()
