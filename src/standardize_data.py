## This code defines functions for standardizing raw accretion-candidate tables

# ---------------------------------- Imports -----------------------------------------------------

from __future__ import annotations
from pathlib import Path
from typing import Dict, Iterable, Optional
import numpy as np
import pandas as pd

# ---------------------------------- Variables ---------------------------------------------------

# Canonical raw semantic fields expected by the standardizer.
CANONICAL_RAW_FIELDS = [
    "measurement_id", "object_id", "ra_deg", "dec_deg", "redshift", "survey", "object_class",
    "log_mbh_msun", "log_mbh_err_plus", "log_mbh_err_minus", "mbh_method",
    "log_mstar_msun", "log_mstar_err_plus", "log_mstar_err_minus", "mstar_method",
    "log_lbol_erg_s", "log_lbol_err_plus", "log_lbol_err_minus", "lbol_method",
    "edd_ratio_reported", "edd_ratio_err_plus", "edd_ratio_err_minus",
    "source_key", "notes",
]

# Default 1:1 mapping for raw files that already use canonical names.
DEFAULT_COLUMN_MAP = {name: name for name in CANONICAL_RAW_FIELDS}

# Processed data CSV columns 
STANDARDIZED_OUTPUT_COLUMNS = [
    "measurement_id", "object_id", "ra_deg", "dec_deg", "redshift", "cosmic_time_gyr",
    "survey", "object_class",
    "log_mbh_msun_std", "log_mbh_err_plus_std", "log_mbh_err_minus_std",
    "log_mstar_msun_std", "log_mstar_err_plus_std", "log_mstar_err_minus_std",
    "log_lbol_erg_s_std", "log_lbol_err_plus_std", "log_lbol_err_minus_std",
    "log_mbh_mstar_ratio", "log_mbh_mstar_ratio_err",
    "edd_ratio_std", "edd_ratio_err_std",
    "mbh_interpretation_tag", "mstar_interpretation_tag", "lbol_interpretation_tag",
    "quality_flag", "project_version", "source_key", "notes",
]

# ------------------------------ Functions -----------------------------------------------------

def cosmic_time_gyr(
    redshift: Iterable[float] | np.ndarray,
    h0_km_s_mpc: float = 70.0,
    omega_m: float = 0.3,
    omega_lambda: float = 0.7,
) -> np.ndarray:
    """Return cosmic age in Gyr for each redshift using a flat-ΛCDM closed form.

    Notes:
    - Valid for flat cosmology (Ω_k = 0) with matter + dark energy only.
    - Good for reproducible comparisons in v1; detailed cosmology sweeps belong in models.
    """
    z = np.asarray(redshift, dtype=float)
    h0_s = h0_km_s_mpc * 1000.0 / 3.0856775814913673e22
    sec_per_gyr = 3.15576e16
    prefactor_gyr = (2.0 / (3.0 * h0_s * np.sqrt(omega_lambda))) / sec_per_gyr
    arg = np.sqrt(omega_lambda / omega_m) / np.power(1.0 + z, 1.5)
    return prefactor_gyr * np.arcsinh(arg)

def read_raw_csv(path: str | Path, *, dtype_overrides: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """Read a raw CSV file into a dataframe.

    Use `dtype_overrides` if a source needs explicit typing for fragile columns.
    """
    path = Path(path)
    return pd.read_csv(path, dtype=dtype_overrides)

def remap_to_canonical(
    raw_df: pd.DataFrame,
    column_map: Optional[Dict[str, str]] = None,
) -> pd.DataFrame:
    """Map arbitrary input column names into canonical raw semantic fields.

    Args:
        raw_df: raw source dataframe with source-specific column names.
        column_map: mapping of canonical_name -> source_column_name.
            Example: {"redshift": "z_spec", "log_mbh_msun": "logMBH"}
            If omitted, `DEFAULT_COLUMN_MAP` is used (identity map).
    """
    cmap = DEFAULT_COLUMN_MAP if column_map is None else {**DEFAULT_COLUMN_MAP, **column_map}

    missing_source_cols = sorted({src_col for src_col in cmap.values() if src_col not in raw_df.columns})
    if missing_source_cols:
        raise ValueError(f"Input dataframe missing mapped source columns: {missing_source_cols}")

    renamed = raw_df.rename(columns={src: canon for canon, src in cmap.items()})
    return renamed

def validate_canonical_raw_schema(canonical_df: pd.DataFrame) -> None:
    """Validate that canonical semantic fields required for v1 exist."""
    missing = sorted(set(CANONICAL_RAW_FIELDS) - set(canonical_df.columns))
    if missing:
        raise ValueError(f"Missing canonical raw fields: {missing}")

def standardize_dataframe(
    canonical_df: pd.DataFrame,
    *,
    project_version: str = "v1",
    mbh_tag: str = "single-epoch-virial",
    lbol_tag: str = "balmer-line-bolometric-correction",
) -> pd.DataFrame:
    """Convert canonical raw dataframe to standardized v1 dataframe."""
    validate_canonical_raw_schema(canonical_df)

    std = canonical_df.copy()

    # Ensure numeric fields are numeric where applicable.
    numeric_cols = [
        "ra_deg", "dec_deg", "redshift",
        "log_mbh_msun", "log_mbh_err_plus", "log_mbh_err_minus",
        "log_mstar_msun", "log_mstar_err_plus", "log_mstar_err_minus",
        "log_lbol_erg_s", "log_lbol_err_plus", "log_lbol_err_minus",
        "edd_ratio_reported", "edd_ratio_err_plus", "edd_ratio_err_minus",
    ]
    for col in numeric_cols:
        std[col] = pd.to_numeric(std[col], errors="coerce")

    std["cosmic_time_gyr"] = cosmic_time_gyr(std["redshift"])

    std["log_mbh_msun_std"] = std["log_mbh_msun"]
    std["log_mbh_err_plus_std"] = std["log_mbh_err_plus"]
    std["log_mbh_err_minus_std"] = std["log_mbh_err_minus"]

    std["log_mstar_msun_std"] = std["log_mstar_msun"]
    std["log_mstar_err_plus_std"] = std["log_mstar_err_plus"]
    std["log_mstar_err_minus_std"] = std["log_mstar_err_minus"]

    std["log_lbol_erg_s_std"] = std["log_lbol_erg_s"]
    std["log_lbol_err_plus_std"] = std["log_lbol_err_plus"]
    std["log_lbol_err_minus_std"] = std["log_lbol_err_minus"]

    std["edd_ratio_std"] = std["edd_ratio_reported"]
    std["edd_ratio_err_std"] = std[["edd_ratio_err_plus", "edd_ratio_err_minus"]].mean(axis=1, skipna=True)

    std["log_mbh_mstar_ratio"] = std["log_mbh_msun_std"] - std["log_mstar_msun_std"]
    mbh_sigma = std[["log_mbh_err_plus_std", "log_mbh_err_minus_std"]].mean(axis=1, skipna=True)
    mstar_sigma = std[["log_mstar_err_plus_std", "log_mstar_err_minus_std"]].mean(axis=1, skipna=True)
    std["log_mbh_mstar_ratio_err"] = np.sqrt(mbh_sigma**2 + mstar_sigma**2)

    std["mbh_interpretation_tag"] = mbh_tag
    std["mstar_interpretation_tag"] = np.where(
        std["log_mstar_msun_std"].notna(),
        "host-sed-with-agn-contamination-risk",
        "missing-host-mstar",
    )
    std["lbol_interpretation_tag"] = lbol_tag

    std["quality_flag"] = np.where(
        std["notes"].fillna("").str.startswith("Robust sample"),
        "robust",
        "tentative",
    )
    std["project_version"] = project_version

    standardized = std[STANDARDIZED_OUTPUT_COLUMNS].copy()

    # Minimal reproducibility checks.
    if not standardized["measurement_id"].is_unique:
        raise ValueError("measurement_id must be unique")
    if (standardized["redshift"] < 0).any():
        raise ValueError("redshift must be non-negative")
    if (standardized["cosmic_time_gyr"] <= 0).any():
        raise ValueError("cosmic_time_gyr must be positive")

    return standardized

def standardize_raw_csv(
    path: str | Path,
    *,
    column_map: Optional[Dict[str, str]] = None,
    dtype_overrides: Optional[Dict[str, str]] = None,
    project_version: str = "v1",                              
) -> pd.DataFrame:
    """
    Steps:
    1) reads raw CSV
    2) remaps source columns to canonical names
    3) standardizes to output schema (given project version input)
    4) return dataframe 
    """
    raw_df = read_raw_csv(path, dtype_overrides=dtype_overrides)
    canonical_df = remap_to_canonical(raw_df, column_map=column_map)
    return standardize_dataframe(canonical_df, project_version=project_version)
