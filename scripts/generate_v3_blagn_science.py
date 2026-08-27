"""Generate v3 BLAGN evaluation, ranking, uncertainty, and summary CSVs."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.v3_science import (
    DEFAULT_N_SAMPLES,
    DEFAULT_RANDOM_SEED,
    build_catalogue_summary,
    build_growth_summary,
    build_point_ranking,
    build_uncertainty_ranking,
    build_uncertainty_summaries,
    evaluate_catalogue,
    prepare_catalogue_view,
    verify_v3_outputs,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results/releases/v3/tables"
MEASUREMENT_INPUT = PROJECT_ROOT / "data/processed/v3/v3_blagn_measurements.csv"
OBJECT_INPUT = PROJECT_ROOT / "data/processed/v3/v3_blagn_objects.csv"

OUTPUT_PATHS = {
    "measurement_evaluation": RESULTS_DIR / "v3_blagn_measurement_evaluation.csv",
    "object_evaluation": RESULTS_DIR / "v3_blagn_physical_object_evaluation.csv",
    "measurement_point_ranking": RESULTS_DIR / "v3_blagn_measurement_point_ranking.csv",
    "object_point_ranking": RESULTS_DIR / "v3_blagn_physical_object_point_ranking.csv",
    "measurement_uncertainty_fedd": RESULTS_DIR / "v3_blagn_measurement_uncertainty_fedd.csv",
    "measurement_uncertainty_mseed": RESULTS_DIR / "v3_blagn_measurement_uncertainty_mseed.csv",
    "object_uncertainty_fedd": RESULTS_DIR / "v3_blagn_physical_object_uncertainty_fedd.csv",
    "object_uncertainty_mseed": RESULTS_DIR / "v3_blagn_physical_object_uncertainty_mseed.csv",
    "measurement_uncertainty_ranking": RESULTS_DIR / "v3_blagn_measurement_uncertainty_ranking.csv",
    "object_uncertainty_ranking": RESULTS_DIR / "v3_blagn_physical_object_uncertainty_ranking.csv",
    "catalogue_summary": RESULTS_DIR / "v3_blagn_catalogue_summary.csv",
    "growth_summary": RESULTS_DIR / "v3_blagn_growth_summary.csv",
}


def build_outputs(*, n_samples: int, random_seed: int) -> dict[str, pd.DataFrame]:
    measurement_catalogue = prepare_catalogue_view(pd.read_csv(MEASUREMENT_INPUT), view="measurement")
    object_catalogue = prepare_catalogue_view(pd.read_csv(OBJECT_INPUT), view="physical_object")

    measurement_evaluation = evaluate_catalogue(measurement_catalogue)
    object_evaluation = evaluate_catalogue(object_catalogue)
    measurement_point = build_point_ranking(measurement_catalogue, measurement_evaluation)
    object_point = build_point_ranking(object_catalogue, object_evaluation)

    measurement_fedd, measurement_mseed = build_uncertainty_summaries(
        measurement_catalogue, n_samples=n_samples, random_seed=random_seed
    )
    object_fedd, object_mseed = build_uncertainty_summaries(
        object_catalogue, n_samples=n_samples, random_seed=random_seed
    )
    measurement_uncertainty = build_uncertainty_ranking(
        measurement_point, measurement_fedd, measurement_mseed
    )
    object_uncertainty = build_uncertainty_ranking(object_point, object_fedd, object_mseed)

    return {
        "measurement_evaluation": measurement_evaluation,
        "object_evaluation": object_evaluation,
        "measurement_point_ranking": measurement_point,
        "object_point_ranking": object_point,
        "measurement_uncertainty_fedd": measurement_fedd,
        "measurement_uncertainty_mseed": measurement_mseed,
        "object_uncertainty_fedd": object_fedd,
        "object_uncertainty_mseed": object_mseed,
        "measurement_uncertainty_ranking": measurement_uncertainty,
        "object_uncertainty_ranking": object_uncertainty,
        "catalogue_summary": build_catalogue_summary(measurement_catalogue, object_catalogue),
        "growth_summary": build_growth_summary(measurement_point, object_point),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-samples", type=int, default=DEFAULT_N_SAMPLES)
    parser.add_argument("--seed", type=int, default=DEFAULT_RANDOM_SEED)
    args = parser.parse_args()
    if args.n_samples <= 0:
        raise ValueError("--n-samples must be positive")

    outputs = build_outputs(n_samples=args.n_samples, random_seed=args.seed)
    checks = verify_v3_outputs(outputs, n_samples=args.n_samples)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    for name, frame in outputs.items():
        frame.to_csv(OUTPUT_PATHS[name], index=False)
        print(f"Wrote {len(frame):4d} rows: {OUTPUT_PATHS[name].relative_to(PROJECT_ROOT)}")

    print("Verification checks:")
    for name, passed in checks.items():
        print(f"  {name}: {'PASS' if passed else 'FAIL'}")
    top = outputs["object_uncertainty_ranking"].nsmallest(10, "rank_uncertainty_pressure")
    print("Top physical-object uncertainty-pressure ranks:")
    print(
        top[
            [
                "rank_uncertainty_pressure",
                "physical_object_id",
                "object_id",
                "source_key",
                "redshift",
                "log_mbh_msun",
                "uncertainty_growth_pressure_tier",
                "prob_required_fedd_seed1e2_gt_1_baseline",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
