"""Validated source/method metadata for virial-mass systematics.

The registry is descriptive.  A numeric value is never inferred from another
paper or automatically combined with a source-reported statistical error.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


REGISTRY_REQUIRED_COLUMNS = {
    "source_key", "mbh_method", "calibration_tag", "line_species",
    "calibration_reference", "calibration_equation", "reported_systematic_dex",
    "systematic_scope", "source_support", "scenario_policy", "notes",
}


def load_mass_method_registry(path: str | Path) -> pd.DataFrame:
    """Load and validate the source/method registry without filling blanks."""
    registry = pd.read_csv(path)
    if missing := REGISTRY_REQUIRED_COLUMNS - set(registry.columns):
        raise ValueError(f"Mass-method registry missing fields: {sorted(missing)}")
    keys = ["source_key", "mbh_method"]
    if registry.duplicated(keys).any():
        raise ValueError("Mass-method registry contains duplicate source/method rows")
    for column in ["source_key", "mbh_method", "calibration_tag", "calibration_reference", "source_support"]:
        if registry[column].isna().any() or registry[column].astype(str).str.strip().eq("").any():
            raise ValueError(f"Mass-method registry requires nonblank {column}")
    numeric = pd.to_numeric(registry["reported_systematic_dex"], errors="coerce")
    invalid_numeric = registry["reported_systematic_dex"].notna() & numeric.isna()
    if invalid_numeric.any() or numeric.dropna().le(0).any():
        raise ValueError("reported_systematic_dex must be blank or positive numeric dex")
    registry["reported_systematic_dex"] = numeric
    return registry


def validate_catalogue_method_coverage(catalogue: pd.DataFrame, registry: pd.DataFrame) -> None:
    """Require every catalogue source/method pair to have reviewed metadata."""
    keys = ["source_key", "mbh_method"]
    if missing := set(keys) - set(catalogue.columns):
        raise ValueError(f"Catalogue missing mass-method keys: {sorted(missing)}")
    catalogue_pairs = set(map(tuple, catalogue[keys].drop_duplicates().astype(str).to_numpy()))
    registry_pairs = set(map(tuple, registry[keys].astype(str).to_numpy()))
    if missing_pairs := catalogue_pairs - registry_pairs:
        raise ValueError(f"Unregistered catalogue mass methods: {sorted(missing_pairs)}")

