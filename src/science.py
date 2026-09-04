"""Shared science products for every dataset version."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

import numpy as np
import pandas as pd

from src.internal.uncertainty import (
    asymmetric_normal_samples, resolve_mbh_uncertainty, summarize_distribution,
)
from src import models
from src.internal.compatibility import v7_science_core as core
from src.datasets import DATASET_SPECS
from src.selection_completeness import build_selection_summary, load_selection_registry


DEFAULT_RANDOM_SEED = core.DEFAULT_RANDOM_SEED
DEFAULT_N_SAMPLES = core.DEFAULT_N_SAMPLES
BURST_SCENARIOS = (
    ("eddington", 1.0),
    ("moderate_super_eddington", 2.0),
    ("strong_super_eddington", 3.0),
)


def _boolish(value: object) -> bool:
    if pd.isna(value):
        return False
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "y"}
    return bool(value)


def _joined_values(series: pd.Series, *, separator: str = ";") -> str:
    values: set[str] = set()
    for value in series.dropna().astype(str):
        for item in value.split(separator):
            cleaned = item.strip()
            if cleaned:
                values.add(cleaned)
    return separator.join(sorted(values))


def build_followup_priority(
    objects: pd.DataFrame, point: pd.DataFrame, uncertainty: pd.DataFrame,
) -> pd.DataFrame:
    """Build a transparent class-aware observational follow-up matrix."""
    point_fields = [
        "physical_object_id", "rank_global_navigation", "rank_within_object_class",
        "growth_pressure_tier", "growth_pressure_score_0_100", "required_fedd_seed1e2",
        "required_log_mseed_fedd0p3", "systematic_envelope_available_flag",
        "required_fedd_seed1e2_systematic_low", "required_fedd_seed1e2_systematic_high",
        "edd_ratio_consistency_flag", "edd_ratio_log_residual_dex",
    ]
    uncertainty_fields = [
        "physical_object_id", "uncertainty_pressure_tier",
        "prob_required_fedd_seed1e2_gt_1", "required_fedd_seed1e2_p16",
        "required_fedd_seed1e2_p50", "required_fedd_seed1e2_p84",
    ]
    result = objects[[
        "physical_object_id", "object_id", "object_class", "source_key", "redshift",
        "quality_flag", "evidence_status", "mass_comparability_group",
        "growth_ranking_eligible_flag", "primary_growth_ranking_flag",
        "growth_ranking_eligibility_reason", "source_caveat_tags",
    ]].copy()
    result = result.merge(point[point_fields], on="physical_object_id", how="left", validate="one_to_one")
    result = result.merge(
        uncertainty[uncertainty_fields], on="physical_object_id", how="left", validate="one_to_one",
    )

    def classify(row: pd.Series) -> str:
        if not _boolish(row["growth_ranking_eligible_flag"]):
            return "not_ranked_no_canonical_mass"
        if str(row["edd_ratio_consistency_flag"]) == "inconsistent":
            return "C_source_consistency"
        high = str(row["growth_pressure_tier"]) == "high"
        robust = str(row["quality_flag"]).lower() == "robust"
        primary = _boolish(row["primary_growth_ranking_flag"])
        if high and robust and primary:
            return "A_robust_high_pressure"
        if high:
            return "B_caveated_high_pressure"
        if str(row["uncertainty_pressure_tier"]) == "possible_high_pressure":
            return "D_uncertainty_leverage"
        if str(row["growth_pressure_tier"]) == "medium" and robust:
            return "E_comparison_anchor"
        return "F_context"

    def recommendation(row: pd.Series) -> str:
        category = row["followup_priority_category"]
        if category == "not_ranked_no_canonical_mass":
            return "obtain a method-comparable canonical black-hole mass before growth inference"
        if category == "A_robust_high_pressure":
            return "independent black-hole mass and accretion-history constraints"
        if category == "B_caveated_high_pressure":
            return "resolve measurement or comparability caveats, then re-evaluate growth pressure"
        if category == "C_source_consistency":
            return "resolve the published mass/luminosity/Eddington-ratio inconsistency"
        if category == "D_uncertainty_leverage":
            return "reduce black-hole mass uncertainty near the high-pressure boundary"
        if category == "E_comparison_anchor":
            return "retain as a within-class comparison anchor"
        return "retain for catalogue context; no priority claim"

    result["followup_priority_category"] = result.apply(classify, axis=1)
    result["most_needed_followup"] = result.apply(recommendation, axis=1)
    category_base = {
        "A_robust_high_pressure": 90.0,
        "B_caveated_high_pressure": 80.0,
        "C_source_consistency": 70.0,
        "D_uncertainty_leverage": 60.0,
        "E_comparison_anchor": 50.0,
        "F_context": 30.0,
    }
    eligible = result["growth_ranking_eligible_flag"].map(_boolish)
    pressure = pd.to_numeric(result["growth_pressure_score_0_100"], errors="coerce").fillna(0.0)
    probability = pd.to_numeric(
        result["prob_required_fedd_seed1e2_gt_1"], errors="coerce",
    ).fillna(0.0)
    result["followup_value_score_0_100"] = np.nan
    result.loc[eligible, "followup_value_score_0_100"] = [
        min(100.0, category_base[category] + 0.06 * pscore + 2.0 * probability_value)
        for category, pscore, probability_value in zip(
            result.loc[eligible, "followup_priority_category"],
            pressure.loc[eligible], probability.loc[eligible], strict=True,
        )
    ]
    result["rank_followup_global_navigation"] = pd.Series(pd.NA, index=result.index, dtype="Int64")
    result["rank_followup_within_object_class"] = pd.Series(pd.NA, index=result.index, dtype="Int64")
    order = result.loc[eligible].sort_values(
        ["followup_value_score_0_100", "growth_pressure_score_0_100", "redshift", "physical_object_id"],
        ascending=[False, False, False, True],
    )
    result.loc[order.index, "rank_followup_global_navigation"] = np.arange(1, len(order) + 1)
    for _, group in result.loc[eligible].groupby("object_class", sort=True):
        class_order = group.sort_values(
            ["followup_value_score_0_100", "growth_pressure_score_0_100", "redshift", "physical_object_id"],
            ascending=[False, False, False, True],
        )
        result.loc[class_order.index, "rank_followup_within_object_class"] = np.arange(1, len(class_order) + 1)
    result.insert(0, "science_release", core.SCIENCE_RELEASE)
    result.insert(1, "input_catalogue_release", core.CATALOGUE_RELEASE)
    result["global_rank_policy"] = "navigation_only_no_cross_class_demographic_inference"
    return result.sort_values(
        ["growth_ranking_eligible_flag", "rank_followup_global_navigation", "object_class", "physical_object_id"],
        ascending=[False, True, True, True], na_position="last",
    ).reset_index(drop=True)


def build_source_caveat_summary(measurements: pd.DataFrame) -> pd.DataFrame:
    """Summarize provenance and caveats once per admitted source family."""
    rows: list[dict[str, object]] = []
    for source_key, group in measurements.groupby("source_key", sort=True, dropna=False):
        rows.append({
            "science_release": core.SCIENCE_RELEASE,
            "input_catalogue_release": core.CATALOGUE_RELEASE,
            "source_key": source_key,
            "source_paper_version": _joined_values(group["source_paper_version"]),
            "source_doi": _joined_values(group["source_doi"]),
            "source_url": _joined_values(group["source_url"]),
            "n_measurements": len(group),
            "n_physical_objects": group["physical_object_id"].nunique(),
            "n_growth_eligible_measurements": int(group["growth_ranking_eligible_flag"].map(_boolish).sum()),
            "object_classes": _joined_values(group["object_class"]),
            "mass_comparability_groups": _joined_values(group["mass_comparability_group"]),
            "evidence_statuses": _joined_values(group["evidence_status"]),
            "selection_channels": _joined_values(group["selection_channels"]),
            "source_caveat_tags": _joined_values(group["source_caveat_tags"]),
            "growth_exclusion_reasons": _joined_values(
                group.loc[~group["growth_ranking_eligible_flag"].map(_boolish), "growth_ranking_eligibility_reason"],
            ),
            "selection_criteria": _joined_values(group["selection_criteria"]),
            "demographic_inference_allowed": False,
        })
    return pd.DataFrame(rows)


@contextmanager
def science_context(version: str):
    spec = DATASET_SPECS[version]
    old_catalogue, old_science = core.CATALOGUE_RELEASE, core.SCIENCE_RELEASE
    core.CATALOGUE_RELEASE = spec.catalogue_release
    core.SCIENCE_RELEASE = f"{version}-shared-science"
    try:
        yield
    finally:
        core.CATALOGUE_RELEASE, core.SCIENCE_RELEASE = old_catalogue, old_science


def build_accretion_history(
    view: pd.DataFrame, *, n_samples: int, random_seed: int,
) -> pd.DataFrame:
    """Evaluate the retained two-state duty-cycle scenarios for one view."""
    rows: list[dict[str, object]] = []
    for _, obj in view.sort_values("ranking_id").iterrows():
        rng = core._rng(random_seed, f"duty:{obj['ranking_id']}")
        uncertainty = resolve_mbh_uncertainty(
            obj["log_mbh_err_plus_std"], obj["log_mbh_err_minus_std"],
        )
        has_reported_error = (
            uncertainty.mode != "point_estimate_no_reported_mbh_error"
        )
        masses = asymmetric_normal_samples(
            obj["log_mbh_msun_std"], obj["log_mbh_err_plus_std"],
            obj["log_mbh_err_minus_std"], n_samples=n_samples, rng=rng,
        )
        required = models.required_fedd_for_seed(
            2.0, masses, core.EPSILON, core.Z_SEED, float(obj["redshift"]),
            merger_boost=core.MERGER_BOOST,
        )
        required_point = float(models.required_fedd_for_seed(
            2.0, float(obj["log_mbh_msun_std"]), core.EPSILON, core.Z_SEED,
            float(obj["redshift"]), merger_boost=core.MERGER_BOOST,
        ))
        current = pd.to_numeric(pd.Series([obj.get("edd_ratio_std")]), errors="coerce").iloc[0]
        consistency = str(obj.get("edd_ratio_consistency_flag", "not_evaluable"))
        current_ok = pd.notna(current) and float(current) > 0 and consistency != "inconsistent"
        for scenario, burst in BURST_SCENARIOS:
            duty = models.required_duty_cycle(required, burst, 0.0)
            duty_point = float(models.required_duty_cycle(required_point, burst, 0.0))
            rows.append({
                "science_release": core.SCIENCE_RELEASE,
                "input_catalogue_release": core.CATALOGUE_RELEASE,
                "catalogue_view": obj["catalogue_view"],
                "ranking_id": obj["ranking_id"],
                "measurement_id": obj["measurement_id"],
                "physical_object_id": obj["physical_object_id"],
                "object_id": obj["object_id"],
                "source_key": obj["source_key"],
                "object_class": obj["object_class"],
                "redshift": obj["redshift"],
                "log_mseed_assumption": 2.0,
                "z_seed": core.Z_SEED,
                "epsilon": core.EPSILON,
                "merger_boost": core.MERGER_BOOST,
                "burst_scenario": scenario,
                "burst_fedd": burst,
                "quiescent_fedd": 0.0,
                "required_lifetime_average_fedd_point": required_point,
                "required_duty_cycle_point": duty_point,
                **summarize_distribution(duty, prefix="required_duty_cycle"),
                "prob_required_duty_cycle_gt_1": (
                    float(np.mean(duty > 1.0)) if has_reported_error else np.nan
                ),
                "fixed_burst_scenario_feasible_point": duty_point <= 1.0,
                "reported_current_fedd": current,
                "current_fedd_comparison_eligible_flag": current_ok,
                "current_to_required_fedd_ratio": (
                    float(current) / required_point if current_ok and required_point > 0 else np.nan
                ),
                "current_fedd_is_instantaneous_not_history": True,
                "n_samples": n_samples,
                "random_seed": random_seed,
                "reported_statistical_errors_sampled": has_reported_error,
                "statistical_error_model": (
                    "split_normal_in_log_mbh" if has_reported_error
                    else "point_estimate_no_statistical_distribution"
                ),
                "log_mbh_sigma_plus_used": uncertainty.sigma_plus,
                "log_mbh_sigma_minus_used": uncertainty.sigma_minus,
                "systematic_combined_with_statistical_error": False,
            })
    return pd.DataFrame(rows)


def build_outputs(
    version: str, measurements: pd.DataFrame, objects: pd.DataFrame, *,
    n_samples: int = DEFAULT_N_SAMPLES, random_seed: int = DEFAULT_RANDOM_SEED,
) -> dict[str, pd.DataFrame]:
    with science_context(version):
        measurement_view = core.prepare_science_view(measurements, view="measurement")
        object_view = core.prepare_science_view(objects, view="physical_object")
        measurement_point = core.build_point_ranking(measurement_view)
        object_point = core.build_point_ranking(object_view)
        outputs = {
            "evaluation_table": object_point.copy(),
            "measurement_point_ranking": measurement_point,
            "object_point_ranking": object_point,
            "measurement_uncertainty_ranking": core.build_uncertainty_ranking(
                measurement_view, n_samples=n_samples, random_seed=random_seed,
            ),
            "object_uncertainty_ranking": core.build_uncertainty_ranking(
                object_view, n_samples=n_samples, random_seed=random_seed,
            ),
            "class_method_summary": core.build_class_method_summary(measurement_point, object_point),
            "exclusion_audit": core.build_exclusion_audit(measurements, objects),
            "alternate_measurement_sensitivity": core.build_alternate_measurement_sensitivity(measurements, objects),
            "science_policy": core.build_science_policy(),
            "measurement_accretion_history": build_accretion_history(
                measurement_view, n_samples=n_samples, random_seed=random_seed,
            ),
            "object_accretion_history": build_accretion_history(
                object_view, n_samples=n_samples, random_seed=random_seed,
            ),
        }
        outputs["followup_priority"] = build_followup_priority(
            objects, object_point, outputs["object_uncertainty_ranking"],
        )
        outputs["source_caveat_summary"] = build_source_caveat_summary(measurements)
        selection_registry = load_selection_registry(
            Path(__file__).resolve().parents[1] / "data/selection_function_registry.csv"
        )
        outputs["selection_completeness_summary"] = build_selection_summary(
            measurements, selection_registry,
        ).assign(
            science_release=core.SCIENCE_RELEASE,
            input_catalogue_release=core.CATALOGUE_RELEASE,
        )
        fedd_fields = {
            "1e2": "required_fedd_seed1e2",
            "1e4": "required_fedd_seed1e4",
            "1e5": "required_fedd_seed1e5",
        }
        outputs["required_fedd_by_seed_mass"] = pd.concat([
            object_point[["physical_object_id", "object_id", "object_class", "redshift"]]
            .assign(seed_mass_family=label, required_fedd=object_point[field].to_numpy())
            for label, field in fedd_fields.items()
        ], ignore_index=True)
        mseed_fields = {
            "0p3": "required_log_mseed_fedd0p3",
            "1": "required_log_mseed_fedd1",
        }
        outputs["required_mseed_by_growth_assumption"] = pd.concat([
            object_point[["physical_object_id", "object_id", "object_class", "redshift"]]
            .assign(fedd_assumption=label, required_log_mseed=object_point[field].to_numpy())
            for label, field in mseed_fields.items()
        ], ignore_index=True)
        outputs["sample_summary"] = (
            objects.groupby("object_class", dropna=False)
            .agg(
                n_objects=("physical_object_id", "nunique"),
                n_growth_eligible=("growth_ranking_eligible_flag", lambda x: int(x.astype(bool).sum())),
                median_redshift=("redshift", "median"),
                median_log_mbh=("log_mbh_msun_std", "median"),
            )
            .reset_index()
            .assign(science_release=core.SCIENCE_RELEASE, input_catalogue_release=core.CATALOGUE_RELEASE)
        )
    eligible_measurements = int(measurements["growth_ranking_eligible_flag"].map(_boolish).sum())
    eligible_objects = int(objects["growth_ranking_eligible_flag"].map(_boolish).sum())
    expected = {
        "measurement_point_ranking": eligible_measurements,
        "object_point_ranking": eligible_objects,
        "measurement_uncertainty_ranking": eligible_measurements,
        "object_uncertainty_ranking": eligible_objects,
        "measurement_accretion_history": 3 * eligible_measurements,
        "object_accretion_history": 3 * eligible_objects,
    }
    observed = {name: len(outputs[name]) for name in expected}
    if observed != expected:
        raise ValueError(f"{version} science coverage changed: {observed} != {expected}")
    return outputs
