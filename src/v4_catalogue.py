"""Build the v4 same-class BLAGN catalogue without mutating v1--v3."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

from src.identity import (
    apply_reviewed_identity_overrides, candidate_matches, cross_source_candidate_matches,
    require_unambiguous_candidates, stable_object_id,
)
from src.standardize_data import CANONICAL_RAW_FIELDS, LOG10_EDDINGTON_LUMINOSITY_PER_MSUN, standardize_dataframe


CATALOGUE_RELEASE = "v4-blagn"
MASS_METHOD = "single-epoch-virial-halpha-reines2013"
MATTHEE_SOURCE_KEY = "matthee23_eiger_fresco_blagn"
ASPIRE_SOURCE_KEY = "lin24_aspire_blagn"
MATTHEE_PAPER_VERSION = "The Astrophysical Journal 963:129 (2024); arXiv:2306.05448v3"
ASPIRE_PAPER_VERSION = "The Astrophysical Journal 974:147 (2024); arXiv:2407.17570v1"

SOURCE_CONFIG = {
    MATTHEE_SOURCE_KEY: {
        "rows": 20,
        "source_table": "Tables 1-3",
        "paper_version": MATTHEE_PAPER_VERSION,
        "url": "https://doi.org/10.3847/1538-4357/ad2345",
        "doi": "10.3847/1538-4357/ad2345",
        "archive_url": "https://arxiv.org/e-print/2306.05448v3",
        "archive_sha256": "b3e6f5385e694d92a7456f81eb123a305468baf743cebc7aeea820befb9b1190",
        "selection": "broad Halpha S/N >5; broad Halpha luminosity >2e42 erg/s; broad FWHM >1000 km/s; visual rejection of spatial-broadening impostors",
        "lbol_method": "broad-halpha-to-l5100-greene-ho2005;bolometric-correction-richards2006",
    },
    ASPIRE_SOURCE_KEY: {
        "rows": 16,
        "source_table": "Tables 1-3",
        "paper_version": ASPIRE_PAPER_VERSION,
        "url": "https://doi.org/10.3847/1538-4357/ad6565",
        "doi": "10.3847/1538-4357/ad6565",
        "archive_url": "https://arxiv.org/e-print/2407.17570v1",
        "archive_sha256": "fc1c4d96e4a568b09b3caefa0fdde1c7fabe8decad71fb6423ff37c912b024cd",
        "selection": "compact red photometric preselection; integrated line S/N >5; robust broad Halpha FWHM >1000 km/s; visual artifact and contamination rejection",
        "lbol_method": "broad-halpha-to-l5100-greene-ho2005;bolometric-correction-richards2006",
    },
}

SOURCE_EXTRA_FIELDS = [
    "program", "field", "selection_channel", "broad_line_species", "redshift_err",
    "published_ra", "published_dec", "halpha_broad_to_total_ratio",
    "halpha_broad_to_total_ratio_err", "halpha_lum_broad_1e42",
    "halpha_lum_broad_err_plus", "halpha_lum_broad_err_minus",
    "halpha_lum_total_1e42", "halpha_lum_total_err_plus", "halpha_lum_total_err_minus",
    "halpha_broad_fwhm_km_s", "halpha_broad_fwhm_err_plus", "halpha_broad_fwhm_err_minus",
    "halpha_narrow_fwhm_km_s", "halpha_narrow_fwhm_err_plus", "halpha_narrow_fwhm_err_minus",
    "halpha_ew_rest_angstrom", "halpha_ew_err_plus", "halpha_ew_err_minus",
    "photometry_band", "photometry_mag", "photometry_mag_err_plus", "photometry_mag_err_minus",
    "f200w_mag", "f200w_err_plus", "f200w_err_minus", "muv", "muv_err_plus", "muv_err_minus",
    "beta_uv", "beta_uv_err_plus", "beta_uv_err_minus", "beta_opt", "beta_opt_err_plus",
    "beta_opt_err_minus", "delta_m_lw", "lbol_1e44_erg_s", "lbol_1e44_err_plus",
    "lbol_1e44_err_minus", "lrd_flag", "lrd_definition", "halpha_absorption_fit_flag",
    "log_mbh_systematic_dex", "mbh_systematic_kind", "mbh_systematic_applied_flag",
    "mbh_formal_uncertainty_kind", "dust_correction_applied_flag", "source_caveat_tags",
    "source_paper_version", "source_url", "source_doi", "source_archive_url",
    "source_archive_sha256", "extraction_date", "selection_criteria",
]


def _require_columns(df: pd.DataFrame, fields: Iterable[str], label: str) -> None:
    if missing := sorted(set(fields) - set(df.columns)):
        raise ValueError(f"{label} missing columns: {missing}")


def _native_lbol_to_log(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    native = pd.to_numeric(result["lbol_1e44_erg_s"], errors="coerce")
    plus = pd.to_numeric(result["lbol_1e44_err_plus"], errors="coerce")
    minus = pd.to_numeric(result["lbol_1e44_err_minus"], errors="coerce")
    mask = native.notna()
    result.loc[mask, "log_lbol_erg_s"] = 44.0 + np.log10(native[mask])
    result.loc[mask, "log_lbol_err_plus"] = np.log10((native[mask] + plus[mask]) / native[mask])
    result.loc[mask, "log_lbol_err_minus"] = np.log10(native[mask] / (native[mask] - minus[mask]))
    return result


def validate_source_raw(raw: pd.DataFrame, source_key: str) -> pd.DataFrame:
    """Validate exact row-level publication values and source-wide anchors."""
    if source_key not in SOURCE_CONFIG:
        raise ValueError(f"Unsupported v4 source: {source_key}")
    required = {
        "measurement_id", "object_id", "published_ra", "published_dec", "ra_deg", "dec_deg",
        "redshift", "field", "survey", "program", "halpha_lum_broad_1e42",
        "halpha_broad_fwhm_km_s", "log_mbh_msun", "log_mbh_err_plus", "log_mbh_err_minus",
        "lrd_flag", "lrd_definition", "halpha_absorption_fit_flag", "source_caveat_tags",
    }
    _require_columns(raw, required, f"{source_key} raw table")
    result = raw.copy()
    expected_rows = SOURCE_CONFIG[source_key]["rows"]
    if len(result) != expected_rows:
        raise ValueError(f"{source_key} must contain {expected_rows} rows, found {len(result)}")
    if not result["measurement_id"].is_unique or not result["object_id"].is_unique:
        raise ValueError(f"{source_key} identifiers must be unique")
    for field in ["ra_deg", "dec_deg", "redshift", "halpha_lum_broad_1e42", "halpha_broad_fwhm_km_s", "log_mbh_msun", "log_mbh_err_plus", "log_mbh_err_minus", "lrd_flag", "halpha_absorption_fit_flag"]:
        result[field] = pd.to_numeric(result[field], errors="raise")
    if not result["redshift"].ge(4.0).all():
        raise ValueError(f"{source_key} contains a source below z=4")
    if not result["halpha_broad_fwhm_km_s"].gt(1000.0).all():
        raise ValueError(f"{source_key} violates its broad-line threshold")
    if not result["lrd_flag"].eq(1).all():
        raise ValueError(f"{source_key} LRD sample label must be preserved independently of class")
    expected_absorption = 2 if source_key == MATTHEE_SOURCE_KEY else 3
    if int(result["halpha_absorption_fit_flag"].sum()) != expected_absorption:
        raise ValueError(f"{source_key} absorption-fit count must be {expected_absorption}")
    return result


def standardize_source(raw: pd.DataFrame, source_key: str) -> pd.DataFrame:
    """Map one source-native extraction into the common v4 measurement schema."""
    config = SOURCE_CONFIG[source_key]
    validated = _native_lbol_to_log(validate_source_raw(raw, source_key))
    validated["published_ra"] = validated["published_ra"].astype("string")
    validated["published_dec"] = validated["published_dec"].astype("string")
    canonical = pd.DataFrame(index=validated.index, columns=CANONICAL_RAW_FIELDS)
    for field in ["measurement_id", "object_id", "ra_deg", "dec_deg", "redshift", "survey", "log_mbh_msun", "log_mbh_err_plus", "log_mbh_err_minus", "log_lbol_erg_s", "log_lbol_err_plus", "log_lbol_err_minus"]:
        canonical[field] = validated[field]
    canonical["redshift_kind"] = "spec"
    canonical["object_class"] = "broad-line-agn"
    canonical["mbh_method"] = MASS_METHOD
    canonical["detection_evidence"] = "individual_robust"
    canonical["lbol_method"] = config["lbol_method"]
    canonical["source_key"] = source_key
    canonical["source_table"] = config["source_table"]
    canonical["notes"] = "Nominal source-table Halpha mass and luminosity are not dust corrected; formal MBH errors exclude the 0.5 dex estimator systematic."
    standardized = standardize_dataframe(
        canonical,
        project_version="v4",
        mbh_tag=MASS_METHOD,
        lbol_tag=config["lbol_method"],
        min_redshift=4.0,
    )
    extras = validated.copy()
    extras["selection_channel"] = "broad-halpha"
    extras["broad_line_species"] = "Halpha"
    extras["log_mbh_systematic_dex"] = 0.5
    extras["mbh_systematic_kind"] = "Reines et al. (2013) Halpha single-epoch estimator intrinsic/calibration uncertainty"
    extras["mbh_systematic_applied_flag"] = False
    extras["mbh_formal_uncertainty_kind"] = "source-table statistical line-fit propagation"
    extras["dust_correction_applied_flag"] = False
    extras["source_paper_version"] = config["paper_version"]
    extras["source_url"] = config["url"]
    extras["source_doi"] = config["doi"]
    extras["source_archive_url"] = config["archive_url"]
    extras["source_archive_sha256"] = config["archive_sha256"]
    extras["extraction_date"] = "2026-08-22"
    extras["selection_criteria"] = config["selection"]
    keep = ["measurement_id", *SOURCE_EXTRA_FIELDS]
    result = standardized.merge(extras[keep], on="measurement_id", validate="one_to_one")
    # Derived comparison value is kept separate from the unpublished reported ratio.
    result["edd_ratio_from_mbh_lbol"] = np.power(
        10.0,
        result["log_lbol_erg_s_std"] - result["log_mbh_msun_std"] - LOG10_EDDINGTON_LUMINOSITY_PER_MSUN,
    )
    return result


def build_v4_catalogues(
    v3_measurements: pd.DataFrame,
    matthee_raw: pd.DataFrame,
    aspire_raw: pd.DataFrame,
    identity_overrides: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return v4 measurements, objects, links, aliases, and match candidates."""
    _require_columns(v3_measurements, ["measurement_id", "physical_object_id", "preferred_measurement_flag"], "v3 measurements")
    matthee = standardize_source(matthee_raw, MATTHEE_SOURCE_KEY)
    aspire = standardize_source(aspire_raw, ASPIRE_SOURCE_KEY)
    new = pd.concat([matthee, aspire], ignore_index=True, sort=False)

    prior_candidates = candidate_matches(new, v3_measurements)
    same_release_candidates = cross_source_candidate_matches(new)
    candidate_frames = [frame for frame in [prior_candidates, same_release_candidates] if not frame.empty]
    candidates = pd.concat(candidate_frames, ignore_index=True) if candidate_frames else prior_candidates.copy()
    require_unambiguous_candidates(prior_candidates, new["measurement_id"])
    candidates, accepted_map = apply_reviewed_identity_overrides(candidates, identity_overrides)
    expected = candidates[candidates["measurement_id"].eq("GOODSS13971_matthee23")]
    if len(candidates) != 1 or len(expected) != 1 or accepted_map.get("GOODSS13971_matthee23") != "HZA-GS-204851":
        raise ValueError("The sole verified new cross-paper match must be GOODS-S-13971 = GS-204851")

    inherited_link_columns = ["measurement_id", "physical_object_id", "preferred_measurement_flag", "preferred_measurement_reason", "match_method", "match_reference"]
    inherited = v3_measurements[inherited_link_columns].copy()
    link_rows: list[dict[str, object]] = []
    for _, row in new.iterrows():
        measurement_id = str(row["measurement_id"])
        if measurement_id in accepted_map:
            physical_id = accepted_map[measurement_id]
            preferred = False
            reason = "prior-release preferred measurement retained for longitudinal reproducibility"
            method = "coordinate-redshift match; manually reviewed"
            reference = "0.5 arcsec and delta-z 0.01 candidate thresholds"
        else:
            physical_id = stable_object_id(str(row["object_id"]))
            preferred = True
            reason = "only catalogue measurement in this release"
            method = "singleton assignment after coordinate-redshift search"
            reference = "no candidate within 0.5 arcsec and delta-z 0.01"
        link_rows.append({"measurement_id": measurement_id, "physical_object_id": physical_id, "preferred_measurement_flag": preferred, "preferred_measurement_reason": reason, "match_method": method, "match_reference": reference})
    links = pd.concat([inherited, pd.DataFrame(link_rows)], ignore_index=True)

    release_columns = list(dict.fromkeys([*v3_measurements.columns, *new.columns]))
    # Building from records avoids pandas' deprecated dtype inference for
    # columns that are entirely missing in one source family while preserving
    # the explicit union-column order.
    measurements = pd.DataFrame.from_records(
        [
            *v3_measurements.reindex(columns=release_columns).to_dict("records"),
            *new.reindex(columns=release_columns).to_dict("records"),
        ],
        columns=release_columns,
    )
    measurements = measurements.drop(columns=[c for c in inherited_link_columns[1:] if c in measurements], errors="ignore")
    measurements = measurements.merge(links, on="measurement_id", validate="one_to_one")
    measurements["catalogue_release"] = CATALOGUE_RELEASE
    if not measurements["measurement_id"].is_unique:
        raise ValueError("v4 measurement IDs must be unique")
    preferred_counts = measurements.groupby("physical_object_id")["preferred_measurement_flag"].sum()
    if not preferred_counts.eq(1).all():
        raise ValueError("Every v4 physical object must have exactly one preferred measurement")

    grouped = measurements.groupby("physical_object_id", sort=False)
    aggregates = grouped.agg(
        n_measurements=("measurement_id", "size"),
        available_measurement_ids=("measurement_id", lambda values: ";".join(values.astype(str))),
        available_object_ids=("object_id", lambda values: ";".join(values.astype(str))),
        lrd_reported_by_any_measurement=("lrd_flag", lambda values: any(pd.notna(v) and bool(v) for v in values)),
    ).reset_index()
    lrd_evidence = (
        measurements[measurements["lrd_flag"].fillna(False).astype(bool)]
        .groupby("physical_object_id")["measurement_id"]
        .agg(lambda values: ";".join(values.astype(str)))
    )
    lrd_source_evidence = (
        measurements[measurements["lrd_flag"].fillna(False).astype(bool)]
        .groupby("physical_object_id")["source_key"]
        .agg(lambda values: ";".join(dict.fromkeys(values.astype(str))))
    )
    aggregates["lrd_evidence_measurement_ids"] = aggregates["physical_object_id"].map(lrd_evidence)
    aggregates["lrd_evidence_source_keys"] = aggregates["physical_object_id"].map(lrd_source_evidence)
    objects = measurements[measurements["preferred_measurement_flag"]].copy()
    objects["preferred_measurement_lrd_flag"] = objects["lrd_flag"]
    objects = objects.merge(aggregates, on="physical_object_id", validate="one_to_one")
    objects["lrd_flag"] = objects["lrd_reported_by_any_measurement"]

    aliases = measurements[["physical_object_id", "measurement_id", "object_id", "source_key", "ra_deg", "dec_deg", "redshift"]].copy()
    aliases["alias_kind"] = "source_object_id"
    aliases["catalogue_release"] = CATALOGUE_RELEASE
    front = ["catalogue_release", "physical_object_id", "measurement_id", "object_id"]
    measurements = measurements[front + [c for c in measurements if c not in front]]
    objects = objects[front + ["n_measurements", "available_measurement_ids", "available_object_ids"] + [c for c in objects if c not in front and c not in {"n_measurements", "available_measurement_ids", "available_object_ids"}]]
    return (
        measurements.sort_values(["source_key", "redshift", "measurement_id"], ascending=[True, False, True]).reset_index(drop=True),
        objects.sort_values(["source_key", "redshift", "physical_object_id"], ascending=[True, False, True]).reset_index(drop=True),
        links.sort_values("measurement_id").reset_index(drop=True),
        aliases.sort_values(["physical_object_id", "measurement_id"]).reset_index(drop=True),
        candidates.sort_values(["measurement_id", "separation_arcsec"]).reset_index(drop=True),
    )
