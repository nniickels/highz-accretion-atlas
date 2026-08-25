"""Generate v5 BLAGN evaluation, ranking, uncertainty, and summary CSVs."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.v5_science import (
    DEFAULT_N_SAMPLES, DEFAULT_RANDOM_SEED, build_alternate_measurement_sensitivity,
    build_catalogue_summary, build_growth_summary, build_point_ranking,
    build_uncertainty_ranking, build_uncertainty_summaries, evaluate_catalogue,
    prepare_catalogue_view, verify_v5_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
MEASUREMENTS = ROOT / "data/processed/v5_blagn_measurements.csv"
OBJECTS = ROOT / "data/processed/v5_blagn_objects.csv"
OUTPUT_PATHS = {
    "measurement_evaluation": RESULTS / "v5_blagn_measurement_evaluation.csv",
    "object_evaluation": RESULTS / "v5_blagn_physical_object_evaluation.csv",
    "measurement_point_ranking": RESULTS / "v5_blagn_measurement_point_ranking.csv",
    "object_point_ranking": RESULTS / "v5_blagn_physical_object_point_ranking.csv",
    "measurement_uncertainty_fedd": RESULTS / "v5_blagn_measurement_uncertainty_fedd.csv",
    "measurement_uncertainty_mseed": RESULTS / "v5_blagn_measurement_uncertainty_mseed.csv",
    "object_uncertainty_fedd": RESULTS / "v5_blagn_physical_object_uncertainty_fedd.csv",
    "object_uncertainty_mseed": RESULTS / "v5_blagn_physical_object_uncertainty_mseed.csv",
    "measurement_uncertainty_ranking": RESULTS / "v5_blagn_measurement_uncertainty_ranking.csv",
    "object_uncertainty_ranking": RESULTS / "v5_blagn_physical_object_uncertainty_ranking.csv",
    "catalogue_summary": RESULTS / "v5_blagn_catalogue_summary.csv",
    "growth_summary": RESULTS / "v5_blagn_growth_summary.csv",
    "alternate_measurement_sensitivity": RESULTS / "v5_blagn_alternate_measurement_sensitivity.csv",
}


def build_outputs(
    *, n_samples: int, random_seed: int,
    measurements: pd.DataFrame | None = None,
    objects: pd.DataFrame | None = None,
) -> dict[str, pd.DataFrame]:
    measurements = prepare_catalogue_view(
        pd.read_csv(MEASUREMENTS) if measurements is None else measurements,
        view="measurement",
    )
    objects = prepare_catalogue_view(
        pd.read_csv(OBJECTS) if objects is None else objects,
        view="physical_object",
    )
    measurement_eval = evaluate_catalogue(measurements)
    object_eval = evaluate_catalogue(objects)
    measurement_point = build_point_ranking(measurements, measurement_eval)
    object_point = build_point_ranking(objects, object_eval)
    measurement_fedd, measurement_mseed = build_uncertainty_summaries(
        measurements, n_samples=n_samples, random_seed=random_seed,
    )
    object_fedd, object_mseed = build_uncertainty_summaries(
        objects, n_samples=n_samples, random_seed=random_seed,
    )
    return {
        "measurement_evaluation": measurement_eval,
        "object_evaluation": object_eval,
        "measurement_point_ranking": measurement_point,
        "object_point_ranking": object_point,
        "measurement_uncertainty_fedd": measurement_fedd,
        "measurement_uncertainty_mseed": measurement_mseed,
        "object_uncertainty_fedd": object_fedd,
        "object_uncertainty_mseed": object_mseed,
        "measurement_uncertainty_ranking": build_uncertainty_ranking(
            measurement_point, measurement_fedd, measurement_mseed,
        ),
        "object_uncertainty_ranking": build_uncertainty_ranking(
            object_point, object_fedd, object_mseed,
        ),
        "catalogue_summary": build_catalogue_summary(measurements, objects),
        "growth_summary": build_growth_summary(measurement_point, object_point),
        "alternate_measurement_sensitivity": build_alternate_measurement_sensitivity(
            measurements, objects, n_samples=n_samples, random_seed=random_seed,
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-samples", type=int, default=DEFAULT_N_SAMPLES)
    parser.add_argument("--seed", type=int, default=DEFAULT_RANDOM_SEED)
    args = parser.parse_args()
    outputs = build_outputs(n_samples=args.n_samples, random_seed=args.seed)
    checks = verify_v5_outputs(outputs, n_samples=args.n_samples)
    for name, frame in outputs.items():
        frame.to_csv(OUTPUT_PATHS[name], index=False)
        print(f"Wrote {len(frame):4d} rows: {OUTPUT_PATHS[name].relative_to(ROOT)}")
    print("Verification: " + ", ".join(f"{name}=PASS" for name in checks))


if __name__ == "__main__":
    main()
