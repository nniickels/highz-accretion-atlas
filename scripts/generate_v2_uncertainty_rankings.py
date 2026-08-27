"""Propagate v1-catalogue mass uncertainty through the v2 diagnostics.

The v2 uncertainty model samples source-reported asymmetric log(MBH) errors
with an equal-side two-piece normal approximation, then applies systematic
mass-shift scenarios.
It writes long-form diagnostic summaries plus an uncertainty-aware ranking table.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.generate_v2_rankings import build_ranking_table, read_inputs
from src.models import required_fedd_for_seed, required_seed_mass_for_growth

RESULTS_DIR = REPO_ROOT / "results/releases/v2/tables"
FEDD_SUMMARY_PATH = RESULTS_DIR / "v2_uncertainty_required_fedd_summary.csv"
MSEED_SUMMARY_PATH = RESULTS_DIR / "v2_uncertainty_required_mseed_summary.csv"
UNCERTAINTY_RANKING_PATH = RESULTS_DIR / "v2_uncertainty_aware_ranking_table.csv"

DEFAULT_RANDOM_SEED = 20260808
DEFAULT_N_SAMPLES = 10000
Z_SEED = 30.0
EPSILON = 0.1
MERGER_BOOST = 1.0
ANALYSIS_RELEASE = "v2"
INPUT_CATALOGUE_RELEASE = "v1"

FIXED_SEED_MASSES = [
    ("seed1e2", "seed_1e2_msun", 2.0, 100.0),
    ("seed1e4", "seed_1e4_msun", 4.0, 10000.0),
    ("seed1e5", "seed_1e5_msun", 5.0, 100000.0),
]

FIXED_GROWTH_HISTORIES = [
    ("fedd0p3", 0.3),
    ("fedd1", 1.0),
]


@dataclass(frozen=True)
class MassShiftScenario:
    name: str
    mbh_delta_dex: float
    label: str


@dataclass(frozen=True)
class MbhUncertaintySpec:
    sigma_plus: float
    sigma_minus: float
    mode: str


MASS_SHIFT_SCENARIOS = [
    MassShiftScenario("baseline", 0.0, "reported MBH"),
    MassShiftScenario("mbh_minus_0p3dex", -0.3, "MBH -0.3 dex"),
    MassShiftScenario("mbh_plus_0p3dex", 0.3, "MBH +0.3 dex"),
]


def resolve_mbh_uncertainty(err_plus: float | None, err_minus: float | None) -> MbhUncertaintySpec:
    """Return the sigma values and provenance mode used for MBH sampling."""
    plus = float(err_plus) if pd.notna(err_plus) else np.nan
    minus = float(err_minus) if pd.notna(err_minus) else np.nan

    if np.isfinite(plus) and plus < 0:
        raise ValueError("MBH uncertainties must be non-negative where finite")
    if np.isfinite(minus) and minus < 0:
        raise ValueError("MBH uncertainties must be non-negative where finite")

    if np.isfinite(plus) and np.isfinite(minus):
        mode = "asymmetric" if not np.isclose(plus, minus) else "symmetric_reported"
        return MbhUncertaintySpec(sigma_plus=plus, sigma_minus=minus, mode=mode)
    if np.isfinite(plus):
        return MbhUncertaintySpec(sigma_plus=plus, sigma_minus=plus, mode="symmetric_from_plus")
    if np.isfinite(minus):
        return MbhUncertaintySpec(sigma_plus=minus, sigma_minus=minus, mode="symmetric_from_minus")
    return MbhUncertaintySpec(sigma_plus=0.0, sigma_minus=0.0, mode="point_estimate_no_reported_mbh_error")


def asymmetric_normal_samples(
    center: float,
    err_plus: float | None,
    err_minus: float | None,
    *,
    n_samples: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Sample an equal-side two-piece normal approximation in log space."""
    spec = resolve_mbh_uncertainty(err_plus, err_minus)

    z = rng.standard_normal(int(n_samples))
    sigma = np.where(z >= 0.0, spec.sigma_plus, spec.sigma_minus)
    return float(center) + z * sigma


def summarize_distribution(values: np.ndarray, *, prefix: str) -> dict[str, float]:
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        raise ValueError("Cannot summarize an empty distribution")
    if not np.isfinite(arr).all():
        raise ValueError(f"{prefix} distribution contains non-finite values")

    p5, p16, p50, p84, p95 = np.percentile(arr, [5, 16, 50, 84, 95])
    return {
        f"{prefix}_p5": float(p5),
        f"{prefix}_p16": float(p16),
        f"{prefix}_p50": float(p50),
        f"{prefix}_p84": float(p84),
        f"{prefix}_p95": float(p95),
    }


def sample_catalogue_mbh(catalogue: pd.DataFrame, *, n_samples: int, random_seed: int) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(int(random_seed))
    samples: dict[str, np.ndarray] = {}
    for _, row in catalogue.sort_values("measurement_id").iterrows():
        samples[str(row["measurement_id"])] = asymmetric_normal_samples(
            row["log_mbh_msun_std"],
            row["log_mbh_err_plus_std"],
            row["log_mbh_err_minus_std"],
            n_samples=n_samples,
            rng=rng,
        )
    return samples


def fedd_summary_rows(
    catalogue: pd.DataFrame,
    mbh_samples_by_id: dict[str, np.ndarray],
    *,
    n_samples: int,
    random_seed: int,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for _, obj in catalogue.iterrows():
        measurement_id = str(obj["measurement_id"])
        base_samples = mbh_samples_by_id[measurement_id]
        uncertainty_spec = resolve_mbh_uncertainty(obj["log_mbh_err_plus_std"], obj["log_mbh_err_minus_std"])
        for scenario in MASS_SHIFT_SCENARIOS:
            shifted_samples = base_samples + scenario.mbh_delta_dex
            mbh_stats = summarize_distribution(shifted_samples, prefix="log_mbh_sample")
            for short_name, seed_label, log_mseed, mseed_msun in FIXED_SEED_MASSES:
                required = required_fedd_for_seed(
                    log_mseed=log_mseed,
                    log_mbh_final=shifted_samples,
                    epsilon=EPSILON,
                    z_seed=Z_SEED,
                    z_obs=float(obj["redshift"]),
                    merger_boost=MERGER_BOOST,
                )
                summary = summarize_distribution(required, prefix="required_fedd")
                prob_required_fedd_gt_1 = float(np.mean(required > 1.0))
                rows.append(
                    {
                        "analysis_release": ANALYSIS_RELEASE,
                        "input_catalogue_release": INPUT_CATALOGUE_RELEASE,
                        "measurement_id": measurement_id,
                        "object_id": obj["object_id"],
                        "redshift": obj["redshift"],
                        "quality_flag": obj["quality_flag"],
                        "detection_evidence": obj["detection_evidence"],
                        "mbh_method": obj["mbh_method"],
                        "edd_ratio_consistency_flag": obj["edd_ratio_consistency_flag"],
                        "edd_ratio_log_residual_dex": obj["edd_ratio_log_residual_dex"],
                        "scenario": scenario.name,
                        "scenario_label": scenario.label,
                        "mbh_delta_dex": scenario.mbh_delta_dex,
                        "n_samples": int(n_samples),
                        "random_seed": int(random_seed),
                        "z_seed": Z_SEED,
                        "epsilon": EPSILON,
                        "merger_boost": MERGER_BOOST,
                        "seed_mass_assumption": seed_label,
                        "seed_mass_short": short_name,
                        "log_mseed_assumption": log_mseed,
                        "mseed_assumption_msun": mseed_msun,
                        "log_mbh_err_plus_reported": obj["log_mbh_err_plus_std"],
                        "log_mbh_err_minus_reported": obj["log_mbh_err_minus_std"],
                        "log_mbh_sigma_plus_used": uncertainty_spec.sigma_plus,
                        "log_mbh_sigma_minus_used": uncertainty_spec.sigma_minus,
                        "mbh_uncertainty_mode": uncertainty_spec.mode,
                        **mbh_stats,
                        **summary,
                        "p_required_fedd_gt1": prob_required_fedd_gt_1,
                        "prob_required_fedd_gt_1": prob_required_fedd_gt_1,
                    }
                )
    return rows


def mseed_summary_rows(
    catalogue: pd.DataFrame,
    mbh_samples_by_id: dict[str, np.ndarray],
    *,
    n_samples: int,
    random_seed: int,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for _, obj in catalogue.iterrows():
        measurement_id = str(obj["measurement_id"])
        base_samples = mbh_samples_by_id[measurement_id]
        uncertainty_spec = resolve_mbh_uncertainty(obj["log_mbh_err_plus_std"], obj["log_mbh_err_minus_std"])
        for scenario in MASS_SHIFT_SCENARIOS:
            shifted_samples = base_samples + scenario.mbh_delta_dex
            mbh_stats = summarize_distribution(shifted_samples, prefix="log_mbh_sample")
            for short_name, f_edd in FIXED_GROWTH_HISTORIES:
                required_log_seed = required_seed_mass_for_growth(
                    log_mbh_final=shifted_samples,
                    f_edd=f_edd,
                    epsilon=EPSILON,
                    z_seed=Z_SEED,
                    z_obs=float(obj["redshift"]),
                    merger_boost=MERGER_BOOST,
                )
                summary = summarize_distribution(required_log_seed, prefix="required_log_mseed")
                linear_summary = summarize_distribution(10.0 ** required_log_seed, prefix="required_mseed_msun")
                prob_required_mseed_gt_1e5 = float(np.mean(required_log_seed > 5.0))
                prob_required_mseed_gt_1e6 = float(np.mean(required_log_seed > 6.0))
                rows.append(
                    {
                        "analysis_release": ANALYSIS_RELEASE,
                        "input_catalogue_release": INPUT_CATALOGUE_RELEASE,
                        "measurement_id": measurement_id,
                        "object_id": obj["object_id"],
                        "redshift": obj["redshift"],
                        "quality_flag": obj["quality_flag"],
                        "detection_evidence": obj["detection_evidence"],
                        "mbh_method": obj["mbh_method"],
                        "edd_ratio_consistency_flag": obj["edd_ratio_consistency_flag"],
                        "edd_ratio_log_residual_dex": obj["edd_ratio_log_residual_dex"],
                        "scenario": scenario.name,
                        "scenario_label": scenario.label,
                        "mbh_delta_dex": scenario.mbh_delta_dex,
                        "n_samples": int(n_samples),
                        "random_seed": int(random_seed),
                        "z_seed": Z_SEED,
                        "epsilon": EPSILON,
                        "merger_boost": MERGER_BOOST,
                        "growth_history": short_name,
                        "f_edd_avg": f_edd,
                        "log_mbh_err_plus_reported": obj["log_mbh_err_plus_std"],
                        "log_mbh_err_minus_reported": obj["log_mbh_err_minus_std"],
                        "log_mbh_sigma_plus_used": uncertainty_spec.sigma_plus,
                        "log_mbh_sigma_minus_used": uncertainty_spec.sigma_minus,
                        "mbh_uncertainty_mode": uncertainty_spec.mode,
                        **mbh_stats,
                        **summary,
                        **linear_summary,
                        "p_required_mseed_gt1e5": prob_required_mseed_gt_1e5,
                        "p_required_mseed_gt1e6": prob_required_mseed_gt_1e6,
                        "prob_required_mseed_gt_1e5": prob_required_mseed_gt_1e5,
                        "prob_required_mseed_gt_1e6": prob_required_mseed_gt_1e6,
                    }
                )
    return rows


def uncertainty_pressure_tier(row: pd.Series) -> str:
    if (
        row["prob_required_fedd_seed1e2_gt_1_baseline"] >= 0.5
        or row["prob_required_mseed_fedd0p3_gt_1e6_baseline"] >= 0.5
    ):
        return "likely_high_pressure"
    if (
        row["prob_required_fedd_seed1e2_gt_1_baseline"] >= 0.16
        or row["prob_required_mseed_fedd0p3_gt_1e6_baseline"] >= 0.16
        or row["prob_required_mseed_fedd0p3_gt_1e5_baseline"] >= 0.5
    ):
        return "possible_high_pressure"
    return "lower_pressure"


def uncertainty_pressure_score(row: pd.Series) -> float:
    probability_component = 100.0 * max(
        row["prob_required_fedd_seed1e2_gt_1_baseline"],
        row["prob_required_mseed_fedd0p3_gt_1e6_baseline"],
        0.5 * row["prob_required_mseed_fedd0p3_gt_1e5_baseline"],
    )
    median_component = float(row["physical_pressure_score_0_100"])
    return float(np.clip(0.7 * probability_component + 0.3 * median_component, 0.0, 100.0))


def uncertainty_followup_category(row: pd.Series) -> str:
    # Source inconsistencies must remain quarantined regardless of the derived
    # pressure or host-ratio tiers; those quantities may depend on the values
    # that require clarification.
    if row["followup_priority_category"] == "D_source_consistency":
        return "D_source_consistency"
    if row["uncertainty_growth_pressure_tier"] == "likely_high_pressure" and row["quality_flag"] == "robust":
        return "A_likely_robust_high_pressure"
    if row["uncertainty_growth_pressure_tier"] == "likely_high_pressure":
        return "B_likely_tentative_high_pressure"
    if row["uncertainty_growth_pressure_tier"] == "possible_high_pressure":
        return "C_uncertain_high_pressure"
    if row["mbh_mstar_tension_label"] == "extreme":
        return "D_host_ratio_tension"
    if row["followup_priority_category"] in {"D_systematics_leverage", "E_comparison_anchor"}:
        return "E_comparison_or_systematics_anchor"
    return "F_context"


def uncertainty_followup_reason(row: pd.Series) -> str:
    if row["uncertainty_followup_category"] == "D_source_consistency":
        return (
            f"{row['object_id']} is {row['quality_flag']} with source-consistency priority "
            f"under baseline assumptions (z_seed=30, epsilon=0.1, no merger): its reported "
            f"Eddington ratio differs from the MBH/Lbol-implied value by "
            f"{row['edd_ratio_log_residual_dex']:.2f} dex; measurement tier="
            f"{row['measurement_confidence_tier']}; requires source clarification."
        )
    return (
        f"{row['object_id']} is {row['quality_flag']} with "
        f"{row['uncertainty_growth_pressure_tier']} under baseline assumptions "
        f"(z_seed=30, epsilon=0.1, no merger): "
        f"prob_required_fedd_seed1e2_gt_1="
        f"{row['prob_required_fedd_seed1e2_gt_1_baseline']:.2f}; "
        f"prob_required_mseed_fedd0p3_gt_1e6="
        f"{row['prob_required_mseed_fedd0p3_gt_1e6_baseline']:.2f}; "
        f"measurement tier={row['measurement_confidence_tier']}."
    )


def build_uncertainty_ranking(
    point_ranking: pd.DataFrame,
    fedd_summary: pd.DataFrame,
    mseed_summary: pd.DataFrame,
) -> pd.DataFrame:
    ranking = point_ranking.copy()
    uncertainty_meta = (
        fedd_summary[
            (fedd_summary["scenario"] == "baseline") & (fedd_summary["seed_mass_short"] == "seed1e2")
        ]
        .set_index("measurement_id")[
            [
                "log_mbh_sigma_plus_used",
                "log_mbh_sigma_minus_used",
                "mbh_uncertainty_mode",
            ]
        ]
    )
    for col in uncertainty_meta.columns:
        ranking[col] = ranking["measurement_id"].map(uncertainty_meta[col])

    for scenario in [scenario.name for scenario in MASS_SHIFT_SCENARIOS]:
        fedd_base = fedd_summary[fedd_summary["scenario"] == scenario]
        for short_name, _, _, _ in FIXED_SEED_MASSES:
            rowset = fedd_base[fedd_base["seed_mass_short"] == short_name].set_index("measurement_id")
            suffix = scenario
            ranking[f"req_fedd_{short_name}_p16_{suffix}"] = ranking["measurement_id"].map(
                rowset["required_fedd_p16"]
            )
            ranking[f"req_fedd_{short_name}_p50_{suffix}"] = ranking["measurement_id"].map(
                rowset["required_fedd_p50"]
            )
            ranking[f"req_fedd_{short_name}_p84_{suffix}"] = ranking["measurement_id"].map(
                rowset["required_fedd_p84"]
            )
            ranking[f"p_req_fedd_{short_name}_gt1_{suffix}"] = ranking["measurement_id"].map(
                rowset["p_required_fedd_gt1"]
            )
            ranking[f"prob_required_fedd_{short_name}_gt_1_{suffix}"] = ranking["measurement_id"].map(
                rowset["prob_required_fedd_gt_1"]
            )

        mseed_base = mseed_summary[mseed_summary["scenario"] == scenario]
        for short_name, _ in FIXED_GROWTH_HISTORIES:
            rowset = mseed_base[mseed_base["growth_history"] == short_name].set_index("measurement_id")
            suffix = scenario
            ranking[f"req_log_mseed_{short_name}_p16_{suffix}"] = ranking["measurement_id"].map(
                rowset["required_log_mseed_p16"]
            )
            ranking[f"req_log_mseed_{short_name}_p50_{suffix}"] = ranking["measurement_id"].map(
                rowset["required_log_mseed_p50"]
            )
            ranking[f"req_log_mseed_{short_name}_p84_{suffix}"] = ranking["measurement_id"].map(
                rowset["required_log_mseed_p84"]
            )
            ranking[f"p_req_log_mseed_{short_name}_gt1e5_{suffix}"] = ranking["measurement_id"].map(
                rowset["p_required_mseed_gt1e5"]
            )
            ranking[f"p_req_log_mseed_{short_name}_gt1e6_{suffix}"] = ranking["measurement_id"].map(
                rowset["p_required_mseed_gt1e6"]
            )
            ranking[f"prob_required_mseed_{short_name}_gt_1e5_{suffix}"] = ranking["measurement_id"].map(
                rowset["prob_required_mseed_gt_1e5"]
            )
            ranking[f"prob_required_mseed_{short_name}_gt_1e6_{suffix}"] = ranking["measurement_id"].map(
                rowset["prob_required_mseed_gt_1e6"]
            )

    ranking["uncertainty_growth_pressure_tier"] = ranking.apply(uncertainty_pressure_tier, axis=1)
    ranking["uncertainty_pressure_score_0_100"] = ranking.apply(uncertainty_pressure_score, axis=1)
    ranking = ranking.sort_values(
        [
            "uncertainty_pressure_score_0_100",
            "prob_required_fedd_seed1e2_gt_1_baseline",
            "prob_required_mseed_fedd0p3_gt_1e6_baseline",
            "redshift",
        ],
        ascending=[False, False, False, False],
    ).reset_index(drop=True)
    ranking["rank_uncertainty_pressure"] = np.arange(1, len(ranking) + 1)
    ranking["uncertainty_followup_category"] = ranking.apply(uncertainty_followup_category, axis=1)
    ranking["uncertainty_followup_reason"] = ranking.apply(uncertainty_followup_reason, axis=1)

    front_columns = [
        "rank_uncertainty_pressure",
        "rank_physical_pressure",
        "measurement_id",
        "object_id",
        "redshift",
        "quality_flag",
        "measurement_confidence_tier",
        "physical_growth_pressure_tier",
        "uncertainty_growth_pressure_tier",
        "followup_priority_category",
        "uncertainty_followup_category",
            "uncertainty_followup_reason",
            "uncertainty_pressure_score_0_100",
            "physical_pressure_score_0_100",
            "prob_required_fedd_seed1e2_gt_1_baseline",
            "prob_required_mseed_fedd0p3_gt_1e5_baseline",
            "prob_required_mseed_fedd0p3_gt_1e6_baseline",
        ]
    return ranking[front_columns + [col for col in ranking.columns if col not in front_columns]]


def verify_outputs(
    point_ranking: pd.DataFrame,
    fedd_summary: pd.DataFrame,
    mseed_summary: pd.DataFrame,
    uncertainty_ranking: pd.DataFrame,
) -> None:
    n_objects = len(point_ranking)
    expected_fedd_rows = n_objects * len(MASS_SHIFT_SCENARIOS) * len(FIXED_SEED_MASSES)
    expected_mseed_rows = n_objects * len(MASS_SHIFT_SCENARIOS) * len(FIXED_GROWTH_HISTORIES)
    source_consistency = uncertainty_ranking["followup_priority_category"].eq("D_source_consistency")

    checks = {
        "fedd_row_count": len(fedd_summary) == expected_fedd_rows,
        "mseed_row_count": len(mseed_summary) == expected_mseed_rows,
        "ranking_row_count": len(uncertainty_ranking) == n_objects,
        "ranking_measurement_id_unique": uncertainty_ranking["measurement_id"].is_unique,
        "source_consistency_followup_preserved": bool(
            uncertainty_ranking.loc[
                source_consistency, "uncertainty_followup_category"
            ].eq("D_source_consistency").all()
        ),
        "valid_fedd_percentiles": (
            fedd_summary["required_fedd_p5"].le(fedd_summary["required_fedd_p16"]).all()
            and fedd_summary["required_fedd_p16"].le(fedd_summary["required_fedd_p50"]).all()
            and fedd_summary["required_fedd_p50"].le(fedd_summary["required_fedd_p84"]).all()
            and fedd_summary["required_fedd_p84"].le(fedd_summary["required_fedd_p95"]).all()
        ),
        "valid_mseed_percentiles": (
            mseed_summary["required_log_mseed_p5"].le(mseed_summary["required_log_mseed_p16"]).all()
            and mseed_summary["required_log_mseed_p16"].le(mseed_summary["required_log_mseed_p50"]).all()
            and mseed_summary["required_log_mseed_p50"].le(mseed_summary["required_log_mseed_p84"]).all()
            and mseed_summary["required_log_mseed_p84"].le(mseed_summary["required_log_mseed_p95"]).all()
        ),
    }

    base = fedd_summary[
        (fedd_summary["scenario"] == "baseline") & (fedd_summary["seed_mass_short"] == "seed1e2")
    ].set_index("measurement_id")
    minus = fedd_summary[
        (fedd_summary["scenario"] == "mbh_minus_0p3dex") & (fedd_summary["seed_mass_short"] == "seed1e2")
    ].set_index("measurement_id")
    plus = fedd_summary[
        (fedd_summary["scenario"] == "mbh_plus_0p3dex") & (fedd_summary["seed_mass_short"] == "seed1e2")
    ].set_index("measurement_id")
    checks["mbh_shift_monotonic_fedd"] = (
        minus["required_fedd_p50"].lt(base["required_fedd_p50"]).all()
        and base["required_fedd_p50"].lt(plus["required_fedd_p50"]).all()
    )

    mbase = mseed_summary[
        (mseed_summary["scenario"] == "baseline") & (mseed_summary["growth_history"] == "fedd0p3")
    ].set_index("measurement_id")
    mminus = mseed_summary[
        (mseed_summary["scenario"] == "mbh_minus_0p3dex") & (mseed_summary["growth_history"] == "fedd0p3")
    ].set_index("measurement_id")
    mplus = mseed_summary[
        (mseed_summary["scenario"] == "mbh_plus_0p3dex") & (mseed_summary["growth_history"] == "fedd0p3")
    ].set_index("measurement_id")
    checks["mbh_shift_monotonic_mseed"] = (
        mminus["required_log_mseed_p50"].lt(mbase["required_log_mseed_p50"]).all()
        and mbase["required_log_mseed_p50"].lt(mplus["required_log_mseed_p50"]).all()
    )

    print("Verified uncertainty products in memory")
    print(f"Rows: f_Edd={len(fedd_summary)}, seed={len(mseed_summary)}, ranking={len(uncertainty_ranking)}")
    print("Sanity checks:")
    for name, passed in checks.items():
        print(f"  {name}: {'PASS' if passed else 'FAIL'}")

    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"Uncertainty verification failed: {failed}")

    cols = [
        "rank_uncertainty_pressure",
        "object_id",
        "quality_flag",
        "uncertainty_growth_pressure_tier",
        "prob_required_fedd_seed1e2_gt_1_baseline",
        "prob_required_mseed_fedd0p3_gt_1e6_baseline",
        "uncertainty_followup_category",
    ]
    print("Top uncertainty-pressure objects:")
    print(uncertainty_ranking.nsmallest(8, "rank_uncertainty_pressure")[cols].to_string(index=False))


def build_outputs(*, n_samples: int, random_seed: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    catalogue, required_fedd, required_mseed = read_inputs()
    point_ranking = build_ranking_table(catalogue, required_fedd, required_mseed)
    mbh_samples = sample_catalogue_mbh(catalogue, n_samples=n_samples, random_seed=random_seed)

    fedd_summary = pd.DataFrame(
        fedd_summary_rows(catalogue, mbh_samples, n_samples=n_samples, random_seed=random_seed)
    )
    mseed_summary = pd.DataFrame(
        mseed_summary_rows(catalogue, mbh_samples, n_samples=n_samples, random_seed=random_seed)
    )
    uncertainty_ranking = build_uncertainty_ranking(point_ranking, fedd_summary, mseed_summary)
    return fedd_summary, mseed_summary, uncertainty_ranking


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-samples", type=int, default=DEFAULT_N_SAMPLES, help="Monte Carlo samples per object")
    parser.add_argument("--seed", type=int, default=DEFAULT_RANDOM_SEED, help="Deterministic random seed")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.n_samples <= 0:
        raise ValueError("--n-samples must be positive")

    fedd_summary, mseed_summary, uncertainty_ranking = build_outputs(
        n_samples=args.n_samples,
        random_seed=args.seed,
    )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fedd_summary.to_csv(FEDD_SUMMARY_PATH, index=False)
    mseed_summary.to_csv(MSEED_SUMMARY_PATH, index=False)
    uncertainty_ranking.to_csv(UNCERTAINTY_RANKING_PATH, index=False)

    print(f"Wrote uncertainty required-f_Edd summary: {FEDD_SUMMARY_PATH.relative_to(REPO_ROOT)}")
    print(f"Wrote uncertainty required-seed summary: {MSEED_SUMMARY_PATH.relative_to(REPO_ROOT)}")
    print(f"Wrote uncertainty-aware ranking table: {UNCERTAINTY_RANKING_PATH.relative_to(REPO_ROOT)}")

    point_ranking = uncertainty_ranking.drop(columns=["rank_uncertainty_pressure"])
    verify_outputs(point_ranking, fedd_summary, mseed_summary, uncertainty_ranking)


if __name__ == "__main__":
    main()
