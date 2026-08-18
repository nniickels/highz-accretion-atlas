"""Build the expanded BLAGN catalogue without mutating the v1 release.

The Taylor et al. source table is stored as a measurement table.  A separate
crossmatch table maps each measurement onto a stable physical-object ID, so
repeat spectra remain available while an object-level view can select one
preferred measurement deterministically.
"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

from src.standardize_data import (
    CANONICAL_RAW_FIELDS,
    STANDARDIZED_OUTPUT_COLUMNS,
    standardize_dataframe,
)


TAYLOR_SOURCE_KEY = "taylor24_ceers_rubies_blagn"
TAYLOR_PAPER_VERSION = "The Astrophysical Journal 986:165 (2025); arXiv:2409.06772v2"
TAYLOR_MASS_METHOD = "single-epoch-virial-halpha-reines2013"

TAYLOR_EXTRA_FIELDS = [
    "program",
    "field",
    "selection_channel",
    "broad_line_species",
    "halpha_flux_total_1e18_erg_s_cm2",
    "halpha_flux_total_err_plus",
    "halpha_flux_total_err_minus",
    "halpha_flux_narrow_1e18_erg_s_cm2",
    "halpha_flux_narrow_err_plus",
    "halpha_flux_narrow_err_minus",
    "halpha_flux_broad_1e18_erg_s_cm2",
    "halpha_flux_broad_err_plus",
    "halpha_flux_broad_err_minus",
    "halpha_broad_fwhm_km_s",
    "halpha_broad_fwhm_err_plus",
    "halpha_broad_fwhm_err_minus",
    "fwhm_instrument_corrected_flag",
    "lrd_flag",
    "lrd_definition",
    "halpha_absorption_fit_flag",
    "log_mbh_systematic_dex",
    "mbh_systematic_kind",
    "mbh_systematic_applied_flag",
    "mbh_formal_uncertainty_kind",
    "dust_correction_applied_flag",
    "source_caveat_tags",
    "source_paper_version",
    "source_url",
    "source_doi",
    "source_archive_url",
    "source_archive_sha256",
    "extraction_date",
    "selection_criteria",
]

TAYLOR_NUMERIC_FIELDS = [
    "halpha_flux_total_1e18_erg_s_cm2",
    "halpha_flux_total_err_plus",
    "halpha_flux_total_err_minus",
    "halpha_flux_narrow_1e18_erg_s_cm2",
    "halpha_flux_narrow_err_plus",
    "halpha_flux_narrow_err_minus",
    "halpha_flux_broad_1e18_erg_s_cm2",
    "halpha_flux_broad_err_plus",
    "halpha_flux_broad_err_minus",
    "halpha_broad_fwhm_km_s",
    "halpha_broad_fwhm_err_plus",
    "halpha_broad_fwhm_err_minus",
    "log_mbh_systematic_dex",
]

TAYLOR_FLAG_FIELDS = [
    "fwhm_instrument_corrected_flag",
    "lrd_flag",
    "halpha_absorption_fit_flag",
    "mbh_systematic_applied_flag",
    "dust_correction_applied_flag",
]

TAYLOR_REQUIRED_PUBLISHED_FIELDS = [
    "measurement_id",
    "object_id",
    "ra_deg",
    "dec_deg",
    "redshift",
    "redshift_kind",
    "survey",
    "program",
    "field",
    "log_mbh_msun",
    "log_mbh_err_plus",
    "log_mbh_err_minus",
    *TAYLOR_NUMERIC_FIELDS,
    *TAYLOR_FLAG_FIELDS,
    "lrd_definition",
    "source_caveat_tags",
    "source_url",
    "source_doi",
    "source_archive_url",
    "source_archive_sha256",
    "extraction_date",
    "selection_criteria",
]

UNPUBLISHED_OPTIONAL_FIELDS = [
    "log_mstar_msun",
    "log_mstar_err_plus",
    "log_mstar_err_minus",
    "mstar_method",
    "log_lbol_erg_s",
    "log_lbol_err_plus",
    "log_lbol_err_minus",
    "lbol_method",
    "edd_ratio_reported",
    "edd_ratio_err_plus",
    "edd_ratio_err_minus",
]

LINK_FIELDS = [
    "measurement_id",
    "physical_object_id",
    "preferred_measurement_flag",
    "preferred_measurement_reason",
    "match_method",
    "match_reference",
]


def _missing(series: pd.Series) -> pd.Series:
    return series.isna() | series.astype("string").str.strip().fillna("").eq("")


def _require_columns(df: pd.DataFrame, fields: Iterable[str], label: str) -> None:
    missing = sorted(set(fields) - set(df.columns))
    if missing:
        raise ValueError(f"{label} is missing columns: {missing}")


def _coerce_flags(df: pd.DataFrame, fields: Iterable[str]) -> pd.DataFrame:
    result = df.copy()
    for field in fields:
        numeric = pd.to_numeric(result[field], errors="coerce")
        invalid = numeric.isna() | ~numeric.isin([0, 1])
        if invalid.any():
            ids = result.loc[invalid, "measurement_id"].astype(str).head(5).tolist()
            raise ValueError(f"{field} must contain only 0/1; invalid rows: {ids}")
        result[field] = numeric.astype(bool)
    return result


def validate_taylor_raw(raw: pd.DataFrame) -> pd.DataFrame:
    """Validate the extracted Taylor Table 1 source contract."""
    _require_columns(raw, [*CANONICAL_RAW_FIELDS, *TAYLOR_EXTRA_FIELDS], "Taylor raw table")
    if len(raw) != 63:
        raise ValueError(f"Taylor Table 1 must contain 63 measurement rows, found {len(raw)}")
    if not raw["measurement_id"].is_unique:
        raise ValueError("Taylor measurement_id values must be unique")

    result = raw.copy()
    for field in TAYLOR_REQUIRED_PUBLISHED_FIELDS:
        if _missing(result[field]).any():
            raise ValueError(f"Taylor published/provenance field {field} cannot be missing")
    for field in TAYLOR_NUMERIC_FIELDS:
        original = result[field]
        result[field] = pd.to_numeric(original, errors="coerce")
        invalid = result[field].isna() & ~_missing(original)
        if invalid.any():
            raise ValueError(f"Taylor field {field} contains non-numeric values")
    result = _coerce_flags(result, TAYLOR_FLAG_FIELDS)

    exact_values = {
        "source_key": TAYLOR_SOURCE_KEY,
        "source_table": "Table 1 (Sample of BLAGN)",
        "source_paper_version": TAYLOR_PAPER_VERSION,
        "object_class": "broad-line-agn",
        "mbh_method": TAYLOR_MASS_METHOD,
        "detection_evidence": "individual_robust",
        "broad_line_species": "Halpha",
        "selection_channel": "broad-halpha",
        "mbh_systematic_kind": (
            "Approximate Reines et al. (2013) single-epoch virial-calibration scatter; "
            "may be larger at high redshift"
        ),
        "mbh_formal_uncertainty_kind": (
            "16th/84th percentiles from correlated Halpha flux and FWHM posteriors"
        ),
    }
    for field, expected in exact_values.items():
        if not result[field].eq(expected).all():
            raise ValueError(f"Taylor field {field} must equal {expected!r} for every row")

    for field in UNPUBLISHED_OPTIONAL_FIELDS:
        if (~_missing(result[field])).any():
            raise ValueError(f"Taylor field {field} must remain missing because Table 1 does not publish it")

    if not result["log_mbh_systematic_dex"].eq(0.5).all():
        raise ValueError("Taylor virial mass systematic must be recorded as approximately 0.5 dex")
    if result["mbh_systematic_applied_flag"].any():
        raise ValueError("Taylor virial systematic must not be folded into formal posterior errors")
    if result["dust_correction_applied_flag"].any():
        raise ValueError("Taylor Table 1 fluxes and masses are nominal, not dust corrected")

    nonnegative_fields = [
        *[field for field in TAYLOR_NUMERIC_FIELDS if "fwhm_km_s" not in field],
        "log_mbh_err_plus",
        "log_mbh_err_minus",
    ]
    for field in nonnegative_fields:
        if pd.to_numeric(result[field], errors="coerce").lt(0).any():
            raise ValueError(f"Taylor field {field} cannot contain negative values")
    if result["halpha_broad_fwhm_km_s"].le(700).any():
        raise ValueError("Taylor broad FWHM values must satisfy the published >700 km/s cut")
    if not result["fwhm_instrument_corrected_flag"].all():
        raise ValueError("Taylor Table 1 broad FWHM values must be marked instrument corrected")

    if int(result["lrd_flag"].sum()) != 21:
        raise ValueError("Taylor full-table LRD count must be 21")
    if int(result["halpha_absorption_fit_flag"].sum()) != 4:
        raise ValueError("Taylor full-table absorption-fit count must be 4")

    return result


def standardize_taylor(raw: pd.DataFrame, *, min_redshift: float = 4.0) -> pd.DataFrame:
    """Standardize Taylor measurements while retaining source-specific observables."""
    validated = validate_taylor_raw(raw)
    base = standardize_dataframe(
        validated[CANONICAL_RAW_FIELDS],
        project_version="expanded-blagn-v1",
        mbh_tag=TAYLOR_MASS_METHOD,
        lbol_tag="not-published-by-source",
        min_redshift=min_redshift,
    )
    extras = validated[["measurement_id", *TAYLOR_EXTRA_FIELDS]]
    return base.merge(extras, on="measurement_id", how="left", validate="one_to_one")


def validate_links(links: pd.DataFrame) -> pd.DataFrame:
    _require_columns(links, LINK_FIELDS, "measurement-object link table")
    result = _coerce_flags(links[LINK_FIELDS], ["preferred_measurement_flag"])
    if not result["measurement_id"].is_unique:
        raise ValueError("Link-table measurement_id values must be unique")
    if _missing(result["physical_object_id"]).any():
        raise ValueError("Every measurement link requires a physical_object_id")
    return result


def build_expanded_catalogues(
    v1_processed: pd.DataFrame,
    taylor_raw: pd.DataFrame,
    links: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return measurement- and physical-object-level expanded catalogue views."""
    _require_columns(v1_processed, STANDARDIZED_OUTPUT_COLUMNS, "v1 processed table")
    if not v1_processed["measurement_id"].is_unique:
        raise ValueError("v1 measurement_id values must be unique")

    taylor = standardize_taylor(taylor_raw, min_redshift=4.0)
    release_columns = [*STANDARDIZED_OUTPUT_COLUMNS, *TAYLOR_EXTRA_FIELDS]
    v1 = v1_processed.reindex(columns=release_columns).copy()
    taylor = taylor.reindex(columns=release_columns).copy()
    measurements = pd.concat([v1, taylor], ignore_index=True, sort=False)
    measurements["catalogue_release"] = "expanded-blagn-v1"
    if not measurements["measurement_id"].is_unique:
        raise ValueError("Combined release measurement_id values must be unique")

    validated_links = validate_links(links)
    active_links = validated_links[
        validated_links["measurement_id"].isin(measurements["measurement_id"])
    ].copy()
    missing_links = sorted(set(measurements["measurement_id"]) - set(active_links["measurement_id"]))
    if missing_links:
        raise ValueError(f"Expanded measurements missing physical-object links: {missing_links[:5]}")
    measurements = measurements.merge(
        active_links,
        on="measurement_id",
        how="left",
        validate="one_to_one",
    )

    preferred_counts = measurements.groupby("physical_object_id")["preferred_measurement_flag"].sum()
    invalid_preference = preferred_counts[preferred_counts != 1]
    if not invalid_preference.empty:
        raise ValueError(
            "Each physical object must have exactly one preferred measurement: "
            f"{invalid_preference.index.tolist()[:5]}"
        )

    group = measurements.groupby("physical_object_id", sort=False)
    aggregates = group.agg(
        n_measurements=("measurement_id", "size"),
        available_measurement_ids=("measurement_id", lambda values: ";".join(values.astype(str))),
        available_object_ids=("object_id", lambda values: ";".join(values.astype(str))),
    ).reset_index()
    objects = measurements[measurements["preferred_measurement_flag"]].copy()
    objects = objects.merge(aggregates, on="physical_object_id", how="left", validate="one_to_one")

    identifier_fields = [
        "catalogue_release",
        "physical_object_id",
        "measurement_id",
        "object_id",
    ]
    measurements = measurements[
        identifier_fields
        + [column for column in measurements.columns if column not in identifier_fields]
    ].sort_values(["source_key", "redshift", "measurement_id"], ascending=[True, False, True])
    objects = objects[
        identifier_fields
        + ["n_measurements", "available_measurement_ids", "available_object_ids"]
        + [
            column
            for column in objects.columns
            if column not in identifier_fields
            and column not in {"n_measurements", "available_measurement_ids", "available_object_ids"}
        ]
    ].sort_values(["source_key", "redshift", "physical_object_id"], ascending=[True, False, True])

    return measurements.reset_index(drop=True), objects.reset_index(drop=True)
