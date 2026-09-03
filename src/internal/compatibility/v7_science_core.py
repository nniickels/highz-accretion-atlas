"""Class-aware growth diagnostics for the v7 catalogue.

The global ordering is a navigation aid only. Scientific comparisons are
ranked independently within evidence class and mass-comparability group.
"""

from __future__ import annotations

import hashlib

import numpy as np
import pandas as pd

from src.internal.uncertainty import (
    asymmetric_normal_samples,
    resolve_mbh_uncertainty,
    summarize_distribution,
)
from src import models
from src.internal.compatibility.v7_catalogue import CATALOGUE_RELEASE
from src.internal.compatibility.v7_admission import validate_v7_admission


SCIENCE_RELEASE = "v7-class-aware-science"
Z_SEED = 30.0
EPSILON = 0.1
MERGER_BOOST = 1.0
DEFAULT_RANDOM_SEED = 20260808
DEFAULT_N_SAMPLES = 10_000


def _boolish(value: object) -> bool:
    if pd.isna(value):
        return False
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return bool(value)


def prepare_science_view(catalogue: pd.DataFrame, *, view: str) -> pd.DataFrame:
    """Validate a release view and return only explicitly growth-eligible rows."""
    if view not in {"measurement", "physical_object"}:
        raise ValueError("view must be measurement or physical_object")
    validate_v7_admission(catalogue)
    result = catalogue[catalogue["growth_ranking_eligible_flag"].map(_boolish)].copy()
    result["input_catalogue_release"] = CATALOGUE_RELEASE
    result["science_release"] = SCIENCE_RELEASE
    result["catalogue_view"] = view
    result["ranking_id"] = (
        result["measurement_id"] if view == "measurement" else result["physical_object_id"]
    )
    if result.empty or not result["ranking_id"].is_unique:
        raise ValueError(f"{view} science view must contain unique eligible ranking IDs")
    return result.reset_index(drop=True)


def _required_fedd(log_mbh: object, redshift: object, log_seed: float) -> np.ndarray:
    return models.required_fedd_for_seed(
        log_seed, log_mbh, EPSILON, Z_SEED, redshift, merger_boost=MERGER_BOOST,
    )


def _required_mseed(log_mbh: object, redshift: object, fedd: float) -> np.ndarray:
    return models.required_seed_mass_for_growth(
        log_mbh, fedd, EPSILON, Z_SEED, redshift, merger_boost=MERGER_BOOST,
    )


def _pressure_score(fedd_seed1e2: pd.Series, log_mseed_fedd0p3: pd.Series, redshift: pd.Series) -> pd.Series:
    light = np.clip((fedd_seed1e2 - 0.3) / 1.2, 0.0, 1.0)
    heavy = np.clip((log_mseed_fedd0p3 - 4.0) / 2.8, 0.0, 1.0)
    timing = np.clip((redshift - 6.0) / 4.0, 0.0, 1.0) * 8.0
    return np.clip(100.0 * np.maximum(light, heavy) + timing, 0.0, 100.0)


def _add_ranks(frame: pd.DataFrame, *, score: str, prefix: str) -> pd.DataFrame:
    result = frame.copy()
    tie_fields = [score, "required_fedd_seed1e2", "redshift", "ranking_id"]
    ascending = [False, False, False, True]

    def assign(column: str, fields: list[str]) -> None:
        result[column] = pd.Series(pd.NA, index=result.index, dtype="Int64")
        for _, indexes in result.groupby(fields, dropna=False, sort=True).groups.items():
            order = result.loc[indexes].sort_values(tie_fields, ascending=ascending).index
            result.loc[order, column] = range(1, len(order) + 1)

    order = result.sort_values(tie_fields, ascending=ascending).index
    result[f"{prefix}_global_navigation"] = pd.Series(pd.NA, index=result.index, dtype="Int64")
    result.loc[order, f"{prefix}_global_navigation"] = range(1, len(order) + 1)
    assign(f"{prefix}_within_object_class", ["object_class"])
    assign(f"{prefix}_within_mass_group", ["mass_comparability_group"])
    assign(
        f"{prefix}_within_class_mass_group",
        ["object_class", "mass_comparability_group"],
    )
    primary = result["primary_growth_ranking_flag"].map(_boolish)
    result[f"{prefix}_primary_within_class_mass_group"] = pd.Series(
        pd.NA, index=result.index, dtype="Int64",
    )
    for _, indexes in result.loc[primary].groupby(
        ["object_class", "mass_comparability_group"], dropna=False, sort=True,
    ).groups.items():
        primary_order = result.loc[indexes].sort_values(tie_fields, ascending=ascending).index
        result.loc[primary_order, f"{prefix}_primary_within_class_mass_group"] = range(
            1, len(primary_order) + 1,
        )
    return result


def build_point_ranking(catalogue: pd.DataFrame) -> pd.DataFrame:
    """Build deterministic baseline and separate systematic-envelope diagnostics."""
    result = catalogue.copy()
    mass = result["log_mbh_msun_std"].astype(float)
    redshift = result["redshift"].astype(float)
    result["required_fedd_seed1e2"] = _required_fedd(mass, redshift, 2.0)
    result["required_fedd_seed1e4"] = _required_fedd(mass, redshift, 4.0)
    result["required_fedd_seed1e5"] = _required_fedd(mass, redshift, 5.0)
    result["required_log_mseed_fedd0p3"] = _required_mseed(mass, redshift, 0.3)
    result["required_log_mseed_fedd1"] = _required_mseed(mass, redshift, 1.0)
    result["growth_pressure_score_0_100"] = _pressure_score(
        result["required_fedd_seed1e2"], result["required_log_mseed_fedd0p3"], redshift,
    )
    result["growth_pressure_tier"] = np.select(
        [
            result["required_fedd_seed1e2"].gt(1.0)
            | result["required_log_mseed_fedd0p3"].gt(6.0),
            result["required_fedd_seed1e2"].gt(0.7)
            | result["required_log_mseed_fedd0p3"].gt(5.0),
        ],
        ["high", "medium"], default="low",
    )
    systematic = pd.to_numeric(result["log_mbh_systematic_dex"], errors="coerce")
    result["systematic_envelope_available_flag"] = systematic.notna()
    result["required_fedd_seed1e2_systematic_low"] = np.nan
    result["required_fedd_seed1e2_systematic_high"] = np.nan
    result["required_log_mseed_fedd0p3_systematic_low"] = np.nan
    result["required_log_mseed_fedd0p3_systematic_high"] = np.nan
    available = systematic.notna()
    result.loc[available, "required_fedd_seed1e2_systematic_low"] = _required_fedd(
        mass[available] - systematic[available], redshift[available], 2.0,
    )
    result.loc[available, "required_fedd_seed1e2_systematic_high"] = _required_fedd(
        mass[available] + systematic[available], redshift[available], 2.0,
    )
    result.loc[available, "required_log_mseed_fedd0p3_systematic_low"] = _required_mseed(
        mass[available] - systematic[available], redshift[available], 0.3,
    )
    result.loc[available, "required_log_mseed_fedd0p3_systematic_high"] = _required_mseed(
        mass[available] + systematic[available], redshift[available], 0.3,
    )
    result["systematic_combined_with_statistical_error"] = False
    result["global_rank_policy"] = "navigation_only_no_cross_class_science_claim"
    result["demographic_inference_allowed"] = False
    result["current_edd_ratio_comparison_status"] = np.select(
        [
            result["edd_ratio_consistency_flag"].eq("inconsistent"),
            result["edd_ratio_std"].isna(),
        ],
        ["excluded_source_internal_inconsistency", "unavailable_not_published"],
        default="available_not_growth_history",
    )
    result = _add_ranks(result, score="growth_pressure_score_0_100", prefix="rank")
    front = [
        "science_release", "input_catalogue_release", "catalogue_view",
        "rank_global_navigation", "rank_within_object_class", "rank_within_mass_group",
        "rank_within_class_mass_group", "rank_primary_within_class_mass_group",
        "ranking_id", "measurement_id", "physical_object_id", "object_id", "source_key",
        "object_class", "mass_comparability_group", "evidence_status", "redshift",
        "log_mbh_msun_std", "mbh_method", "growth_pressure_tier",
        "growth_pressure_score_0_100",
    ]
    return result[front + [column for column in result if column not in front]].sort_values(
        ["rank_global_navigation", "ranking_id"],
    ).reset_index(drop=True)


def _rng(random_seed: int, ranking_id: str) -> np.random.Generator:
    digest = hashlib.sha256(f"{random_seed}:{ranking_id}".encode()).digest()
    return np.random.default_rng(int.from_bytes(digest[:8], "little"))


def build_uncertainty_ranking(
    catalogue: pd.DataFrame,
    *,
    n_samples: int = DEFAULT_N_SAMPLES,
    random_seed: int = DEFAULT_RANDOM_SEED,
) -> pd.DataFrame:
    """Sample reported statistical mass errors without folding in systematics."""
    rows = []
    metadata = [
        "science_release", "input_catalogue_release", "catalogue_view", "ranking_id",
        "measurement_id", "physical_object_id", "object_id", "source_key", "survey",
        "field", "object_class", "mass_comparability_group", "evidence_status",
        "evidence_status_basis", "primary_growth_ranking_flag", "redshift", "mbh_method",
        "log_mbh_msun_std", "log_mbh_err_plus_std", "log_mbh_err_minus_std",
        "log_mbh_systematic_dex", "mbh_systematic_kind",
    ]
    for _, source in catalogue.sort_values("ranking_id").iterrows():
        spec = resolve_mbh_uncertainty(
            source["log_mbh_err_plus_std"], source["log_mbh_err_minus_std"],
        )
        masses = asymmetric_normal_samples(
            source["log_mbh_msun_std"], source["log_mbh_err_plus_std"],
            source["log_mbh_err_minus_std"], n_samples=n_samples,
            rng=_rng(random_seed, str(source["ranking_id"])),
        )
        required_fedd = _required_fedd(masses, float(source["redshift"]), 2.0)
        required_mseed = _required_mseed(masses, float(source["redshift"]), 0.3)
        rows.append({
            **{field: source.get(field, np.nan) for field in metadata},
            "n_samples": int(n_samples),
            "random_seed": int(random_seed),
            "reported_statistical_errors_sampled": True,
            "statistical_error_model": "split_normal_in_log_mbh",
            "log_mbh_sigma_plus_used": spec.sigma_plus,
            "log_mbh_sigma_minus_used": spec.sigma_minus,
            "mbh_uncertainty_mode": spec.mode,
            "systematic_combined_with_statistical_error": False,
            **summarize_distribution(required_fedd, prefix="required_fedd_seed1e2"),
            "prob_required_fedd_seed1e2_gt_1": float(np.mean(required_fedd > 1.0)),
            **summarize_distribution(required_mseed, prefix="required_log_mseed_fedd0p3"),
            "prob_required_log_mseed_fedd0p3_gt_1e5": float(np.mean(required_mseed > 5.0)),
            "prob_required_log_mseed_fedd0p3_gt_1e6": float(np.mean(required_mseed > 6.0)),
        })
    result = pd.DataFrame(rows)
    probability = pd.concat([
        result["prob_required_fedd_seed1e2_gt_1"],
        result["prob_required_log_mseed_fedd0p3_gt_1e6"],
        0.5 * result["prob_required_log_mseed_fedd0p3_gt_1e5"],
    ], axis=1).max(axis=1)
    result["uncertainty_pressure_score_0_100"] = 100.0 * probability
    result["uncertainty_pressure_tier"] = np.select(
        [probability.ge(0.5), probability.ge(0.16)],
        ["likely_high_pressure", "possible_high_pressure"], default="lower_pressure",
    )
    # Ranking helper expects this deterministic tie-break field.
    result["required_fedd_seed1e2"] = result["required_fedd_seed1e2_p50"]
    result = _add_ranks(
        result, score="uncertainty_pressure_score_0_100", prefix="rank_uncertainty",
    )
    return result.sort_values(
        ["rank_uncertainty_global_navigation", "ranking_id"],
    ).reset_index(drop=True)


def build_class_method_summary(
    measurement_point: pd.DataFrame,
    object_point: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize explicitly non-demographic class/method strata."""
    rows = []
    dimensions = {
        "object_class": ["object_class"],
        "mass_comparability_group": ["mass_comparability_group"],
        "object_class_x_mass_group": ["object_class", "mass_comparability_group"],
        "evidence_status": ["evidence_status"],
        "source_key": ["source_key"],
    }
    for frame in [measurement_point, object_point]:
        for dimension, fields in dimensions.items():
            for values, group in frame.groupby(fields, dropna=False, sort=True):
                values = values if isinstance(values, tuple) else (values,)
                value = ";".join(f"{field}={item}" for field, item in zip(fields, values, strict=True))
                top = group.nsmallest(1, "rank_global_navigation").iloc[0]
                rows.append({
                    "science_release": SCIENCE_RELEASE,
                    "input_catalogue_release": CATALOGUE_RELEASE,
                    "catalogue_view": frame["catalogue_view"].iloc[0],
                    "stratum_dimension": dimension,
                    "stratum_value": value,
                    "n_rows": len(group),
                    "n_physical_objects": group["physical_object_id"].nunique(),
                    "n_primary": int(group["primary_growth_ranking_flag"].map(_boolish).sum()),
                    "n_high_pressure": int(group["growth_pressure_tier"].eq("high").sum()),
                    "median_required_fedd_seed1e2": group["required_fedd_seed1e2"].median(),
                    "median_required_log_mseed_fedd0p3": group[
                        "required_log_mseed_fedd0p3"
                    ].median(),
                    "top_ranking_id": top["ranking_id"],
                    "demographic_inference_allowed": False,
                    "comparison_policy": (
                        "descriptive_stratum_only_no_selection_completeness_correction"
                    ),
                })
    if not rows:
        return pd.DataFrame(columns=[
            "science_release", "input_catalogue_release", "catalogue_view",
            "measurement_id", "physical_object_id", "object_id", "source_key",
            "object_class", "mass_comparability_group",
            "growth_ranking_eligibility_reason", "retained_in_catalogue_flag",
            "excluded_from_science_rank_flag",
        ])
    return pd.DataFrame(rows).sort_values(
        ["catalogue_view", "stratum_dimension", "stratum_value"],
    ).reset_index(drop=True)


def build_exclusion_audit(measurements: pd.DataFrame, objects: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for view, frame in [("measurement", measurements), ("physical_object", objects)]:
        excluded = frame[~frame["growth_ranking_eligible_flag"].map(_boolish)]
        for _, source in excluded.iterrows():
            rows.append({
                "science_release": SCIENCE_RELEASE,
                "input_catalogue_release": CATALOGUE_RELEASE,
                "catalogue_view": view,
                "measurement_id": source["measurement_id"],
                "physical_object_id": source["physical_object_id"],
                "object_id": source["object_id"],
                "source_key": source["source_key"],
                "object_class": source["object_class"],
                "mass_comparability_group": source["mass_comparability_group"],
                "growth_ranking_eligibility_reason": source[
                    "growth_ranking_eligibility_reason"
                ],
                "retained_in_catalogue_flag": True,
                "excluded_from_science_rank_flag": True,
            })
    if not rows:
        return pd.DataFrame(columns=[
            "science_release", "input_catalogue_release", "catalogue_view",
            "measurement_id", "physical_object_id", "object_id", "source_key",
            "object_class", "mass_comparability_group",
            "growth_ranking_eligibility_reason", "retained_in_catalogue_flag",
            "excluded_from_science_rank_flag",
        ])
    return pd.DataFrame(rows).sort_values(
        ["catalogue_view", "measurement_id"],
    ).reset_index(drop=True)


def build_alternate_measurement_sensitivity(
    measurements: pd.DataFrame,
    objects: pd.DataFrame,
) -> pd.DataFrame:
    """Compare every eligible alternate measurement with its preferred object row."""
    preferred = objects.set_index("physical_object_id")
    rows = []
    alternates = measurements[
        ~measurements["preferred_measurement_flag"].map(_boolish)
        & measurements["growth_ranking_eligible_flag"].map(_boolish)
    ]
    for _, alternate in alternates.sort_values(["physical_object_id", "measurement_id"]).iterrows():
        default = preferred.loc[alternate["physical_object_id"]]
        if not _boolish(default["growth_ranking_eligible_flag"]):
            continue
        default_fedd = float(_required_fedd(default["log_mbh_msun_std"], default["redshift"], 2.0))
        alternate_fedd = float(_required_fedd(
            alternate["log_mbh_msun_std"], alternate["redshift"], 2.0,
        ))
        rows.append({
            "science_release": SCIENCE_RELEASE,
            "input_catalogue_release": CATALOGUE_RELEASE,
            "physical_object_id": alternate["physical_object_id"],
            "object_class": default["object_class"],
            "mass_comparability_group_default": default["mass_comparability_group"],
            "mass_comparability_group_alternate": alternate["mass_comparability_group"],
            "default_measurement_id": default["measurement_id"],
            "alternate_measurement_id": alternate["measurement_id"],
            "default_source_key": default["source_key"],
            "alternate_source_key": alternate["source_key"],
            "default_log_mbh": default["log_mbh_msun_std"],
            "alternate_log_mbh": alternate["log_mbh_msun_std"],
            "delta_log_mbh_alternate_minus_default": (
                alternate["log_mbh_msun_std"] - default["log_mbh_msun_std"]
            ),
            "default_required_fedd_seed1e2": default_fedd,
            "alternate_required_fedd_seed1e2": alternate_fedd,
            "delta_required_fedd_alternate_minus_default": alternate_fedd - default_fedd,
            "comparison_is_within_same_mass_group": (
                default["mass_comparability_group"] == alternate["mass_comparability_group"]
            ),
            "default_release_preference_changed_flag": False,
        })
    if not rows:
        return pd.DataFrame(columns=[
            "science_release", "input_catalogue_release", "physical_object_id",
            "object_class", "mass_comparability_group_default",
            "mass_comparability_group_alternate", "default_measurement_id",
            "alternate_measurement_id", "default_source_key", "alternate_source_key",
            "default_log_mbh", "alternate_log_mbh",
            "delta_log_mbh_alternate_minus_default", "default_required_fedd_seed1e2",
            "alternate_required_fedd_seed1e2",
            "delta_required_fedd_alternate_minus_default",
            "comparison_is_within_same_mass_group",
            "default_release_preference_changed_flag",
        ])
    return pd.DataFrame(rows)


def build_science_policy() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "science_release": SCIENCE_RELEASE,
            "scope": "global_navigation_rank",
            "allowed": True,
            "policy": "navigation_only_no_cross_class_science_claim",
        },
        {
            "science_release": SCIENCE_RELEASE,
            "scope": "within_object_class_rank",
            "allowed": True,
            "policy": "descriptive_growth_pressure_comparison_only",
        },
        {
            "science_release": SCIENCE_RELEASE,
            "scope": "within_class_and_mass_group_rank",
            "allowed": True,
            "policy": "primary_interpretive_comparison_scope",
        },
        {
            "science_release": SCIENCE_RELEASE,
            "scope": "pooled_demographic_inference",
            "allowed": False,
            "policy": "forbidden_without_selection_function_and_completeness_model",
        },
    ])


def verify_science_outputs(outputs: dict[str, pd.DataFrame], *, n_samples: int) -> None:
    measurement_point = outputs["measurement_point_ranking"]
    object_point = outputs["object_point_ranking"]
    measurement_uncertainty = outputs["measurement_uncertainty_ranking"]
    object_uncertainty = outputs["object_uncertainty_ranking"]
    checks = {
        "measurement_point_count": len(measurement_point) == 119,
        "object_point_count": len(object_point) == 112,
        "measurement_uncertainty_count": len(measurement_uncertainty) == 119,
        "object_uncertainty_count": len(object_uncertainty) == 112,
        "measurement_ids_unique": measurement_point["measurement_id"].is_unique,
        "object_ids_unique": object_point["physical_object_id"].is_unique,
        "sample_count": measurement_uncertainty["n_samples"].eq(n_samples).all(),
        "exclusion_audit_count": len(outputs["exclusion_audit"]) == 4,
        "policy_count": len(outputs["science_policy"]) == 4,
        "no_demographic_permission": (
            ~outputs["class_method_summary"]["demographic_inference_allowed"].map(_boolish)
        ).all(),
        "all_release_metadata": all(
            frame["science_release"].eq(SCIENCE_RELEASE).all() for frame in outputs.values()
        ),
    }
    for frame, prefix in [
        (measurement_point, "rank"), (object_point, "rank"),
        (measurement_uncertainty, "rank_uncertainty"),
        (object_uncertainty, "rank_uncertainty"),
    ]:
        column = f"{prefix}_global_navigation"
        checks[f"{column}_{frame['catalogue_view'].iloc[0]}_contiguous"] = (
            sorted(frame[column].astype(int)) == list(range(1, len(frame) + 1))
        )
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise ValueError(f"v7 class-aware science verification failed: {failed}")
