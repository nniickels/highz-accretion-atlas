"""Science workflow for the v6 THRILS same-class BLAGN consolidation."""

from __future__ import annotations

from contextlib import contextmanager

import pandas as pd

from src import v4_science as v4
from src import v5_science as v5
from src.object_taxonomy import TAXONOMY_FIELDS
from src.v6_catalogue import CATALOGUE_RELEASE, THRILS_SOURCE_KEY


Z_SEED = v5.Z_SEED
EPSILON = v5.EPSILON
MERGER_BOOST = v5.MERGER_BOOST
DEFAULT_RANDOM_SEED = v5.DEFAULT_RANDOM_SEED
DEFAULT_N_SAMPLES = v5.DEFAULT_N_SAMPLES

THRILS_SCENARIOS = [
    v4.SourceScenario(
        "thrils_virial_minus_0p5dex",
        "THRILS virial calibration sensitivity: MBH -0.5 dex",
        -0.5,
        THRILS_SOURCE_KEY,
    ),
    v4.SourceScenario(
        "thrils_virial_plus_0p5dex",
        "THRILS virial calibration sensitivity: MBH +0.5 dex",
        0.5,
        THRILS_SOURCE_KEY,
    ),
]


@contextmanager
def _v6_context():
    """Temporarily extend the inherited release/scenario configuration."""
    previous_release = v5.CATALOGUE_RELEASE
    previous_scenarios = v4.SOURCE_SCENARIOS
    v5.CATALOGUE_RELEASE = CATALOGUE_RELEASE
    v4.SOURCE_SCENARIOS = [*previous_scenarios, *THRILS_SCENARIOS]
    try:
        yield
    finally:
        v5.CATALOGUE_RELEASE = previous_release
        v4.SOURCE_SCENARIOS = previous_scenarios


def prepare_catalogue_view(catalogue: pd.DataFrame, *, view: str) -> pd.DataFrame:
    with _v6_context():
        return v5.prepare_catalogue_view(catalogue, view=view)


def evaluate_catalogue(catalogue: pd.DataFrame) -> pd.DataFrame:
    with _v6_context():
        return v5.evaluate_catalogue(catalogue)


def build_point_ranking(catalogue: pd.DataFrame, evaluation: pd.DataFrame) -> pd.DataFrame:
    with _v6_context():
        result = v5.build_point_ranking(catalogue, evaluation)
    is_thrils = result["source_key"].eq(THRILS_SOURCE_KEY)
    result.loc[is_thrils, "source_virial_sensitivity_note"] = (
        "THRILS statistical errors and +/-0.5 dex single-epoch calibration "
        "scenarios are separate"
    )
    return result


def build_uncertainty_summaries(
    catalogue: pd.DataFrame, *, n_samples: int = DEFAULT_N_SAMPLES,
    random_seed: int = DEFAULT_RANDOM_SEED,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    with _v6_context():
        return v5.build_uncertainty_summaries(
            catalogue, n_samples=n_samples, random_seed=random_seed,
        )


def build_uncertainty_ranking(
    point_ranking: pd.DataFrame,
    fedd_summary: pd.DataFrame,
    mseed_summary: pd.DataFrame,
) -> pd.DataFrame:
    with _v6_context():
        return v5.build_uncertainty_ranking(point_ranking, fedd_summary, mseed_summary)


def build_catalogue_summary(measurements: pd.DataFrame, objects: pd.DataFrame) -> pd.DataFrame:
    with _v6_context():
        result = v5.build_catalogue_summary(measurements, objects)
    result.loc[result["stratum_type"].eq("overall"), "selection_function_note"] = (
        "descriptive only: mixes JADES, CEERS/RUBIES, EIGER/FRESCO, ASPIRE, "
        "Harikane NIRSpec, and THRILS EELG/deep-G395M selection functions"
    )
    return result


def build_growth_summary(
    measurement_ranking: pd.DataFrame,
    object_ranking: pd.DataFrame,
) -> pd.DataFrame:
    with _v6_context():
        result = v5.build_growth_summary(measurement_ranking, object_ranking)
    result.loc[result["stratum_type"].eq("overall"), "selection_function_note"] = (
        "descriptive only: mixes JADES, CEERS/RUBIES, EIGER/FRESCO, ASPIRE, "
        "Harikane NIRSpec, and THRILS EELG/deep-G395M selection functions"
    )
    return result


def build_alternate_measurement_sensitivity(
    measurements: pd.DataFrame,
    objects: pd.DataFrame,
    *,
    n_samples: int = DEFAULT_N_SAMPLES,
    random_seed: int = DEFAULT_RANDOM_SEED,
) -> pd.DataFrame:
    with _v6_context():
        return v5.build_alternate_measurement_sensitivity(
            measurements, objects, n_samples=n_samples, random_seed=random_seed,
        )


def build_accretion_history_diagnostics(
    catalogue: pd.DataFrame, *, n_samples: int = DEFAULT_N_SAMPLES,
    random_seed: int = DEFAULT_RANDOM_SEED,
) -> pd.DataFrame:
    with _v6_context():
        return v5.build_accretion_history_diagnostics(
            catalogue, n_samples=n_samples, random_seed=random_seed,
        )


def build_primary_ranking_comparison(
    point_ranking: pd.DataFrame,
    uncertainty_ranking: pd.DataFrame,
) -> pd.DataFrame:
    with _v6_context():
        return v5.build_primary_ranking_comparison(point_ranking, uncertainty_ranking)


def _boolish(value: object) -> bool:
    if pd.isna(value):
        return False
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return bool(value)


def verify_v6_outputs(outputs: dict[str, pd.DataFrame], *, n_samples: int) -> dict[str, bool]:
    checks = {
        "measurement_count": len(outputs["measurement_point_ranking"]) == 112,
        "physical_object_count": len(outputs["object_point_ranking"]) == 105,
        "measurement_evaluation_count": len(outputs["measurement_evaluation"]) == 494,
        "object_evaluation_count": len(outputs["object_evaluation"]) == 469,
        "measurement_uncertainty_fedd_count": len(outputs["measurement_uncertainty_fedd"]) == 1482,
        "object_uncertainty_fedd_count": len(outputs["object_uncertainty_fedd"]) == 1407,
        "measurement_uncertainty_mseed_count": len(outputs["measurement_uncertainty_mseed"]) == 988,
        "object_uncertainty_mseed_count": len(outputs["object_uncertainty_mseed"]) == 938,
        "sample_count": outputs["measurement_uncertainty_fedd"]["n_samples"].eq(n_samples).all(),
        "alternate_measurement_sensitivity_count": len(outputs["alternate_measurement_sensitivity"]) == 7,
        "measurement_accretion_history_count": len(outputs["measurement_accretion_history"]) == 336,
        "object_accretion_history_count": len(outputs["object_accretion_history"]) == 315,
        "primary_ranking_comparison_count": len(outputs["primary_ranking_comparison"]) == 105,
        "primary_measurement_count": int(
            outputs["measurement_point_ranking"]["primary_growth_ranking_flag"].map(_boolish).sum()
        ) == 111,
        "primary_object_count": int(
            outputs["object_point_ranking"]["primary_growth_ranking_flag"].map(_boolish).sum()
        ) == 104,
        "taxonomy_in_rankings": all(
            set(TAXONOMY_FIELDS).issubset(outputs[name].columns)
            for name in [
                "measurement_point_ranking", "object_point_ranking",
                "measurement_uncertainty_ranking", "object_uncertainty_ranking",
            ]
        ),
        "all_point_ranks_contiguous": all(
            sorted(outputs[name]["rank_growth_pressure"].astype(int))
            == list(range(1, len(outputs[name]) + 1))
            for name in ["measurement_point_ranking", "object_point_ranking"]
        ),
        "all_uncertainty_ranks_contiguous": all(
            sorted(outputs[name]["rank_uncertainty_pressure"].astype(int))
            == list(range(1, len(outputs[name]) + 1))
            for name in ["measurement_uncertainty_ranking", "object_uncertainty_ranking"]
        ),
        "all_primary_ranks_contiguous": all(
            sorted(outputs[name][column].dropna().astype(int))
            == list(range(1, int(outputs[name][column].notna().sum()) + 1))
            for name, column in [
                ("measurement_point_ranking", "rank_primary_growth_pressure"),
                ("object_point_ranking", "rank_primary_growth_pressure"),
                ("measurement_uncertainty_ranking", "rank_primary_uncertainty_pressure"),
                ("object_uncertainty_ranking", "rank_primary_uncertainty_pressure"),
            ]
        ),
        "release_metadata": all(
            frame["catalogue_release"].eq(CATALOGUE_RELEASE).all()
            for frame in outputs.values()
        ),
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise ValueError(f"v6 output verification failed: {failed}")
    return checks
