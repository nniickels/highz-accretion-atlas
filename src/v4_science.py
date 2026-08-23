"""Science workflow for v4, preserving v3 calculations and adding source systematics."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from scripts.generate_v2_uncertainty_rankings import asymmetric_normal_samples, resolve_mbh_uncertainty, summarize_distribution
from src import models
from src import v3_science as v3
from src.v4_catalogue import ASPIRE_SOURCE_KEY, CATALOGUE_RELEASE, MATTHEE_SOURCE_KEY


Z_SEED = v3.Z_SEED
EPSILON = v3.EPSILON
MERGER_BOOST = v3.MERGER_BOOST
DEFAULT_RANDOM_SEED = v3.DEFAULT_RANDOM_SEED
DEFAULT_N_SAMPLES = v3.DEFAULT_N_SAMPLES


@dataclass(frozen=True)
class SourceScenario:
    name: str
    label: str
    delta_dex: float
    source_key: str


SOURCE_SCENARIOS = [
    SourceScenario("matthee_virial_minus_0p5dex", "Matthee virial calibration sensitivity: MBH -0.5 dex", -0.5, MATTHEE_SOURCE_KEY),
    SourceScenario("matthee_virial_plus_0p5dex", "Matthee virial calibration sensitivity: MBH +0.5 dex", 0.5, MATTHEE_SOURCE_KEY),
    SourceScenario("aspire_virial_minus_0p5dex", "ASPIRE virial calibration sensitivity: MBH -0.5 dex", -0.5, ASPIRE_SOURCE_KEY),
    SourceScenario("aspire_virial_plus_0p5dex", "ASPIRE virial calibration sensitivity: MBH +0.5 dex", 0.5, ASPIRE_SOURCE_KEY),
]

INTERPRETIVE_CAVEAT_TAGS = {
    "possible_outflow_contribution", "alternative_non_agn",
    "absorption_interpretation_uncertain",
}
MEASUREMENT_CAVEAT_TAGS = {
    "severe_spatially_dependent_slit_loss",
    "foreground_trace_contamination_red_wing_excluded",
    "halpha_absorption_component_fit", "halpha_absorption_fit",
    "narrow_flux_absorption_degenerate",
    "two_broad_components_total_profile_used_for_mass",
}


def prepare_catalogue_view(catalogue: pd.DataFrame, *, view: str) -> pd.DataFrame:
    result = v3.prepare_catalogue_view(catalogue, view=view)
    result["catalogue_release"] = CATALOGUE_RELEASE
    result["input_catalogue_release"] = CATALOGUE_RELEASE
    return result


def _scenario_evaluation_row(base: pd.Series, scenario: SourceScenario) -> dict[str, object]:
    row = base.to_dict()
    log_mbh = float(base["log_mbh_eval"]) + scenario.delta_dex
    row.update(
        {
            "scenario": scenario.name,
            "scenario_label": scenario.label,
            "scenario_kind": "source_virial_calibration_sensitivity",
            "scenario_scope": f"{scenario.source_key}_only",
            "mbh_delta_dex": scenario.delta_dex,
            "log_mbh_eval": log_mbh,
        }
    )
    for short, log_seed, _ in v3.FIXED_SEEDS:
        row[f"required_fedd_{short}"] = float(models.required_fedd_for_seed(log_seed, log_mbh, EPSILON, Z_SEED, float(base["redshift"]), merger_boost=MERGER_BOOST))
    for short, f_edd in v3.FIXED_GROWTH:
        row[f"required_log_mseed_{short}"] = float(models.required_seed_mass_for_growth(log_mbh, f_edd, EPSILON, Z_SEED, float(base["redshift"]), merger_boost=MERGER_BOOST))
    return row


def evaluate_catalogue(catalogue: pd.DataFrame) -> pd.DataFrame:
    base = v3.evaluate_catalogue(catalogue)
    additions: list[dict[str, object]] = []
    baseline = base[base["scenario"].eq("baseline")]
    for scenario in SOURCE_SCENARIOS:
        for _, row in baseline[baseline["source_key"].eq(scenario.source_key)].iterrows():
            additions.append(_scenario_evaluation_row(row, scenario))
    return pd.concat([base, pd.DataFrame(additions)], ignore_index=True, sort=False)


def build_point_ranking(catalogue: pd.DataFrame, evaluation: pd.DataFrame) -> pd.DataFrame:
    ranking = v3.build_point_ranking(catalogue, evaluation)
    for scenario in SOURCE_SCENARIOS:
        subset = evaluation[evaluation["scenario"].eq(scenario.name)].set_index("ranking_id")
        ranking[f"req_fedd_seed1e2_{scenario.name}"] = ranking["ranking_id"].map(subset["required_fedd_seed1e2"])
        ranking[f"req_log_mseed_fedd0p3_{scenario.name}"] = ranking["ranking_id"].map(subset["required_log_mseed_fedd0p3"])
    ranking["source_virial_sensitivity_note"] = "not_applicable_or_recorded_in_source_specific_columns"
    for source, label in [(MATTHEE_SOURCE_KEY, "Matthee"), (ASPIRE_SOURCE_KEY, "ASPIRE")]:
        ranking.loc[ranking["source_key"].eq(source), "source_virial_sensitivity_note"] = f"{label} statistical errors and +/-0.5 dex calibration scenarios are separate"
    ranking["catalogue_release"] = CATALOGUE_RELEASE
    ranking["input_catalogue_release"] = CATALOGUE_RELEASE
    return _apply_v4_confidence_model(ranking)


def _tags(row: pd.Series) -> set[str]:
    value = row.get("source_caveat_tags", "")
    if pd.isna(value):
        return set()
    return {tag for tag in str(value).split(";") if tag}


def _detection_confidence(row: pd.Series) -> tuple[str, int]:
    if row.get("detection_evidence") == "stack_supported_tentative_hbeta":
        return "low_tentative_stack_supported", 35
    if str(row.get("quality_flag", "")).lower() == "robust":
        return "high", 90
    return "medium_tentative", 60


def _mass_reliability(row: pd.Series) -> tuple[str, int]:
    tags = _tags(row)
    if row.get("edd_ratio_consistency_flag") == "inconsistent":
        return "source_values_internally_inconsistent", 55
    if any(token in tag for token in INTERPRETIVE_CAVEAT_TAGS for tag in tags):
        return "robust_with_interpretive_caveat", 70
    if any(token in tag for token in MEASUREMENT_CAVEAT_TAGS for tag in tags):
        return "robust_with_measurement_caveat", 75
    if str(row.get("quality_flag", "")).lower() == "robust":
        return "high", 90
    return "medium_tentative", 60


def _v4_followup_category(row: pd.Series) -> str:
    if row.get("edd_ratio_consistency_flag") == "inconsistent":
        return "D_source_consistency"
    caveated = row["mass_measurement_reliability_tier"] in {
        "robust_with_interpretive_caveat", "robust_with_measurement_caveat",
    }
    if row["physical_growth_pressure_tier"] == "high" and caveated:
        return "B_caveated_high_pressure"
    if row["physical_growth_pressure_tier"] == "high" and row["detection_confidence_tier"] == "high":
        return "A_robust_high_pressure"
    if row["physical_growth_pressure_tier"] == "high":
        return "B_tentative_high_pressure"
    if caveated:
        return "C_interpretation_or_measurement_check"
    if row["growth_pressure_robustness_0p3"] != "lower_across_0p3_scenarios":
        return "D_systematics_leverage"
    if row["physical_growth_pressure_tier"] == "medium" and row["detection_confidence_tier"] == "high":
        return "E_comparison_anchor"
    return "F_context"


def _apply_v4_confidence_model(ranking: pd.DataFrame) -> pd.DataFrame:
    """Separate detection confidence from line-model/mass reliability for v4."""
    result = ranking.copy()
    detection = result.apply(_detection_confidence, axis=1)
    reliability = result.apply(_mass_reliability, axis=1)
    result["detection_confidence_tier"] = [value[0] for value in detection]
    result["detection_confidence_score_0_100"] = [value[1] for value in detection]
    result["mass_measurement_reliability_tier"] = [value[0] for value in reliability]
    result["mass_measurement_reliability_score_0_100"] = [value[1] for value in reliability]
    # Retain the historical column names as a conservative combined confidence.
    result["measurement_confidence_tier"] = result["mass_measurement_reliability_tier"]
    result["measurement_confidence_score_0_100"] = np.minimum(
        result["detection_confidence_score_0_100"],
        result["mass_measurement_reliability_score_0_100"],
    )
    result["followup_priority_category"] = result.apply(_v4_followup_category, axis=1)
    category_order = {
        "A_robust_high_pressure": 1, "B_caveated_high_pressure": 2,
        "B_tentative_high_pressure": 3, "C_interpretation_or_measurement_check": 4,
        "D_source_consistency": 5, "D_systematics_leverage": 6,
        "E_comparison_anchor": 7, "F_context": 8,
    }
    result["ranking_note"] = result.apply(
        lambda row: (
            f"Observational-triage rank: {row['physical_growth_pressure_tier']} growth pressure; "
            f"{row['detection_confidence_tier']} detection confidence; "
            f"{row['mass_measurement_reliability_tier']} mass/line-model reliability. "
            "This is not evidence for a unique seed channel."
        ), axis=1,
    )
    order = result.assign(_category=result["followup_priority_category"].map(category_order)).sort_values(
        ["_category", "physical_pressure_score_0_100", "measurement_confidence_score_0_100", "ranking_id"],
        ascending=[True, False, False, True],
    )["ranking_id"].tolist()
    result["rank_followup_priority"] = result["ranking_id"].map(
        {ranking_id: rank for rank, ranking_id in enumerate(order, 1)}
    )
    return result


def _source_uncertainty_rows(
    catalogue: pd.DataFrame,
    *,
    n_samples: int,
    random_seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    fedd_rows: list[dict[str, object]] = []
    mseed_rows: list[dict[str, object]] = []
    for _, obj in catalogue.sort_values("ranking_id").iterrows():
        scenarios = [s for s in SOURCE_SCENARIOS if s.source_key == obj["source_key"]]
        if not scenarios:
            continue
        spec = resolve_mbh_uncertainty(obj["log_mbh_err_plus_std"], obj["log_mbh_err_minus_std"])
        rng = v3._rng_for_measurement(random_seed, str(obj["measurement_id"]))
        base_samples = asymmetric_normal_samples(obj["log_mbh_msun_std"], obj["log_mbh_err_plus_std"], obj["log_mbh_err_minus_std"], n_samples=n_samples, rng=rng)
        metadata = {field: obj.get(field, np.nan) for field in v3.IDENTITY_AND_PROVENANCE_FIELDS}
        common = {
            **metadata,
            "n_samples": int(n_samples), "random_seed": int(random_seed), "z_seed": Z_SEED,
            "epsilon": EPSILON, "merger_boost": MERGER_BOOST,
            "reported_statistical_errors_sampled": True, "statistical_error_model": "split-normal-in-log-mbh",
            "log_mbh_err_plus_reported": obj["log_mbh_err_plus_std"],
            "log_mbh_err_minus_reported": obj["log_mbh_err_minus_std"],
            "log_mbh_sigma_plus_used": spec.sigma_plus, "log_mbh_sigma_minus_used": spec.sigma_minus,
            "mbh_uncertainty_mode": spec.mode, "systematic_combined_with_statistical_error": False,
        }
        for scenario in scenarios:
            samples = base_samples + scenario.delta_dex
            scenario_meta = {
                **common, "scenario": scenario.name, "scenario_label": scenario.label,
                "scenario_kind": "source_virial_calibration_sensitivity",
                "scenario_scope": f"{scenario.source_key}_only", "mbh_delta_dex": scenario.delta_dex,
                **summarize_distribution(samples, prefix="log_mbh_sample"),
            }
            for short, log_seed, seed_msun in v3.FIXED_SEEDS:
                required = models.required_fedd_for_seed(log_seed, samples, EPSILON, Z_SEED, float(obj["redshift"]), merger_boost=MERGER_BOOST)
                fedd_rows.append({**scenario_meta, "seed_mass_short": short, "log_mseed_assumption": log_seed, "mseed_assumption_msun": seed_msun, **summarize_distribution(required, prefix="required_fedd"), "prob_required_fedd_gt_1": float(np.mean(required > 1.0))})
            for short, f_edd in v3.FIXED_GROWTH:
                required_log = models.required_seed_mass_for_growth(samples, f_edd, EPSILON, Z_SEED, float(obj["redshift"]), merger_boost=MERGER_BOOST)
                mseed_rows.append({**scenario_meta, "growth_history": short, "f_edd_avg": f_edd, **summarize_distribution(required_log, prefix="required_log_mseed"), "prob_required_mseed_gt_1e5": float(np.mean(required_log > 5.0)), "prob_required_mseed_gt_1e6": float(np.mean(required_log > 6.0))})
    return pd.DataFrame(fedd_rows), pd.DataFrame(mseed_rows)


def build_uncertainty_summaries(catalogue: pd.DataFrame, *, n_samples: int = DEFAULT_N_SAMPLES, random_seed: int = DEFAULT_RANDOM_SEED) -> tuple[pd.DataFrame, pd.DataFrame]:
    fedd, mseed = v3.build_uncertainty_summaries(catalogue, n_samples=n_samples, random_seed=random_seed)
    extra_fedd, extra_mseed = _source_uncertainty_rows(catalogue, n_samples=n_samples, random_seed=random_seed)
    return (
        pd.concat([fedd, extra_fedd], ignore_index=True, sort=False),
        pd.concat([mseed, extra_mseed], ignore_index=True, sort=False),
    )


def build_uncertainty_ranking(point_ranking: pd.DataFrame, fedd_summary: pd.DataFrame, mseed_summary: pd.DataFrame) -> pd.DataFrame:
    ranking = v3.build_uncertainty_ranking(point_ranking, fedd_summary, mseed_summary)
    for scenario in SOURCE_SCENARIOS:
        fedd = fedd_summary[fedd_summary["scenario"].eq(scenario.name) & fedd_summary["seed_mass_short"].eq("seed1e2")].set_index("ranking_id")
        mseed = mseed_summary[mseed_summary["scenario"].eq(scenario.name) & mseed_summary["growth_history"].eq("fedd0p3")].set_index("ranking_id")
        ranking[f"req_fedd_seed1e2_p50_{scenario.name}"] = ranking["ranking_id"].map(fedd["required_fedd_p50"])
        ranking[f"prob_required_fedd_seed1e2_gt_1_{scenario.name}"] = ranking["ranking_id"].map(fedd["prob_required_fedd_gt_1"])
        ranking[f"req_log_mseed_fedd0p3_p50_{scenario.name}"] = ranking["ranking_id"].map(mseed["required_log_mseed_p50"])
    ranking["catalogue_release"] = CATALOGUE_RELEASE
    ranking["input_catalogue_release"] = CATALOGUE_RELEASE
    return ranking


def build_catalogue_summary(measurements: pd.DataFrame, objects: pd.DataFrame) -> pd.DataFrame:
    result = v3.build_catalogue_summary(measurements, objects)
    result["catalogue_release"] = CATALOGUE_RELEASE
    result["input_catalogue_release"] = CATALOGUE_RELEASE
    result.loc[result["stratum_type"].eq("overall"), "selection_function_note"] = "descriptive only: mixes JADES, CEERS/RUBIES, EIGER/FRESCO, and ASPIRE selection functions"
    result["n_lrd_any_measurement"] = result["n_lrd"]
    result["n_lrd_preferred_measurement"] = result["n_lrd"]
    result["n_lrd_cross_source_only"] = 0
    result["lrd_count_basis"] = "measurement-row phenotype"
    object_rows = result["catalogue_view"].eq("physical_object")
    result.loc[object_rows, "lrd_count_basis"] = "any linked measurement; source strata additionally report preferred-measurement attribution"
    for index, summary_row in result[object_rows].iterrows():
        group = objects
        stratum_type = summary_row["stratum_type"]
        value = str(summary_row["stratum_value"])
        if stratum_type == "source":
            group = group[group["source_key"].astype(str).eq(value)]
        elif stratum_type == "survey":
            group = group[group["survey"].astype(str).eq(value)]
        elif stratum_type == "field":
            group = group[group["field"].astype(str).eq(value)]
        elif stratum_type == "survey_field":
            combined = group["survey"].astype("string").fillna("not_reported") + "/" + group["field"].astype("string").fillna("not_reported")
            group = group[combined.eq(value)]
        elif stratum_type == "lrd_phenotype":
            group = group[group["lrd_status"].astype(str).eq(value)]
        any_lrd = group["lrd_reported_by_any_measurement"].fillna(False).astype(bool)
        preferred_lrd = group["preferred_measurement_lrd_flag"].map(v3._boolish)
        result.loc[index, "n_lrd_any_measurement"] = int(any_lrd.sum())
        result.loc[index, "n_lrd_preferred_measurement"] = int(preferred_lrd.sum())
        result.loc[index, "n_lrd_cross_source_only"] = int((any_lrd & ~preferred_lrd).sum())
        if stratum_type in {"source", "survey", "field", "survey_field"}:
            result.loc[index, "n_lrd"] = int(preferred_lrd.sum())
            result.loc[index, "n_non_lrd"] = int((~preferred_lrd).sum())
    return result


def build_alternate_measurement_sensitivity(
    measurements: pd.DataFrame,
    objects: pd.DataFrame,
    *,
    n_samples: int = DEFAULT_N_SAMPLES,
    random_seed: int = DEFAULT_RANDOM_SEED,
) -> pd.DataFrame:
    """Re-rank the object view after substituting each nonpreferred measurement."""
    default_eval = evaluate_catalogue(objects)
    default_point = build_point_ranking(objects, default_eval).set_index("physical_object_id")
    default_fedd, default_mseed = build_uncertainty_summaries(objects, n_samples=n_samples, random_seed=random_seed)
    default_uncertainty = build_uncertainty_ranking(default_point.reset_index(), default_fedd, default_mseed).set_index("physical_object_id")
    protected = {
        "physical_object_id", "ranking_id", "catalogue_view", "catalogue_release", "input_catalogue_release",
        "n_measurements", "available_measurement_ids", "available_object_ids",
        "lrd_flag", "lrd_status", "lrd_reported_by_any_measurement",
        "lrd_evidence_measurement_ids", "lrd_evidence_source_keys",
    }
    rows: list[dict[str, object]] = []
    alternates = measurements[~measurements["preferred_measurement_flag"].astype(bool)]
    for _, alternate in alternates.sort_values(["physical_object_id", "measurement_id"]).iterrows():
        physical_id = str(alternate["physical_object_id"])
        changed = objects.copy()
        target_index = changed.index[changed["physical_object_id"].eq(physical_id)][0]
        for column in set(changed.columns) & set(measurements.columns) - protected:
            changed.at[target_index, column] = alternate[column]
        changed.at[target_index, "preferred_measurement_flag"] = True
        changed.at[target_index, "preferred_measurement_reason"] = "alternate-measurement sensitivity substitution; not the release default"
        changed.at[target_index, "preferred_measurement_lrd_flag"] = alternate.get("lrd_flag", np.nan)
        changed.at[target_index, "ranking_id"] = physical_id
        alternate_eval = evaluate_catalogue(changed)
        alternate_point = build_point_ranking(changed, alternate_eval).set_index("physical_object_id")
        alt_fedd, alt_mseed = build_uncertainty_summaries(changed, n_samples=n_samples, random_seed=random_seed)
        alternate_uncertainty = build_uncertainty_ranking(alternate_point.reset_index(), alt_fedd, alt_mseed).set_index("physical_object_id")
        default = default_point.loc[physical_id]
        alt = alternate_point.loc[physical_id]
        default_u = default_uncertainty.loc[physical_id]
        alt_u = alternate_uncertainty.loc[physical_id]
        rows.append({
            "catalogue_release": CATALOGUE_RELEASE,
            "comparison_scope": "one_object_substitution",
            "physical_object_id": physical_id,
            "default_measurement_id": default["measurement_id"],
            "alternate_measurement_id": alternate["measurement_id"],
            "default_object_id": default["object_id"],
            "alternate_object_id": alternate["object_id"],
            "default_source_key": default["source_key"],
            "alternate_source_key": alternate["source_key"],
            "default_mbh_method": default["mbh_method"],
            "alternate_mbh_method": alt["mbh_method"],
            "default_redshift": default["redshift"], "alternate_redshift": alt["redshift"],
            "default_log_mbh": default["log_mbh_msun"], "alternate_log_mbh": alt["log_mbh_msun"],
            "default_log_mbh_err_plus": default["log_mbh_err_plus_reported"],
            "default_log_mbh_err_minus": default["log_mbh_err_minus_reported"],
            "alternate_log_mbh_err_plus": alt["log_mbh_err_plus_reported"],
            "alternate_log_mbh_err_minus": alt["log_mbh_err_minus_reported"],
            "delta_log_mbh_alternate_minus_default": alt["log_mbh_msun"] - default["log_mbh_msun"],
            "default_rank_growth_pressure": default["rank_growth_pressure"],
            "alternate_rank_growth_pressure": alt["rank_growth_pressure"],
            "delta_rank_growth_pressure": alt["rank_growth_pressure"] - default["rank_growth_pressure"],
            "default_rank_followup_priority": default["rank_followup_priority"],
            "alternate_rank_followup_priority": alt["rank_followup_priority"],
            "default_followup_category": default["followup_priority_category"],
            "alternate_followup_category": alt["followup_priority_category"],
            "default_mass_reliability_tier": default["mass_measurement_reliability_tier"],
            "alternate_mass_reliability_tier": alt["mass_measurement_reliability_tier"],
            "default_source_caveat_tags": default.get("source_caveat_tags", np.nan),
            "alternate_source_caveat_tags": alt.get("source_caveat_tags", np.nan),
            "default_required_fedd_seed1e2": default["req_fedd_seed1e2_z30_eps0p1_b1"],
            "alternate_required_fedd_seed1e2": alt["req_fedd_seed1e2_z30_eps0p1_b1"],
            "default_rank_uncertainty_pressure": default_u["rank_uncertainty_pressure"],
            "alternate_rank_uncertainty_pressure": alt_u["rank_uncertainty_pressure"],
            "delta_rank_uncertainty_pressure": alt_u["rank_uncertainty_pressure"] - default_u["rank_uncertainty_pressure"],
            "default_uncertainty_tier": default_u["uncertainty_growth_pressure_tier"],
            "alternate_uncertainty_tier": alt_u["uncertainty_growth_pressure_tier"],
            "n_samples": int(n_samples), "random_seed": int(random_seed),
            "interpretation_note": "Sensitivity only: the release-default preferred measurement is unchanged.",
        })
    return pd.DataFrame(rows)


def build_growth_summary(measurement_ranking: pd.DataFrame, object_ranking: pd.DataFrame) -> pd.DataFrame:
    result = v3.build_growth_summary(measurement_ranking, object_ranking)
    result["catalogue_release"] = CATALOGUE_RELEASE
    result["input_catalogue_release"] = CATALOGUE_RELEASE
    return result


def verify_v4_outputs(outputs: dict[str, pd.DataFrame], *, n_samples: int) -> dict[str, bool]:
    checks = {
        "measurement_count": len(outputs["measurement_point_ranking"]) == 96,
        "physical_object_count": len(outputs["object_point_ranking"]) == 94,
        "measurement_evaluation_count": len(outputs["measurement_evaluation"]) == 434,
        "object_evaluation_count": len(outputs["object_evaluation"]) == 424,
        "measurement_uncertainty_fedd_count": len(outputs["measurement_uncertainty_fedd"]) == 1302,
        "object_uncertainty_fedd_count": len(outputs["object_uncertainty_fedd"]) == 1272,
        "measurement_uncertainty_mseed_count": len(outputs["measurement_uncertainty_mseed"]) == 868,
        "object_uncertainty_mseed_count": len(outputs["object_uncertainty_mseed"]) == 848,
        "sample_count": outputs["measurement_uncertainty_fedd"]["n_samples"].eq(n_samples).all(),
        "alternate_measurement_sensitivity_count": len(outputs["alternate_measurement_sensitivity"]) == 2,
        "release_metadata": all(frame["catalogue_release"].eq(CATALOGUE_RELEASE).all() for frame in outputs.values()),
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise ValueError(f"v4 output verification failed: {failed}")
    return checks
