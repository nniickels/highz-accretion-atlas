"""Science evaluation and triage rankings for the v3 BLAGN catalogue.

This module deliberately does not read or write v1 artifacts.  It operates on
the separate v3 measurement and preferred-physical-object catalogue
views and keeps statistical MBH sampling distinct from fixed systematic-shift
scenarios.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Iterable

import numpy as np
import pandas as pd

from scripts.generate_v2_uncertainty_rankings import (
    asymmetric_normal_samples,
    resolve_mbh_uncertainty,
    summarize_distribution,
)
from src import models
from src.v3_catalogue import TAYLOR_SOURCE_KEY


CATALOGUE_RELEASE = "v3-blagn"
Z_SEED = 30.0
EPSILON = 0.1
MERGER_BOOST = 1.0
DEFAULT_RANDOM_SEED = 20260808
DEFAULT_N_SAMPLES = 10000

FIXED_SEEDS = [
    ("seed1e2", 2.0, 100.0),
    ("seed1e4", 4.0, 10_000.0),
    ("seed1e5", 5.0, 100_000.0),
]
FIXED_GROWTH = [("fedd0p3", 0.3), ("fedd1", 1.0)]


@dataclass(frozen=True)
class MassScenario:
    name: str
    label: str
    delta_dex: float
    scope: str
    kind: str


BASE_SCENARIOS = [
    MassScenario("baseline", "reported MBH", 0.0, "all_sources", "none"),
    MassScenario("mbh_minus_0p3dex", "MBH -0.3 dex", -0.3, "all_sources", "global_comparison"),
    MassScenario("mbh_plus_0p3dex", "MBH +0.3 dex", 0.3, "all_sources", "global_comparison"),
]
TAYLOR_SCENARIOS = [
    MassScenario(
        "taylor_virial_minus_0p5dex",
        "Taylor virial calibration sensitivity: MBH -0.5 dex",
        -0.5,
        "taylor24_ceers_rubies_blagn_only",
        "taylor_virial_calibration_sensitivity",
    ),
    MassScenario(
        "taylor_virial_plus_0p5dex",
        "Taylor virial calibration sensitivity: MBH +0.5 dex",
        0.5,
        "taylor24_ceers_rubies_blagn_only",
        "taylor_virial_calibration_sensitivity",
    ),
]

IDENTITY_AND_PROVENANCE_FIELDS = [
    "catalogue_release",
    "catalogue_view",
    "ranking_id",
    "measurement_id",
    "physical_object_id",
    "object_id",
    "n_measurements",
    "available_measurement_ids",
    "preferred_measurement_flag",
    "preferred_measurement_reason",
    "redshift",
    "cosmic_time_gyr",
    "survey",
    "field",
    "object_class",
    "quality_flag",
    "detection_evidence",
    "source_key",
    "source_table",
    "source_paper_version",
    "source_url",
    "source_doi",
    "mbh_method",
    "lrd_flag",
    "lrd_status",
    "halpha_absorption_fit_flag",
    "source_caveat_tags",
    "notes",
]


def _boolish(value: object) -> bool:
    if pd.isna(value):
        return False
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return bool(value)


def _require_columns(df: pd.DataFrame, columns: Iterable[str], label: str) -> None:
    missing = sorted(set(columns) - set(df.columns))
    if missing:
        raise ValueError(f"{label} missing required columns: {missing}")


def _diagnostic_status(row: pd.Series, field: str, diagnostic: str) -> str:
    if pd.notna(row.get(field)):
        return "available"
    if row["source_key"] == TAYLOR_SOURCE_KEY:
        return f"unavailable_not_published_in_taylor_table1:{diagnostic}"
    return f"unavailable_in_source:{diagnostic}"


def prepare_catalogue_view(catalogue: pd.DataFrame, *, view: str) -> pd.DataFrame:
    """Validate and annotate a measurement or physical-object catalogue view."""
    if view not in {"measurement", "physical_object"}:
        raise ValueError("view must be 'measurement' or 'physical_object'")
    _require_columns(
        catalogue,
        [
            "measurement_id",
            "physical_object_id",
            "object_id",
            "redshift",
            "cosmic_time_gyr",
            "source_key",
            "source_table",
            "survey",
            "quality_flag",
            "detection_evidence",
            "log_mbh_msun_std",
            "log_mbh_err_plus_std",
            "log_mbh_err_minus_std",
            "mbh_method",
            "log_mstar_msun_std",
            "log_lbol_erg_s_std",
            "edd_ratio_std",
        ],
        f"expanded {view} catalogue",
    )
    result = catalogue.copy()
    result["catalogue_release"] = CATALOGUE_RELEASE
    result["catalogue_view"] = view
    result["ranking_id"] = result["measurement_id"] if view == "measurement" else result["physical_object_id"]
    if not result["ranking_id"].is_unique:
        raise ValueError(f"{view} ranking_id values must be unique")

    for field in IDENTITY_AND_PROVENANCE_FIELDS:
        if field not in result:
            result[field] = np.nan
    if view == "measurement":
        result["n_measurements"] = 1
        result["available_measurement_ids"] = result["measurement_id"]

    result["lrd_status"] = "not_reported_by_source"
    reported_lrd = result["lrd_flag"].notna()
    result.loc[reported_lrd, "lrd_status"] = np.where(
        result.loc[reported_lrd, "lrd_flag"].map(_boolish), "lrd", "non_lrd"
    )
    result["mstar_diagnostic_status"] = result.apply(
        _diagnostic_status, axis=1, field="log_mstar_msun_std", diagnostic="mstar"
    )
    result["lbol_diagnostic_status"] = result.apply(
        _diagnostic_status, axis=1, field="log_lbol_erg_s_std", diagnostic="lbol"
    )
    result["edd_ratio_diagnostic_status"] = result.apply(
        _diagnostic_status, axis=1, field="edd_ratio_std", diagnostic="edd_ratio"
    )
    return result


def applicable_scenarios(source_key: str) -> list[MassScenario]:
    scenarios = list(BASE_SCENARIOS)
    if source_key == TAYLOR_SOURCE_KEY:
        scenarios.extend(TAYLOR_SCENARIOS)
    return scenarios


def _metadata(row: pd.Series) -> dict[str, object]:
    return {field: row.get(field, np.nan) for field in IDENTITY_AND_PROVENANCE_FIELDS}


def evaluate_catalogue(catalogue: pd.DataFrame) -> pd.DataFrame:
    """Evaluate baseline growth pressure and explicit fixed-mass sensitivities."""
    rows: list[dict[str, object]] = []
    for _, obj in catalogue.iterrows():
        delta_t = float(models.available_growth_time_gyr(Z_SEED, float(obj["redshift"])))
        for scenario in applicable_scenarios(str(obj["source_key"])):
            log_mbh = float(obj["log_mbh_msun_std"]) + scenario.delta_dex
            evaluated: dict[str, object] = {
                **_metadata(obj),
                "scenario": scenario.name,
                "scenario_label": scenario.label,
                "scenario_kind": scenario.kind,
                "scenario_scope": scenario.scope,
                "mbh_delta_dex": scenario.delta_dex,
                "reported_statistical_errors_applied": False,
                "systematic_combined_with_statistical_error": False,
                "z_seed": Z_SEED,
                "epsilon": EPSILON,
                "merger_boost": MERGER_BOOST,
                "delta_t_z30_gyr": delta_t,
                "log_mbh_eval": log_mbh,
                "log_mbh_err_plus_reported": obj["log_mbh_err_plus_std"],
                "log_mbh_err_minus_reported": obj["log_mbh_err_minus_std"],
                "mstar_diagnostic_status": obj["mstar_diagnostic_status"],
                "lbol_diagnostic_status": obj["lbol_diagnostic_status"],
                "edd_ratio_diagnostic_status": obj["edd_ratio_diagnostic_status"],
                "log_mstar_msun": obj["log_mstar_msun_std"],
                "log_lbol_erg_s": obj["log_lbol_erg_s_std"],
                "edd_ratio_reported": obj["edd_ratio_std"],
                "log_mbh_mstar_ratio": obj.get("log_mbh_mstar_ratio", np.nan),
                "edd_ratio_consistency_flag": obj.get("edd_ratio_consistency_flag", "not_evaluable"),
                "edd_ratio_log_residual_dex": obj.get("edd_ratio_log_residual_dex", np.nan),
            }
            for short, log_seed, _ in FIXED_SEEDS:
                evaluated[f"required_fedd_{short}"] = float(
                    models.required_fedd_for_seed(
                        log_seed,
                        log_mbh,
                        EPSILON,
                        Z_SEED,
                        float(obj["redshift"]),
                        merger_boost=MERGER_BOOST,
                    )
                )
            for short, f_edd in FIXED_GROWTH:
                evaluated[f"required_log_mseed_{short}"] = float(
                    models.required_seed_mass_for_growth(
                        log_mbh,
                        f_edd,
                        EPSILON,
                        Z_SEED,
                        float(obj["redshift"]),
                        merger_boost=MERGER_BOOST,
                    )
                )
            rows.append(evaluated)
    return pd.DataFrame(rows)


def _pressure_tier(row: pd.Series) -> str:
    if (
        row["req_fedd_seed1e2_z30_eps0p1_b1"] > 1.0
        or row["req_log_mseed_fedd0p3_z30_eps0p1_b1"] > 6.0
        or (row["req_fedd_seed1e4_z30_eps0p1_b1"] > 0.8 and row["redshift"] > 7.0)
    ):
        return "high"
    if (
        row["req_fedd_seed1e2_z30_eps0p1_b1"] > 0.7
        or row["req_log_mseed_fedd0p3_z30_eps0p1_b1"] > 5.0
        or (row["redshift"] > 7.0 and row["req_fedd_seed1e2_z30_eps0p1_b1"] > 0.8)
    ):
        return "medium"
    return "low"


def _pressure_score(row: pd.Series) -> float:
    light = np.clip((row["req_fedd_seed1e2_z30_eps0p1_b1"] - 0.3) / 1.2, 0.0, 1.0)
    heavy = np.clip((row["req_log_mseed_fedd0p3_z30_eps0p1_b1"] - 4.0) / 2.8, 0.0, 1.0)
    intermediate = np.clip((row["req_fedd_seed1e4_z30_eps0p1_b1"] - 0.3) / 0.7, 0.0, 1.0)
    timing = np.clip((row["redshift"] - 6.0) / 4.0, 0.0, 1.0) * 8.0
    return float(np.clip(100.0 * max(light, heavy, intermediate) + timing, 0.0, 100.0))


def _measurement_confidence(row: pd.Series) -> tuple[str, int]:
    if row["detection_evidence"] == "stack_supported_tentative_hbeta":
        return "low_tentative_stack_supported", 35
    if row.get("edd_ratio_consistency_flag") == "inconsistent":
        return "source_values_internally_inconsistent", 55
    caveats = str(row.get("source_caveat_tags", ""))
    if "possible_outflow_contribution" in caveats or "alternative_non_agn" in caveats:
        return "robust_with_interpretive_caveat", 75
    if "severe_spatially_dependent_slit_loss" in caveats:
        return "robust_with_measurement_caveat", 75
    if str(row["quality_flag"]).lower() == "robust":
        return "high", 90
    return "medium_tentative", 60


def _threshold_high(fedd: float, mseed: float) -> bool:
    return bool(fedd > 1.0 or mseed > 6.0)


def _followup_category(row: pd.Series) -> str:
    if row.get("edd_ratio_consistency_flag") == "inconsistent":
        return "D_source_consistency"
    if row["physical_growth_pressure_tier"] == "high" and row["measurement_confidence_tier"] in {
        "robust_with_interpretive_caveat",
        "robust_with_measurement_caveat",
    }:
        return "B_caveated_high_pressure"
    if row["physical_growth_pressure_tier"] == "high" and row["quality_flag"] == "robust":
        return "A_robust_high_pressure"
    if row["physical_growth_pressure_tier"] == "high":
        return "B_tentative_high_pressure"
    if row["measurement_confidence_tier"] in {
        "robust_with_interpretive_caveat",
        "robust_with_measurement_caveat",
    }:
        return "C_interpretation_or_measurement_check"
    if row["growth_pressure_robustness_0p3"] != "lower_across_0p3_scenarios":
        return "D_systematics_leverage"
    if row["physical_growth_pressure_tier"] == "medium" and row["quality_flag"] == "robust":
        return "E_comparison_anchor"
    return "F_context"


def build_point_ranking(catalogue: pd.DataFrame, evaluation: pd.DataFrame) -> pd.DataFrame:
    """Build one deterministic point-estimate triage row per ranking entity."""
    baseline = evaluation[evaluation["scenario"].eq("baseline")].copy()
    ranking = baseline.rename(
        columns={
            "log_mbh_eval": "log_mbh_msun",
            "required_fedd_seed1e2": "req_fedd_seed1e2_z30_eps0p1_b1",
            "required_fedd_seed1e4": "req_fedd_seed1e4_z30_eps0p1_b1",
            "required_fedd_seed1e5": "req_fedd_seed1e5_z30_eps0p1_b1",
            "required_log_mseed_fedd0p3": "req_log_mseed_fedd0p3_z30_eps0p1_b1",
            "required_log_mseed_fedd1": "req_log_mseed_fedd1_z30_eps0p1_b1",
        }
    )
    keep_eval = [
        "required_fedd_seed1e2",
        "required_log_mseed_fedd0p3",
    ]
    for scenario in [*BASE_SCENARIOS[1:], *TAYLOR_SCENARIOS]:
        subset = evaluation[evaluation["scenario"].eq(scenario.name)].set_index("ranking_id")
        suffix = {
            "mbh_minus_0p3dex": "mbh_minus0p3",
            "mbh_plus_0p3dex": "mbh_plus0p3",
            "taylor_virial_minus_0p5dex": "taylor_virial_minus0p5",
            "taylor_virial_plus_0p5dex": "taylor_virial_plus0p5",
        }[scenario.name]
        for field in keep_eval:
            target = "req_fedd_seed1e2" if field.startswith("required_fedd") else "req_log_mseed_fedd0p3"
            ranking[f"{target}_{suffix}"] = ranking["ranking_id"].map(subset[field])

    ranking["physical_growth_pressure_tier"] = ranking.apply(_pressure_tier, axis=1)
    ranking["physical_pressure_score_0_100"] = ranking.apply(_pressure_score, axis=1)
    down_0p3_high = ranking.apply(
        lambda row: _threshold_high(
            row["req_fedd_seed1e2_mbh_minus0p3"],
            row["req_log_mseed_fedd0p3_mbh_minus0p3"],
        ),
        axis=1,
    )
    base_high = ranking["physical_growth_pressure_tier"].eq("high")
    plus_0p3_high = ranking.apply(
        lambda row: _threshold_high(
            row["req_fedd_seed1e2_mbh_plus0p3"],
            row["req_log_mseed_fedd0p3_mbh_plus0p3"],
        ),
        axis=1,
    )
    ranking["growth_pressure_robustness_0p3"] = np.select(
        [base_high & down_0p3_high, base_high, plus_0p3_high],
        ["robust_high_to_minus0p3", "baseline_high_not_robust_to_minus0p3", "high_only_if_plus0p3"],
        default="lower_across_0p3_scenarios",
    )

    ranking["taylor_virial_sensitivity_label"] = "not_applicable_non_taylor_source"
    is_taylor = ranking["source_key"].eq(TAYLOR_SOURCE_KEY)
    down_0p5_high = (
        ranking["req_fedd_seed1e2_taylor_virial_minus0p5"].gt(1.0)
        | ranking["req_log_mseed_fedd0p3_taylor_virial_minus0p5"].gt(6.0)
    )
    plus_0p5_high = (
        ranking["req_fedd_seed1e2_taylor_virial_plus0p5"].gt(1.0)
        | ranking["req_log_mseed_fedd0p3_taylor_virial_plus0p5"].gt(6.0)
    )
    ranking.loc[is_taylor & base_high & down_0p5_high, "taylor_virial_sensitivity_label"] = (
        "robust_high_to_taylor_minus0p5"
    )
    ranking.loc[is_taylor & base_high & ~down_0p5_high, "taylor_virial_sensitivity_label"] = (
        "baseline_high_not_robust_to_taylor_minus0p5"
    )
    ranking.loc[is_taylor & ~base_high & plus_0p5_high, "taylor_virial_sensitivity_label"] = (
        "high_only_if_taylor_plus0p5"
    )
    ranking.loc[is_taylor & ~base_high & ~plus_0p5_high, "taylor_virial_sensitivity_label"] = (
        "lower_across_taylor_0p5_scenarios"
    )

    confidence = ranking.apply(_measurement_confidence, axis=1)
    ranking["measurement_confidence_tier"] = [value[0] for value in confidence]
    ranking["measurement_confidence_score_0_100"] = [value[1] for value in confidence]
    ranking["missing_diagnostics_penalized_flag"] = False
    ranking["diagnostic_availability_note"] = ranking.apply(
        lambda row: ";".join(
            [
                row["mstar_diagnostic_status"],
                row["lbol_diagnostic_status"],
                row["edd_ratio_diagnostic_status"],
            ]
        ),
        axis=1,
    )
    ranking["followup_priority_category"] = ranking.apply(_followup_category, axis=1)
    category_order = {
        "A_robust_high_pressure": 1,
        "B_caveated_high_pressure": 2,
        "B_tentative_high_pressure": 3,
        "C_interpretation_or_measurement_check": 4,
        "D_source_consistency": 5,
        "D_systematics_leverage": 6,
        "E_comparison_anchor": 7,
        "F_context": 8,
    }
    ranking["_followup_order"] = ranking["followup_priority_category"].map(category_order)
    ranking["ranking_note"] = ranking.apply(
        lambda row: (
            f"Observational-triage rank: {row['physical_growth_pressure_tier']} growth pressure; "
            f"{row['measurement_confidence_tier']} measurement confidence. "
            "This is not evidence for a unique seed channel."
        ),
        axis=1,
    )
    ranking = ranking.sort_values(
        ["physical_pressure_score_0_100", "req_fedd_seed1e2_z30_eps0p1_b1", "redshift", "ranking_id"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)
    ranking["rank_growth_pressure"] = np.arange(1, len(ranking) + 1)
    followup_order = ranking.sort_values(
        ["_followup_order", "physical_pressure_score_0_100", "measurement_confidence_score_0_100", "ranking_id"],
        ascending=[True, False, False, True],
    )["ranking_id"].tolist()
    followup_rank = {ranking_id: rank for rank, ranking_id in enumerate(followup_order, 1)}
    ranking["rank_followup_priority"] = ranking["ranking_id"].map(followup_rank)
    ranking = ranking.drop(columns=["_followup_order"])

    front = [
        "rank_growth_pressure",
        "rank_followup_priority",
        "catalogue_view",
        "ranking_id",
        "measurement_id",
        "physical_object_id",
        "object_id",
        "redshift",
        "source_key",
        "survey",
        "field",
        "lrd_status",
        "log_mbh_msun",
        "physical_growth_pressure_tier",
        "physical_pressure_score_0_100",
        "measurement_confidence_tier",
        "measurement_confidence_score_0_100",
        "followup_priority_category",
    ]
    return ranking[front + [column for column in ranking.columns if column not in front]]


def _rng_for_measurement(random_seed: int, measurement_id: str) -> np.random.Generator:
    digest = hashlib.sha256(f"{int(random_seed)}:{measurement_id}".encode()).digest()
    return np.random.default_rng(int.from_bytes(digest[:8], "little"))


def build_uncertainty_summaries(
    catalogue: pd.DataFrame,
    *,
    n_samples: int = DEFAULT_N_SAMPLES,
    random_seed: int = DEFAULT_RANDOM_SEED,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Sample reported statistical errors, then apply each systematic separately."""
    fedd_rows: list[dict[str, object]] = []
    mseed_rows: list[dict[str, object]] = []
    for _, obj in catalogue.sort_values("ranking_id").iterrows():
        spec = resolve_mbh_uncertainty(obj["log_mbh_err_plus_std"], obj["log_mbh_err_minus_std"])
        rng = _rng_for_measurement(random_seed, str(obj["measurement_id"]))
        base_samples = asymmetric_normal_samples(
            obj["log_mbh_msun_std"],
            obj["log_mbh_err_plus_std"],
            obj["log_mbh_err_minus_std"],
            n_samples=n_samples,
            rng=rng,
        )
        common = {
            **_metadata(obj),
            "n_samples": int(n_samples),
            "random_seed": int(random_seed),
            "z_seed": Z_SEED,
            "epsilon": EPSILON,
            "merger_boost": MERGER_BOOST,
            "reported_statistical_errors_sampled": True,
            "statistical_error_model": "split-normal-in-log-mbh",
            "log_mbh_err_plus_reported": obj["log_mbh_err_plus_std"],
            "log_mbh_err_minus_reported": obj["log_mbh_err_minus_std"],
            "log_mbh_sigma_plus_used": spec.sigma_plus,
            "log_mbh_sigma_minus_used": spec.sigma_minus,
            "mbh_uncertainty_mode": spec.mode,
            "systematic_combined_with_statistical_error": False,
        }
        for scenario in applicable_scenarios(str(obj["source_key"])):
            samples = base_samples + scenario.delta_dex
            scenario_meta = {
                **common,
                "scenario": scenario.name,
                "scenario_label": scenario.label,
                "scenario_kind": scenario.kind,
                "scenario_scope": scenario.scope,
                "mbh_delta_dex": scenario.delta_dex,
                **summarize_distribution(samples, prefix="log_mbh_sample"),
            }
            for short, log_seed, seed_msun in FIXED_SEEDS:
                required = models.required_fedd_for_seed(
                    log_seed,
                    samples,
                    EPSILON,
                    Z_SEED,
                    float(obj["redshift"]),
                    merger_boost=MERGER_BOOST,
                )
                fedd_rows.append(
                    {
                        **scenario_meta,
                        "seed_mass_short": short,
                        "log_mseed_assumption": log_seed,
                        "mseed_assumption_msun": seed_msun,
                        **summarize_distribution(required, prefix="required_fedd"),
                        "prob_required_fedd_gt_1": float(np.mean(required > 1.0)),
                    }
                )
            for short, f_edd in FIXED_GROWTH:
                required_log = models.required_seed_mass_for_growth(
                    samples,
                    f_edd,
                    EPSILON,
                    Z_SEED,
                    float(obj["redshift"]),
                    merger_boost=MERGER_BOOST,
                )
                mseed_rows.append(
                    {
                        **scenario_meta,
                        "growth_history": short,
                        "f_edd_avg": f_edd,
                        **summarize_distribution(required_log, prefix="required_log_mseed"),
                        "prob_required_mseed_gt_1e5": float(np.mean(required_log > 5.0)),
                        "prob_required_mseed_gt_1e6": float(np.mean(required_log > 6.0)),
                    }
                )
    return pd.DataFrame(fedd_rows), pd.DataFrame(mseed_rows)


def build_uncertainty_ranking(
    point_ranking: pd.DataFrame,
    fedd_summary: pd.DataFrame,
    mseed_summary: pd.DataFrame,
) -> pd.DataFrame:
    ranking = point_ranking.copy()
    baseline_fedd = fedd_summary[fedd_summary["scenario"].eq("baseline")]
    baseline_mseed = mseed_summary[mseed_summary["scenario"].eq("baseline")]
    for short, _, _ in FIXED_SEEDS:
        subset = baseline_fedd[baseline_fedd["seed_mass_short"].eq(short)].set_index("ranking_id")
        for metric in ["p16", "p50", "p84"]:
            ranking[f"req_fedd_{short}_{metric}_baseline"] = ranking["ranking_id"].map(
                subset[f"required_fedd_{metric}"]
            )
        ranking[f"prob_required_fedd_{short}_gt_1_baseline"] = ranking["ranking_id"].map(
            subset["prob_required_fedd_gt_1"]
        )
    for short, _ in FIXED_GROWTH:
        subset = baseline_mseed[baseline_mseed["growth_history"].eq(short)].set_index("ranking_id")
        for metric in ["p16", "p50", "p84"]:
            ranking[f"req_log_mseed_{short}_{metric}_baseline"] = ranking["ranking_id"].map(
                subset[f"required_log_mseed_{metric}"]
            )
        for threshold in ["1e5", "1e6"]:
            ranking[f"prob_required_mseed_{short}_gt_{threshold}_baseline"] = ranking["ranking_id"].map(
                subset[f"prob_required_mseed_gt_{threshold}"]
            )

    for scenario in [*BASE_SCENARIOS[1:], *TAYLOR_SCENARIOS]:
        suffix = scenario.name
        fedd = fedd_summary[
            fedd_summary["scenario"].eq(scenario.name) & fedd_summary["seed_mass_short"].eq("seed1e2")
        ].set_index("ranking_id")
        mseed = mseed_summary[
            mseed_summary["scenario"].eq(scenario.name) & mseed_summary["growth_history"].eq("fedd0p3")
        ].set_index("ranking_id")
        ranking[f"req_fedd_seed1e2_p50_{suffix}"] = ranking["ranking_id"].map(fedd["required_fedd_p50"])
        ranking[f"prob_required_fedd_seed1e2_gt_1_{suffix}"] = ranking["ranking_id"].map(
            fedd["prob_required_fedd_gt_1"]
        )
        ranking[f"req_log_mseed_fedd0p3_p50_{suffix}"] = ranking["ranking_id"].map(
            mseed["required_log_mseed_p50"]
        )
        ranking[f"prob_required_mseed_fedd0p3_gt_1e6_{suffix}"] = ranking["ranking_id"].map(
            mseed["prob_required_mseed_gt_1e6"]
        )

    ranking["uncertainty_growth_pressure_tier"] = np.select(
        [
            ranking["prob_required_fedd_seed1e2_gt_1_baseline"].ge(0.5)
            | ranking["prob_required_mseed_fedd0p3_gt_1e6_baseline"].ge(0.5),
            ranking["prob_required_fedd_seed1e2_gt_1_baseline"].ge(0.16)
            | ranking["prob_required_mseed_fedd0p3_gt_1e6_baseline"].ge(0.16)
            | ranking["prob_required_mseed_fedd0p3_gt_1e5_baseline"].ge(0.5),
        ],
        ["likely_high_pressure", "possible_high_pressure"],
        default="lower_pressure",
    )
    probability_component = 100.0 * pd.concat(
        [
            ranking["prob_required_fedd_seed1e2_gt_1_baseline"],
            ranking["prob_required_mseed_fedd0p3_gt_1e6_baseline"],
            0.5 * ranking["prob_required_mseed_fedd0p3_gt_1e5_baseline"],
        ],
        axis=1,
    ).max(axis=1)
    ranking["uncertainty_pressure_score_0_100"] = np.clip(
        0.7 * probability_component + 0.3 * ranking["physical_pressure_score_0_100"],
        0.0,
        100.0,
    )
    ranking = ranking.sort_values(
        [
            "uncertainty_pressure_score_0_100",
            "prob_required_fedd_seed1e2_gt_1_baseline",
            "prob_required_mseed_fedd0p3_gt_1e6_baseline",
            "redshift",
            "ranking_id",
        ],
        ascending=[False, False, False, False, True],
    ).reset_index(drop=True)
    ranking["rank_uncertainty_pressure"] = np.arange(1, len(ranking) + 1)
    front = [
        "rank_uncertainty_pressure",
        "rank_growth_pressure",
        "catalogue_view",
        "ranking_id",
        "measurement_id",
        "physical_object_id",
        "object_id",
        "redshift",
        "source_key",
        "survey",
        "field",
        "lrd_status",
        "uncertainty_growth_pressure_tier",
        "uncertainty_pressure_score_0_100",
        "prob_required_fedd_seed1e2_gt_1_baseline",
        "prob_required_mseed_fedd0p3_gt_1e6_baseline",
        "measurement_confidence_tier",
    ]
    return ranking[front + [column for column in ranking.columns if column not in front]]


def _strata(df: pd.DataFrame) -> list[tuple[str, str, pd.DataFrame]]:
    groups: list[tuple[str, str, pd.DataFrame]] = [("overall", "all", df)]
    for field, stratum_type in [
        ("source_key", "source"),
        ("survey", "survey"),
        ("field", "field"),
        ("lrd_status", "lrd_phenotype"),
    ]:
        values = df[field].astype("string").fillna("not_reported")
        for value in sorted(values.unique()):
            groups.append((stratum_type, str(value), df[values.eq(value)]))
    survey = df["survey"].astype("string").fillna("not_reported")
    field = df["field"].astype("string").fillna("not_reported")
    combined = survey + "/" + field
    for value in sorted(combined.unique()):
        groups.append(("survey_field", str(value), df[combined.eq(value)]))
    return groups


def _selection_note(stratum_type: str) -> str:
    if stratum_type == "overall":
        return "descriptive only: mixes JADES and CEERS/RUBIES selection functions"
    return "descriptive stratum only: no cross-source completeness correction or demographic pooling"


def build_catalogue_summary(measurements: pd.DataFrame, objects: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for view_df in [measurements, objects]:
        view = str(view_df["catalogue_view"].iloc[0])
        for stratum_type, value, group in _strata(view_df):
            n_measurements = int(group["n_measurements"].sum()) if view == "physical_object" else len(group)
            rows.append(
                {
                    "catalogue_release": CATALOGUE_RELEASE,
                    "catalogue_view": view,
                    "stratum_type": stratum_type,
                    "stratum_value": value,
                    "n_rows": len(group),
                    "n_measurements_represented": n_measurements,
                    "n_physical_objects": group["physical_object_id"].nunique(),
                    "redshift_min": group["redshift"].min(),
                    "redshift_max": group["redshift"].max(),
                    "log_mbh_min": group["log_mbh_msun_std"].min(),
                    "log_mbh_median": group["log_mbh_msun_std"].median(),
                    "log_mbh_max": group["log_mbh_msun_std"].max(),
                    "n_lrd": int(group["lrd_status"].eq("lrd").sum()),
                    "n_non_lrd": int(group["lrd_status"].eq("non_lrd").sum()),
                    "n_lrd_not_reported": int(group["lrd_status"].eq("not_reported_by_source").sum()),
                    "stratum_identity_basis": (
                        "measurement-row metadata"
                        if view == "measurement"
                        else "preferred-measurement metadata; n_measurements_represented includes linked alternates"
                    ),
                    "demographic_inference_allowed": False,
                    "selection_function_note": _selection_note(stratum_type),
                }
            )
    return pd.DataFrame(rows)


def build_growth_summary(measurement_ranking: pd.DataFrame, object_ranking: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for ranking in [measurement_ranking, object_ranking]:
        view = str(ranking["catalogue_view"].iloc[0])
        for stratum_type, value, group in _strata(ranking):
            top = group.nsmallest(1, "rank_growth_pressure").iloc[0]
            rows.append(
                {
                    "catalogue_release": CATALOGUE_RELEASE,
                    "catalogue_view": view,
                    "stratum_type": stratum_type,
                    "stratum_value": value,
                    "n_rows": len(group),
                    "n_high_pressure": int(group["physical_growth_pressure_tier"].eq("high").sum()),
                    "n_medium_pressure": int(group["physical_growth_pressure_tier"].eq("medium").sum()),
                    "n_low_pressure": int(group["physical_growth_pressure_tier"].eq("low").sum()),
                    "median_required_fedd_seed1e2": group["req_fedd_seed1e2_z30_eps0p1_b1"].median(),
                    "median_required_log_mseed_fedd0p3": group[
                        "req_log_mseed_fedd0p3_z30_eps0p1_b1"
                    ].median(),
                    "top_ranking_id": top["ranking_id"],
                    "top_object_id": top["object_id"],
                    "top_growth_pressure_score": top["physical_pressure_score_0_100"],
                    "demographic_inference_allowed": False,
                    "selection_function_note": _selection_note(stratum_type),
                    "interpretation_note": (
                        "Growth-pressure rankings are observational triage under stated assumptions; "
                        "they do not identify or prove a black-hole seed channel."
                    ),
                }
            )
    return pd.DataFrame(rows)


def verify_v3_outputs(outputs: dict[str, pd.DataFrame], *, n_samples: int) -> dict[str, bool]:
    measurement_ranking = outputs["measurement_point_ranking"]
    object_ranking = outputs["object_point_ranking"]
    measurement_eval = outputs["measurement_evaluation"]
    object_eval = outputs["object_evaluation"]
    measurement_fedd = outputs["measurement_uncertainty_fedd"]
    object_fedd = outputs["object_uncertainty_fedd"]
    measurement_mseed = outputs["measurement_uncertainty_mseed"]
    object_mseed = outputs["object_uncertainty_mseed"]
    measurement_uncertainty_ranking = outputs["measurement_uncertainty_ranking"]
    object_uncertainty_ranking = outputs["object_uncertainty_ranking"]
    checks = {
        "measurement_rank_count": len(measurement_ranking) == 60,
        "physical_object_rank_count": len(object_ranking) == 59,
        "measurement_ids_unique": measurement_ranking["measurement_id"].is_unique,
        "physical_object_ids_unique": object_ranking["physical_object_id"].is_unique,
        "measurement_evaluation_count": len(measurement_eval) == 254,
        "object_evaluation_count": len(object_eval) == 249,
        "measurement_fedd_uncertainty_count": len(measurement_fedd) == 762,
        "object_fedd_uncertainty_count": len(object_fedd) == 747,
        "measurement_mseed_uncertainty_count": len(measurement_mseed) == 508,
        "object_mseed_uncertainty_count": len(object_mseed) == 498,
        "measurement_uncertainty_rank_count": len(measurement_uncertainty_ranking) == 60,
        "object_uncertainty_rank_count": len(object_uncertainty_ranking) == 59,
        "uncertainty_sample_count": measurement_fedd["n_samples"].eq(int(n_samples)).all(),
        "baseline_assumptions": all(
            frame["z_seed"].eq(Z_SEED).all()
            and frame["epsilon"].eq(EPSILON).all()
            and frame["merger_boost"].eq(MERGER_BOOST).all()
            for frame in [measurement_eval, object_eval, measurement_fedd, object_fedd]
        ),
        "missing_diagnostics_not_penalized": (
            ~measurement_ranking.loc[
                measurement_ranking["source_key"].eq(TAYLOR_SOURCE_KEY),
                "missing_diagnostics_penalized_flag",
            ]
        ).all(),
        "taylor_provenance_present": measurement_ranking.loc[
            measurement_ranking["source_key"].eq(TAYLOR_SOURCE_KEY), "source_doi"
        ].eq("10.3847/1538-4357/add15b").all(),
    }
    duplicate = object_ranking[object_ranking["physical_object_id"].eq("HZA-CEERS-2782")]
    checks["duplicate_counted_once"] = len(duplicate) == 1
    checks["duplicate_preferred_measurement"] = (
        len(duplicate) == 1 and duplicate.iloc[0]["measurement_id"] == "RUBIESEGS50052_taylor24"
    )
    fedd_pivot = measurement_fedd[
        measurement_fedd["seed_mass_short"].eq("seed1e2")
    ].pivot(index="ranking_id", columns="scenario", values="required_fedd_p50")
    checks["global_fedd_scenario_ordering"] = bool(
        (fedd_pivot["mbh_minus_0p3dex"] < fedd_pivot["baseline"]).all()
        and (fedd_pivot["baseline"] < fedd_pivot["mbh_plus_0p3dex"]).all()
    )
    taylor_fedd = fedd_pivot.dropna(subset=["taylor_virial_minus_0p5dex"])
    checks["taylor_fedd_scenario_ordering"] = bool(
        (taylor_fedd["taylor_virial_minus_0p5dex"] < taylor_fedd["mbh_minus_0p3dex"]).all()
        and (taylor_fedd["mbh_plus_0p3dex"] < taylor_fedd["taylor_virial_plus_0p5dex"]).all()
    )
    mseed_pivot = measurement_mseed[
        measurement_mseed["growth_history"].eq("fedd0p3")
    ].pivot(index="ranking_id", columns="scenario", values="required_log_mseed_p50")
    checks["global_mseed_scenario_ordering"] = bool(
        (mseed_pivot["mbh_minus_0p3dex"] < mseed_pivot["baseline"]).all()
        and (mseed_pivot["baseline"] < mseed_pivot["mbh_plus_0p3dex"]).all()
    )
    taylor_mseed = mseed_pivot.dropna(subset=["taylor_virial_minus_0p5dex"])
    checks["taylor_mseed_scenario_ordering"] = bool(
        (taylor_mseed["taylor_virial_minus_0p5dex"] < taylor_mseed["mbh_minus_0p3dex"]).all()
        and (taylor_mseed["mbh_plus_0p3dex"] < taylor_mseed["taylor_virial_plus_0p5dex"]).all()
    )
    failed = [name for name, passed in checks.items() if not bool(passed)]
    if failed:
        raise AssertionError(f"Expanded science verification failed: {failed}")
    return checks
