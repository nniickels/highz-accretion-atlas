"""Science workflow for the v5 BLAGN measurement-version release.

v5 inherits the verified v4 mathematics and scenario definitions. Harikane
et al. (2023) rows receive the baseline and global +/-0.3 dex comparison
scenarios only because that source does not publish a numeric virial
calibration systematic. Statistical errors remain sampled separately.
"""

from __future__ import annotations

import pandas as pd

from src import v4_science as v4
from src.v5_catalogue import CATALOGUE_RELEASE, HARIKANE_SOURCE_KEY


Z_SEED = v4.Z_SEED
EPSILON = v4.EPSILON
MERGER_BOOST = v4.MERGER_BOOST
DEFAULT_RANDOM_SEED = v4.DEFAULT_RANDOM_SEED
DEFAULT_N_SAMPLES = v4.DEFAULT_N_SAMPLES


def _release(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    if "catalogue_release" in result:
        result["catalogue_release"] = CATALOGUE_RELEASE
    if "input_catalogue_release" in result:
        result["input_catalogue_release"] = CATALOGUE_RELEASE
    return result


def prepare_catalogue_view(catalogue: pd.DataFrame, *, view: str) -> pd.DataFrame:
    return _release(v4.prepare_catalogue_view(catalogue, view=view))


def evaluate_catalogue(catalogue: pd.DataFrame) -> pd.DataFrame:
    return _release(v4.evaluate_catalogue(catalogue))


def build_point_ranking(catalogue: pd.DataFrame, evaluation: pd.DataFrame) -> pd.DataFrame:
    result = _release(v4.build_point_ranking(catalogue, evaluation))
    harikane = result["source_key"].eq(HARIKANE_SOURCE_KEY)
    result.loc[harikane, "source_virial_sensitivity_note"] = (
        "Harikane statistical errors are propagated; no numeric virial-calibration "
        "systematic is published, so no source-specific scenario is inferred"
    )
    return result


def build_uncertainty_summaries(
    catalogue: pd.DataFrame, *, n_samples: int = DEFAULT_N_SAMPLES,
    random_seed: int = DEFAULT_RANDOM_SEED,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    fedd, mseed = v4.build_uncertainty_summaries(
        catalogue, n_samples=n_samples, random_seed=random_seed,
    )
    return _release(fedd), _release(mseed)


def build_uncertainty_ranking(
    point_ranking: pd.DataFrame, fedd_summary: pd.DataFrame, mseed_summary: pd.DataFrame,
) -> pd.DataFrame:
    return _release(v4.build_uncertainty_ranking(point_ranking, fedd_summary, mseed_summary))


def build_catalogue_summary(measurements: pd.DataFrame, objects: pd.DataFrame) -> pd.DataFrame:
    result = _release(v4.build_catalogue_summary(measurements, objects))
    result.loc[result["stratum_type"].eq("overall"), "selection_function_note"] = (
        "descriptive only: mixes JADES, CEERS/RUBIES, EIGER/FRESCO, ASPIRE, "
        "and Harikane NIRSpec selection functions"
    )
    return result


def build_growth_summary(
    measurement_ranking: pd.DataFrame, object_ranking: pd.DataFrame,
) -> pd.DataFrame:
    return _release(v4.build_growth_summary(measurement_ranking, object_ranking))


def build_alternate_measurement_sensitivity(
    measurements: pd.DataFrame, objects: pd.DataFrame, *,
    n_samples: int = DEFAULT_N_SAMPLES, random_seed: int = DEFAULT_RANDOM_SEED,
) -> pd.DataFrame:
    return _release(v4.build_alternate_measurement_sensitivity(
        measurements, objects, n_samples=n_samples, random_seed=random_seed,
    ))


def verify_v5_outputs(outputs: dict[str, pd.DataFrame], *, n_samples: int) -> dict[str, bool]:
    checks = {
        "measurement_count": len(outputs["measurement_point_ranking"]) == 106,
        "physical_object_count": len(outputs["object_point_ranking"]) == 99,
        "measurement_evaluation_count": len(outputs["measurement_evaluation"]) == 464,
        "object_evaluation_count": len(outputs["object_evaluation"]) == 439,
        "measurement_uncertainty_fedd_count": len(outputs["measurement_uncertainty_fedd"]) == 1392,
        "object_uncertainty_fedd_count": len(outputs["object_uncertainty_fedd"]) == 1317,
        "measurement_uncertainty_mseed_count": len(outputs["measurement_uncertainty_mseed"]) == 928,
        "object_uncertainty_mseed_count": len(outputs["object_uncertainty_mseed"]) == 878,
        "sample_count": outputs["measurement_uncertainty_fedd"]["n_samples"].eq(n_samples).all(),
        "alternate_measurement_sensitivity_count": len(outputs["alternate_measurement_sensitivity"]) == 7,
        "release_metadata": all(
            frame["catalogue_release"].eq(CATALOGUE_RELEASE).all() for frame in outputs.values()
        ),
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise ValueError(f"v5 output verification failed: {failed}")
    return checks
