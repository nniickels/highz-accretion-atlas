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
    return ranking


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
    return result


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
        "release_metadata": all(frame["catalogue_release"].eq(CATALOGUE_RELEASE).all() for frame in outputs.values()),
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise ValueError(f"v4 output verification failed: {failed}")
    return checks
