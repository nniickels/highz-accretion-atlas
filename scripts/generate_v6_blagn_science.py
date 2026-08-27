"""Generate v6 BLAGN evaluation, ranking, uncertainty, and summary CSVs."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.v6_science import (
    DEFAULT_N_SAMPLES, DEFAULT_RANDOM_SEED, build_accretion_history_diagnostics,
    build_alternate_measurement_sensitivity,
    build_catalogue_summary, build_growth_summary, build_point_ranking,
    build_primary_ranking_comparison, build_uncertainty_ranking,
    build_uncertainty_summaries, evaluate_catalogue, prepare_catalogue_view,
    verify_v6_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results/releases/v6/tables"
MEASUREMENTS = ROOT / "data/processed/v6/v6_blagn_measurements.csv"
OBJECTS = ROOT / "data/processed/v6/v6_blagn_objects.csv"
OUTPUT_PATHS = {
    "measurement_evaluation": RESULTS / "v6_blagn_measurement_evaluation.csv",
    "object_evaluation": RESULTS / "v6_blagn_physical_object_evaluation.csv",
    "measurement_point_ranking": RESULTS / "v6_blagn_measurement_point_ranking.csv",
    "object_point_ranking": RESULTS / "v6_blagn_physical_object_point_ranking.csv",
    "measurement_uncertainty_fedd": RESULTS / "v6_blagn_measurement_uncertainty_fedd.csv",
    "measurement_uncertainty_mseed": RESULTS / "v6_blagn_measurement_uncertainty_mseed.csv",
    "object_uncertainty_fedd": RESULTS / "v6_blagn_physical_object_uncertainty_fedd.csv",
    "object_uncertainty_mseed": RESULTS / "v6_blagn_physical_object_uncertainty_mseed.csv",
    "measurement_uncertainty_ranking": RESULTS / "v6_blagn_measurement_uncertainty_ranking.csv",
    "object_uncertainty_ranking": RESULTS / "v6_blagn_physical_object_uncertainty_ranking.csv",
    "catalogue_summary": RESULTS / "v6_blagn_catalogue_summary.csv",
    "growth_summary": RESULTS / "v6_blagn_growth_summary.csv",
    "alternate_measurement_sensitivity": RESULTS / "v6_blagn_alternate_measurement_sensitivity.csv",
    "measurement_accretion_history": RESULTS / "v6_blagn_measurement_accretion_history.csv",
    "object_accretion_history": RESULTS / "v6_blagn_physical_object_accretion_history.csv",
    "primary_ranking_comparison": RESULTS / "v6_blagn_primary_ranking_comparison.csv",
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
    measurement_uncertainty = build_uncertainty_ranking(
        measurement_point, measurement_fedd, measurement_mseed,
    )
    object_uncertainty = build_uncertainty_ranking(
        object_point, object_fedd, object_mseed,
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
        "measurement_uncertainty_ranking": measurement_uncertainty,
        "object_uncertainty_ranking": object_uncertainty,
        "catalogue_summary": build_catalogue_summary(measurements, objects),
        "growth_summary": build_growth_summary(measurement_point, object_point),
        "alternate_measurement_sensitivity": build_alternate_measurement_sensitivity(
            measurements, objects, n_samples=n_samples, random_seed=random_seed,
        ),
        "measurement_accretion_history": build_accretion_history_diagnostics(
            measurements, n_samples=n_samples, random_seed=random_seed,
        ),
        "object_accretion_history": build_accretion_history_diagnostics(
            objects, n_samples=n_samples, random_seed=random_seed,
        ),
        "primary_ranking_comparison": build_primary_ranking_comparison(
            object_point, object_uncertainty,
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-samples", type=int, default=DEFAULT_N_SAMPLES)
    parser.add_argument("--seed", type=int, default=DEFAULT_RANDOM_SEED)
    args = parser.parse_args()
    outputs = build_outputs(n_samples=args.n_samples, random_seed=args.seed)
    checks = verify_v6_outputs(outputs, n_samples=args.n_samples)
    for name, frame in outputs.items():
        frame.to_csv(OUTPUT_PATHS[name], index=False)
        print(f"Wrote {len(frame):4d} rows: {OUTPUT_PATHS[name].relative_to(ROOT)}")
    print("Verification: " + ", ".join(f"{name}=PASS" for name in checks))


if __name__ == "__main__":
    main()
