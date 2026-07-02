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
    "measurement_id", "object_id", "ra_deg", "dec_deg", "redshift", "redshift_kind",
    "survey", "object_class",
    "log_mbh_msun", "log_mbh_err_plus", "log_mbh_err_minus", "mbh_method",
    "log_mstar_msun", "log_mstar_err_plus", "log_mstar_err_minus", "mstar_method",
    "log_lbol_erg_s", "log_lbol_err_plus", "log_lbol_err_minus", "lbol_method",
    "edd_ratio_reported", "edd_ratio_err_plus", "edd_ratio_err_minus",
    "agn_contam_flag", "lensing_mu", "lensing_mu_err",
    "source_key", "source_table", "notes",
]

# Default 1:1 mapping for raw files that already use canonical names.
DEFAULT_COLUMN_MAP = {name: name for name in CANONICAL_RAW_FIELDS}

REQUIRED_VALUE_FIELDS = [
    "measurement_id", "object_id", "redshift", "log_mbh_msun", "mbh_method",
    "source_key", "source_table", "redshift_kind",
]

NUMERIC_RAW_FIELDS = [
    "ra_deg", "dec_deg", "redshift",
    "log_mbh_msun", "log_mbh_err_plus", "log_mbh_err_minus",
    "log_mstar_msun", "log_mstar_err_plus", "log_mstar_err_minus",
    "log_lbol_erg_s", "log_lbol_err_plus", "log_lbol_err_minus",
    "edd_ratio_reported", "edd_ratio_err_plus", "edd_ratio_err_minus",
    "agn_contam_flag", "lensing_mu", "lensing_mu_err",
]

OPTIONAL_FIELD_GROUPS = {
    "mstar": ["log_mstar_msun", "log_mstar_err_plus", "log_mstar_err_minus", "mstar_method"],
    "lbol": ["log_lbol_erg_s", "log_lbol_err_plus", "log_lbol_err_minus", "lbol_method"],
    "edd_ratio": ["edd_ratio_reported", "edd_ratio_err_plus", "edd_ratio_err_minus"],
    "lensing": ["lensing_mu", "lensing_mu_err"],
}

# Processed data CSV columns
STANDARDIZED_OUTPUT_COLUMNS = [
    "measurement_id", "object_id", "ra_deg", "dec_deg", "redshift", "redshift_kind",
    "cosmic_time_gyr",
    "survey", "object_class",
    "log_mbh_msun_std", "log_mbh_err_plus_std", "log_mbh_err_minus_std",
    "mbh_method",
    "log_mstar_msun_std", "log_mstar_err_plus_std", "log_mstar_err_minus_std",
    "mstar_method",
    "log_lbol_erg_s_std", "log_lbol_err_plus_std", "log_lbol_err_minus_std",
    "lbol_method",
    "log_mbh_mstar_ratio", "log_mbh_mstar_ratio_err",
    "edd_ratio_std", "edd_ratio_err_std",
    "agn_contam_flag", "lensing_mu", "lensing_mu_err",
    "missing_mstar_flag", "missing_lbol_flag", "missing_edd_ratio_flag",
    "missing_lensing_flag", "missing_optional_fields",
    "mbh_interpretation_tag", "mstar_interpretation_tag", "lbol_interpretation_tag",
    "quality_flag", "project_version", "source_key", "source_table", "notes",
]

# ------------------------------ Functions -----------------------------------------------------

def cosmic_time_gyr(
    redshift: Iterable[float] | np.ndarray,
    h0_km_s_mpc: float = 67.3,
    omega_m: float = 0.315,
    omega_lambda: float = 0.685,
) -> np.ndarray:
    """Return cosmic age in Gyr for each redshift using a flat-ΛCDM closed form.

    Notes:
    - Valid for flat cosmology (Ω_k = 0) with matter + dark energy only.
    - Defaults to the Planck 2018-style values H0=67.3 km/s/Mpc,
      Omega_m=0.315, and Omega_Lambda=0.685.
    - Detailed cosmology sweeps belong in models.
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

def _is_missing(series: pd.Series) -> pd.Series:
    """Return True for NaN or blank-string cells."""
    return series.isna() | series.astype("string").str.strip().fillna("").eq("")

def _format_row_ids(df: pd.DataFrame, mask: pd.Series, *, limit: int = 5) -> str:
    """Return compact measurement identifiers for validation errors."""
    if "measurement_id" not in df.columns:
        return "<measurement_id unavailable>"
    ids = df.loc[mask, "measurement_id"].astype("string").fillna("<missing>").head(limit).tolist()
    suffix = "" if int(mask.sum()) <= limit else f", ... ({int(mask.sum())} rows)"
    return ", ".join(ids) + suffix

def _coerce_numeric_columns(df: pd.DataFrame, numeric_cols: Iterable[str]) -> pd.DataFrame:
    """Convert numeric columns and fail if a nonblank value cannot be parsed."""
    converted_df = df.copy()
    for col in numeric_cols:
        original = converted_df[col]
        converted = pd.to_numeric(original, errors="coerce")
        invalid = converted.isna() & ~_is_missing(original)
        if invalid.any():
            ids = _format_row_ids(converted_df, invalid)
            raise ValueError(f"Column {col!r} has non-numeric values for rows: {ids}")
        converted_df[col] = converted
    return converted_df

def _missing_group_columns(df: pd.DataFrame, cols: list[str]) -> pd.Series:
    """Return True when all columns in an optional measurement group are missing."""
    return pd.concat([_is_missing(df[col]) for col in cols], axis=1).all(axis=1)

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

def validate_required_values(canonical_df: pd.DataFrame) -> None:
    """Validate required v1 identifiers, measurements, and provenance are present."""
    for col in REQUIRED_VALUE_FIELDS:
        missing = _is_missing(canonical_df[col])
        if missing.any():
            ids = _format_row_ids(canonical_df, missing)
            raise ValueError(f"Required column {col!r} has missing values for rows: {ids}")

    if not canonical_df["measurement_id"].is_unique:
        duplicated = canonical_df["measurement_id"].duplicated(keep=False)
        ids = _format_row_ids(canonical_df, duplicated)
        raise ValueError(f"measurement_id must be unique; duplicates found for rows: {ids}")

def validate_optional_missingness(canonical_df: pd.DataFrame) -> None:
    """Validate optional groups are either present with methods or explicitly allowed missing."""
    mstar_present = canonical_df["log_mstar_msun"].notna()
    mstar_method_missing = _is_missing(canonical_df["mstar_method"])
    if (mstar_present & mstar_method_missing).any():
        ids = _format_row_ids(canonical_df, mstar_present & mstar_method_missing)
        raise ValueError(f"Mstar values require mstar_method for rows: {ids}")

    lbol_present = canonical_df["log_lbol_erg_s"].notna()
    lbol_method_missing = _is_missing(canonical_df["lbol_method"])
    if (lbol_present & lbol_method_missing).any():
        ids = _format_row_ids(canonical_df, lbol_present & lbol_method_missing)
        raise ValueError(f"Lbol values require lbol_method for rows: {ids}")

def standardize_dataframe(
    canonical_df: pd.DataFrame,
    *,
    project_version: str = "v1",
    mbh_tag: str = "single-epoch-virial",
    lbol_tag: str = "balmer-line-bolometric-correction",
    min_redshift: float = 4.0,
) -> pd.DataFrame:
    """Convert canonical raw dataframe to standardized v1 dataframe.

    Args:
        canonical_df: dataframe using canonical raw semantic field names.
        project_version: version label written to output rows.
        mbh_tag: default MBH interpretation tag for v1.
        lbol_tag: default Lbol interpretation tag for v1.
        min_redshift: keep only rows with redshift >= this value; set to None to disable.
    """
    validate_canonical_raw_schema(canonical_df)

    std = _coerce_numeric_columns(canonical_df, NUMERIC_RAW_FIELDS)
    validate_required_values(std)
    validate_optional_missingness(std)
    
    if min_redshift is not None:
        if (std["redshift"] < float(min_redshift)).all():
            raise ValueError(f"No rows remain after redshift >= {min_redshift:g} filter")
        std = std[std["redshift"] >= float(min_redshift)].copy()

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

    std["missing_mstar_flag"] = _is_missing(std["log_mstar_msun"])
    std["missing_lbol_flag"] = _is_missing(std["log_lbol_erg_s"])
    std["missing_edd_ratio_flag"] = _is_missing(std["edd_ratio_reported"])
    std["missing_lensing_flag"] = _missing_group_columns(std, OPTIONAL_FIELD_GROUPS["lensing"])

    optional_names = ["mstar", "lbol", "edd_ratio", "lensing"]
    optional_flag_cols = [f"missing_{name}_flag" for name in optional_names]
    std["missing_optional_fields"] = [
        ";".join(name for name, flag in zip(optional_names, flags, strict=True) if bool(flag))
        for flags in std[optional_flag_cols].itertuples(index=False, name=None)
    ]

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

    # Reproducibility checks after filtering and column assembly.
    if not standardized["measurement_id"].is_unique:
        raise ValueError("measurement_id must be unique")
    if min_redshift is not None and (standardized["redshift"] < float(min_redshift)).any():
        raise ValueError(f"redshift must be >= {min_redshift:g} after filtering")
    if (standardized["cosmic_time_gyr"] <= 0).any():
        raise ValueError("cosmic_time_gyr must be positive")
    if standardized["log_mbh_msun_std"].isna().any():
        raise ValueError("log_mbh_msun_std cannot be missing")
    if standardized["source_key"].isna().any() or standardized["source_table"].isna().any():
        raise ValueError("source_key and source_table cannot be missing")

    return standardized

def standardize_raw_csv(
    path: str | Path,
    *,
    column_map: Optional[Dict[str, str]] = None,
    dtype_overrides: Optional[Dict[str, str]] = None,
    project_version: str = "v1",
    min_redshift: float = 4.0,                        
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
    return standardize_dataframe(
        canonical_df,
        project_version=project_version,
        min_redshift=min_redshift,
    )
