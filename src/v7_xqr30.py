"""Authoritative XQR-30 extraction validation and v7.1 admission mapping."""

from __future__ import annotations

from collections.abc import Iterable
import re

import numpy as np
import pandas as pd

from src.standardize_data import standardize_dataframe
from src.v7_admission import (
    GROWTH_ELIGIBLE_REASON,
    PRIMARY_ELIGIBLE_REASON,
    expected_growth_eligibility_reason,
    expected_primary_eligibility_reason,
    validate_v7_admission,
    validate_v7_observables,
)


SOURCE_KEY = "xqr30_mazzucchelli23"
MASS_METHOD = "single-epoch-virial-mgii-vestergaard-osmer2009"
PAPER_VERSION = "A&A 676, A71 (2023); arXiv:2306.16474v1"
SOURCE_URL = "https://www.aanda.org/articles/aa/full_html/2023/08/aa46317-23/aa46317-23.html"
SOURCE_DOI = "10.1051/0004-6361/202346317"
SOURCE_ARCHIVE_URL = "https://arxiv.org/e-print/2306.16474v1"
SOURCE_ARCHIVE_SHA256 = "412055cec92c368f711605822d806c949816695a451efee867904d2171fee53f"
COORDINATE_PAPER_VERSION = "MNRAS 523, 1399-1420 (2023); arXiv:2305.05053v1"
COORDINATE_SOURCE_URL = "https://academic.oup.com/mnras/article/523/1/1399/7161136"
COORDINATE_ARCHIVE_URL = "https://arxiv.org/e-print/2305.05053v1"
COORDINATE_ARCHIVE_SHA256 = "1cf315f5fd4cd9f0edebb840c254dcd6bee26e2a061ce9fc9ff5bc8f344d7c42"
EXTRACTION_DATE = "2026-08-26"
SELECTION_CRITERIA = (
    "E-XQR-30: 30 XQR-30 quasars selected at declination<+27 degrees, z>=5.8, "
    "J_AB<=19.8 below z=6.0 or <=20.0 at z>=6.0, without prior deep XSHOOTER "
    "spectra, plus 12 archival XSHOOTER quasars of comparable quality"
)
LENSING_MU = 51.3
LENSING_REFERENCE = (
    "Fan et al. (2019), ApJ 870 L11, DOI 10.3847/2041-8213/aaeffe; "
    "point-source magnification approximately 50 (51.3 adopted in Yang et al. 2022)"
)

TABLE_NUMERIC_FIELDS = [
    "redshift", "fwhm_civ_km_s", "fwhm_civ_km_s_err_plus",
    "fwhm_civ_km_s_err_minus", "fwhm_mgii_km_s",
    "fwhm_mgii_km_s_err_plus", "fwhm_mgii_km_s_err_minus",
    "civ_blueshift_km_s", "civ_blueshift_km_s_err_plus",
    "civ_blueshift_km_s_err_minus", "log_l1350_erg_s",
    "log_l1350_erg_s_err_plus", "log_l1350_erg_s_err_minus",
    "log_l3000_erg_s", "log_l3000_erg_s_err_plus",
    "log_l3000_erg_s_err_minus", "log_lbol_erg_s",
    "log_lbol_erg_s_err_plus", "log_lbol_erg_s_err_minus",
    "log_mbh_civ_msun", "log_mbh_civ_msun_err_plus",
    "log_mbh_civ_msun_err_minus", "log_mbh_mgii_msun",
    "log_mbh_mgii_msun_err_plus", "log_mbh_mgii_msun_err_minus",
    "edd_ratio_civ", "edd_ratio_civ_err_plus", "edd_ratio_civ_err_minus",
    "edd_ratio_mgii", "edd_ratio_mgii_err_plus", "edd_ratio_mgii_err_minus",
]
FLAG_FIELDS = [
    "redshift_from_cii_flag", "bal_flag", "mgii_telluric_caveat_flag",
    "civ_low_snr_caveat_flag", "lensed_flag",
]


def _require_columns(frame: pd.DataFrame, fields: Iterable[str], label: str) -> None:
    if missing := sorted(set(fields) - set(frame.columns)):
        raise ValueError(f"{label} missing columns: {missing}")


def _strict_bool_series(series: pd.Series, field: str) -> pd.Series:
    values = series.map(
        lambda value: value if isinstance(value, (bool, np.bool_)) else
        str(value).strip().lower() == "true" if str(value).strip().lower() in {"true", "false"}
        else np.nan
    )
    if values.isna().any():
        raise ValueError(f"XQR-30 {field} must contain explicit booleans")
    return values.astype(bool)


def validate_xqr30_sources(
    raw_table: pd.DataFrame,
    coordinates: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Validate all 42 table rows, paired coordinate rows, and source anchors."""
    _require_columns(
        raw_table,
        {"measurement_id", "object_id", "table_alias", *TABLE_NUMERIC_FIELDS, *FLAG_FIELDS},
        "XQR-30 Mazzucchelli Table 1",
    )
    _require_columns(
        coordinates,
        {"measurement_id", "object_id", "ra_hms", "dec_dms", "ra_deg", "dec_deg"},
        "XQR-30 D'Odorico coordinate table",
    )
    if len(raw_table) != 42 or not raw_table["measurement_id"].is_unique:
        raise ValueError("XQR-30 mass table must contain 42 unique measurements")
    if len(coordinates) != 42 or not coordinates["measurement_id"].is_unique:
        raise ValueError("XQR-30 coordinate table must contain 42 unique measurements")
    table = raw_table.copy()
    coords = coordinates.copy()
    for field in TABLE_NUMERIC_FIELDS:
        table[field] = pd.to_numeric(table[field], errors="raise")
    for field in ["ra_deg", "dec_deg"]:
        coords[field] = pd.to_numeric(coords[field], errors="raise")
    for field in FLAG_FIELDS:
        table[field] = _strict_bool_series(table[field], field)
    pairs = table[["measurement_id", "object_id"]].merge(
        coords[["measurement_id", "object_id"]],
        on=["measurement_id", "object_id"], how="outer", indicator=True,
    )
    if not pairs["_merge"].eq("both").all():
        raise ValueError("XQR-30 mass and coordinate tables do not pair one-to-one")
    if not table["redshift"].between(5.77, 6.64).all():
        raise ValueError("XQR-30 redshift range mismatch")
    if int(table["mgii_telluric_caveat_flag"].sum()) != 7:
        raise ValueError("XQR-30 must preserve all seven MgII telluric caveats")
    if table.loc[table["civ_low_snr_caveat_flag"], "object_id"].tolist() != ["PSO J065+01"]:
        raise ValueError("XQR-30 CIV low-S/N caveat anchor mismatch")
    if table.loc[table["lensed_flag"], "object_id"].tolist() != ["WISEA J0439+1634"]:
        raise ValueError("XQR-30 lensed-quasar anchor mismatch")
    anchors = table.set_index("object_id")
    if not np.isclose(anchors.loc["PSO J007+04", "log_mbh_mgii_msun"], 9.89):
        raise ValueError("XQR-30 PSO J007+04 MgII mass anchor mismatch")
    if not np.isclose(anchors.loc["SDSS J0100+2802", "log_mbh_mgii_msun"], 10.1):
        raise ValueError("XQR-30 J0100+2802 MgII mass anchor mismatch")
    coord_anchor = coords.set_index("object_id").loc["WISEA J0439+1634"]
    if not np.isclose(coord_anchor["ra_deg"], 69.9461666667, atol=1e-9):
        raise ValueError("XQR-30 J0439+1634 coordinate anchor mismatch")
    return table, coords


def _stable_token(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").upper()


def build_xqr30_admission(
    raw_table: pd.DataFrame,
    coordinates: pd.DataFrame,
) -> pd.DataFrame:
    """Map the complete XQR-30 table to canonical MgII measurement rows."""
    raw, coords = validate_xqr30_sources(raw_table, coordinates)
    raw = raw.merge(coords, on=["measurement_id", "object_id"], validate="one_to_one")
    canonical = pd.DataFrame(index=raw.index)
    canonical["measurement_id"] = raw["measurement_id"]
    canonical["object_id"] = raw["object_id"]
    canonical["ra_deg"] = raw["ra_deg"]
    canonical["dec_deg"] = raw["dec_deg"]
    canonical["redshift"] = raw["redshift"]
    canonical["redshift_kind"] = np.where(
        raw["redshift_from_cii_flag"], "far_ir_cii_spectroscopic", "mgii_spectroscopic",
    )
    canonical["survey"] = "E-XQR-30"
    canonical["object_class"] = "luminous_quasar_comparison"
    canonical["log_mbh_msun"] = raw["log_mbh_mgii_msun"]
    canonical["log_mbh_err_plus"] = raw["log_mbh_mgii_msun_err_plus"]
    canonical["log_mbh_err_minus"] = raw["log_mbh_mgii_msun_err_minus"]
    canonical["mbh_method"] = MASS_METHOD
    canonical["detection_evidence"] = "individual_robust"
    canonical["log_mstar_msun"] = np.nan
    canonical["log_mstar_err_plus"] = np.nan
    canonical["log_mstar_err_minus"] = np.nan
    canonical["mstar_method"] = ""
    canonical["log_lbol_erg_s"] = raw["log_lbol_erg_s"]
    canonical["log_lbol_err_plus"] = raw["log_lbol_erg_s_err_plus"]
    canonical["log_lbol_err_minus"] = raw["log_lbol_erg_s_err_minus"]
    canonical["lbol_method"] = "l3000_richards2006_bc5p15"
    canonical["edd_ratio_reported"] = raw["edd_ratio_mgii"]
    canonical["edd_ratio_err_plus"] = raw["edd_ratio_mgii_err_plus"]
    canonical["edd_ratio_err_minus"] = raw["edd_ratio_mgii_err_minus"]
    canonical["agn_contam_flag"] = np.nan
    canonical["lensing_mu"] = np.where(raw["lensed_flag"], LENSING_MU, np.nan)
    canonical["lensing_mu_err"] = np.nan
    canonical["source_key"] = SOURCE_KEY
    canonical["source_table"] = "Mazzucchelli et al. (2023) Table 1"
    canonical["notes"] = (
        "Canonical row uses the published MgII virial mass; CIV quantities are retained "
        "as source-local observables; no cross-class science pooling is authorized."
    )
    result = standardize_dataframe(
        canonical,
        project_version="v7.1",
        mbh_tag=MASS_METHOD,
        lbol_tag="l3000_richards2006_bc5p15",
        min_redshift=5.7,
    )
    tokens = raw["object_id"].map(_stable_token)
    result["physical_object_id"] = "HZA-XQR30-" + tokens
    result["host_system_id"] = "HZS-XQR30-" + tokens
    result["identity_resolution_status"] = "resolved"
    result["source_key"] = SOURCE_KEY
    result["survey"] = "E-XQR-30"
    result["field"] = "all_sky_bright_quasar_sample"
    result["source_table"] = "Mazzucchelli et al. (2023) Table 1"
    result["source_paper_version"] = PAPER_VERSION
    result["source_url"] = SOURCE_URL
    result["source_doi"] = SOURCE_DOI
    result["source_archive_url"] = SOURCE_ARCHIVE_URL
    result["source_archive_sha256"] = SOURCE_ARCHIVE_SHA256
    result["coordinate_source_table"] = "D'Odorico et al. (2023) Table 1"
    result["coordinate_source_paper_version"] = COORDINATE_PAPER_VERSION
    result["coordinate_source_url"] = COORDINATE_SOURCE_URL
    result["coordinate_source_archive_url"] = COORDINATE_ARCHIVE_URL
    result["coordinate_source_archive_sha256"] = COORDINATE_ARCHIVE_SHA256
    result["extraction_date"] = EXTRACTION_DATE
    result["extraction_date_status"] = "recorded"
    result["selection_criteria"] = SELECTION_CRITERIA
    caveats = []
    for _, row in raw.iterrows():
        tags = []
        if row["bal_flag"]:
            tags.append("broad_absorption_line")
        if row["mgii_telluric_caveat_flag"]:
            tags.append("mgii_near_or_within_strong_telluric_absorption")
        if row["civ_low_snr_caveat_flag"]:
            tags.append("civ_region_very_low_snr")
        if row["lensed_flag"]:
            tags.append("published_values_not_corrected_for_lensing_magnification")
        caveats.append(";".join(tags))
    result["source_caveat_tags"] = caveats
    inconsistent = result["edd_ratio_consistency_flag"].eq("inconsistent")
    result.loc[inconsistent, "source_caveat_tags"] = result.loc[
        inconsistent, "source_caveat_tags"
    ].map(lambda value: ";".join(filter(None, [value, "published_mgii_edd_ratio_internal_inconsistency"])))
    result["evidence_status"] = "secure"
    result["evidence_status_basis"] = "published_high_snr_xshooter_type1_quasar_spectrum"
    result["spectroscopic_type"] = "type1_broad_line"
    result["selection_channels"] = "luminous_quasar;broad_uv_line"
    result["phenotype_tags"] = ""
    result["lrd_flag"] = np.nan
    result["lensing_status"] = np.where(raw["lensed_flag"], "lensed", "unlensed")
    result["lensing_mass_correction_status"] = np.where(
        raw["lensed_flag"], "not_applied", "not_required",
    )
    result["lensing_provenance"] = np.where(raw["lensed_flag"], LENSING_REFERENCE, "")
    result["log_mbh_err_plus"] = raw["log_mbh_mgii_msun_err_plus"]
    result["log_mbh_err_minus"] = raw["log_mbh_mgii_msun_err_minus"]
    result["log_mstar_err_plus"] = np.nan
    result["log_mstar_err_minus"] = np.nan
    result["log_lbol_err_plus"] = raw["log_lbol_erg_s_err_plus"]
    result["log_lbol_err_minus"] = raw["log_lbol_erg_s_err_minus"]
    result["mbh_statistical_uncertainty_kind"] = "published_spectral_fit_propagation"
    result["log_mbh_systematic_dex"] = 0.55
    result["mbh_systematic_kind"] = "mgii_single_epoch_scaling_relation_scatter"
    result["mbh_systematic_applied_flag"] = False
    result["mass_comparability_group"] = "virial_uv_single_epoch"
    result["conditional_mass_flag"] = False
    result["conditional_mass_reason"] = ""
    result["primary_mass_comparison_flag"] = True
    result["primary_mass_comparison_reason"] = "mgii_luminous_quasar_comparison_stratum"
    result["log_mstar_upper_limit_msun"] = np.nan
    result["host_property_scope"] = "not_published"
    growth_reasons = result.apply(expected_growth_eligibility_reason, axis=1)
    growth_flags = growth_reasons.eq(GROWTH_ELIGIBLE_REASON)
    primary_reasons = result.apply(
        lambda row: expected_primary_eligibility_reason(
            row, bool(growth_flags.loc[row.name]),
        ),
        axis=1,
    )
    result["growth_ranking_eligible_flag"] = growth_flags
    result["growth_ranking_eligibility_reason"] = growth_reasons
    result["primary_growth_ranking_flag"] = primary_reasons.eq(PRIMARY_ELIGIBLE_REASON)
    result["primary_growth_ranking_reason"] = primary_reasons
    result["preferred_measurement_flag"] = True
    result["preferred_measurement_reason"] = "only atlas measurement for this physical object"
    result["match_method"] = "singleton assignment after coordinate-redshift search"
    result["match_reference"] = "no v7.0 candidate within 0.5 arcsec and delta-z 0.01"
    result["host_system_assignment_status"] = "source_verified_single_quasar_host"
    result["published_aliases"] = raw.apply(
        lambda row: ";".join(dict.fromkeys([str(row["object_id"]), str(row["table_alias"])])),
        axis=1,
    )
    result["redshift_from_cii_flag"] = raw["redshift_from_cii_flag"]
    result["bal_flag"] = raw["bal_flag"]
    result["mgii_telluric_caveat_flag"] = raw["mgii_telluric_caveat_flag"]
    result["civ_low_snr_caveat_flag"] = raw["civ_low_snr_caveat_flag"]
    validate_v7_admission(result)
    return result


OBSERVABLES = {
    "fwhm_civ_km_s": ("fwhm_civ_reported", "km/s"),
    "fwhm_mgii_km_s": ("fwhm_mgii", "km/s"),
    "civ_blueshift_km_s": ("civ_blueshift", "km/s"),
    "log_l1350_erg_s": ("log_lambda_l1350", "log10(erg/s)"),
    "log_l3000_erg_s": ("log_lambda_l3000", "log10(erg/s)"),
    "log_mbh_civ_msun": ("log_mbh_civ_coatman_corrected", "log10(Msun)"),
    "edd_ratio_civ": ("edd_ratio_civ", "dimensionless"),
}


def build_xqr30_observables(raw_table: pd.DataFrame) -> pd.DataFrame:
    """Return all published alternate CIV and supporting spectral observables."""
    rows = []
    for _, source in raw_table.iterrows():
        for field, (name, unit) in OBSERVABLES.items():
            rows.append({
                "observable_id": f"{source['measurement_id']}__{name}",
                "measurement_id": source["measurement_id"],
                "observable_name": name,
                "value": source[field],
                "err_plus": source[f"{field}_err_plus"],
                "err_minus": source[f"{field}_err_minus"],
                "censoring": "detection",
                "unit": unit,
                "uncertainty_kind": "published_spectral_fit_propagation",
                "source_location": "Mazzucchelli et al. (2023) Table 1",
            })
    result = pd.DataFrame(rows)
    validate_v7_observables(result, raw_table["measurement_id"])
    if len(result) != 294:
        raise ValueError("XQR-30 must retain seven source-local observables per quasar")
    return result
