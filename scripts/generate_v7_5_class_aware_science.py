"""Generate current class-aware science products from the frozen v7.5 catalogue."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.v7_5_science import DEFAULT_N_SAMPLES, DEFAULT_RANDOM_SEED, build_outputs as build


ROOT = Path(__file__).resolve().parents[1]
MEASUREMENTS = ROOT / "data/processed/v7_5/v7_5_accreting_measurements.csv"
OBJECTS = ROOT / "data/processed/v7_5/v7_5_accreting_objects.csv"
OUTPUT_PATHS = {
    "measurement_point_ranking": ROOT / "results/tables/v7_5_class_aware_measurement_point_ranking.csv",
    "object_point_ranking": ROOT / "results/tables/v7_5_class_aware_object_point_ranking.csv",
    "measurement_uncertainty_ranking": ROOT / "results/tables/v7_5_class_aware_measurement_uncertainty_ranking.csv",
    "object_uncertainty_ranking": ROOT / "results/tables/v7_5_class_aware_object_uncertainty_ranking.csv",
    "class_method_summary": ROOT / "results/tables/v7_5_class_aware_class_method_summary.csv",
    "exclusion_audit": ROOT / "results/tables/v7_5_class_aware_exclusion_audit.csv",
    "alternate_measurement_sensitivity": ROOT / "results/tables/v7_5_class_aware_alternate_measurement_sensitivity.csv",
    "science_policy": ROOT / "results/tables/v7_5_class_aware_science_policy.csv",
}


def build_outputs(*, n_samples: int, random_seed: int) -> dict[str, pd.DataFrame]:
    return build(
        pd.read_csv(MEASUREMENTS), pd.read_csv(OBJECTS),
        n_samples=n_samples, random_seed=random_seed,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-samples", type=int, default=DEFAULT_N_SAMPLES)
    parser.add_argument("--seed", type=int, default=DEFAULT_RANDOM_SEED)
    args = parser.parse_args()
    outputs = build_outputs(n_samples=args.n_samples, random_seed=args.seed)
    for name, frame in outputs.items():
        OUTPUT_PATHS[name].parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(OUTPUT_PATHS[name], index=False)
        print(f"Wrote {len(frame):4d} rows: {OUTPUT_PATHS[name].relative_to(ROOT)}")


if __name__ == "__main__":
    main()
