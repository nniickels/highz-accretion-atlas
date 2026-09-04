"""Selection-function metadata and demographic-inference gates."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = (
    "source_key", "selection_model_status", "parent_sample_n", "published_selected_n",
    "survey_area_arcmin2", "completeness_kind", "completeness_value",
    "completeness_scope", "published_threshold", "inverse_weighting_allowed",
    "demographic_use", "verification_date", "notes",
)
MODEL_STATUSES = {"not_quantifiable", "source_local_partial"}
DEMOGRAPHIC_USES = {
    "descriptive_only", "source_local_fraction_only",
    "source_local_luminosity_function_only",
}


def load_selection_registry(path: str | Path) -> pd.DataFrame:
    registry = pd.read_csv(path, dtype=str, keep_default_na=False)
    if tuple(registry.columns) != REQUIRED_COLUMNS:
        raise AssertionError("selection registry columns do not match the contract")
    if registry.empty or registry.isna().any().any() or (registry == "").any().any():
        raise AssertionError("selection registry fields must be nonblank")
    if not registry["source_key"].is_unique:
        raise AssertionError("selection registry source_key values must be unique")
    if not set(registry["selection_model_status"]).issubset(MODEL_STATUSES):
        raise AssertionError("selection registry has an unknown model status")
    if not set(registry["demographic_use"]).issubset(DEMOGRAPHIC_USES):
        raise AssertionError("selection registry has an unknown demographic-use status")
    if not registry["inverse_weighting_allowed"].eq("false").all():
        raise AssertionError("inverse weights require a validated inclusion-probability model")
    return registry


def build_selection_summary(measurements: pd.DataFrame, registry: pd.DataFrame) -> pd.DataFrame:
    """Join catalogue coverage to published source-level selection metadata."""
    eligible = measurements["growth_ranking_eligible_flag"].map(
        lambda value: str(value).strip().lower() == "true"
    )
    measurements = measurements.assign(
        _growth_plottable=eligible,
        _growth_plottable_object=measurements["physical_object_id"].where(eligible),
    )
    observed = (
        measurements.groupby("source_key", sort=True)
        .agg(
            catalogue_measurements=("measurement_id", "size"),
            catalogue_objects=("physical_object_id", "nunique"),
            growth_plottable_measurements=("_growth_plottable", "sum"),
            growth_plottable_objects=("_growth_plottable_object", "nunique"),
        )
        .reset_index()
    )
    missing = sorted(set(observed["source_key"]) - set(registry["source_key"]))
    if missing:
        raise AssertionError(f"selection registry missing catalogue sources: {missing}")
    result = observed.merge(registry, on="source_key", how="left", validate="one_to_one")
    result["pooled_demographic_inference_allowed"] = False
    result["catalogue_inverse_probability_weight"] = pd.NA
    result["inference_gate_reason"] = (
        "no validated cross-source inclusion-probability model; use only the declared source-local scope"
    )
    return result
