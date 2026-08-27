"""Authoritative Shen et al. (2019) GNIRS-50 validation and admission."""

from __future__ import annotations

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


SOURCE_KEY = "shen19_gnirs50"
PAPER_VERSION = "ApJ 873, 35 (2019); arXiv:1809.05584v1"
SOURCE_URL = "https://iopscience.iop.org/article/10.3847/1538-4357/ab03d9"
SOURCE_DOI = "10.3847/1538-4357/ab03d9"
SOURCE_ARCHIVE_URL = "https://arxiv.org/e-print/1809.05584v1"
SOURCE_ARCHIVE_SHA256 = "2b4376dc136873c4b8db0e5016568b9b1d4692042f6bb035e61fa8bd76b980ef"
CDS_TABLE1_URL = "https://cdsarc.cds.unistra.fr/ftp/J/ApJ/873/35/table1.dat"
CDS_TABLE1_SHA256 = "40ed1598d8c6d4d4a4aa580c578742f9e0334c26bb9dd762a9a0375231a7239f"
CDS_TABLE3_URL = "https://cdsarc.cds.unistra.fr/ftp/J/ApJ/873/35/table3.dat"
CDS_TABLE3_SHA256 = "e1eae3266b9ccfc966303c6e389e9c16141678199924a67ab4c786fed3240323"
EXTRACTION_DATE = "2026-08-26"
SELECTION_CRITERIA = (
    "50 optically selected quasars at z>=5.7 observed with Gemini/GNIRS "
    "during semesters 2015B-2017A with simultaneous 0.85-2.5 micron coverage"
)
MGII_METHOD = "single-epoch-virial-mgii-shen2011"
CIV_METHOD = "single-epoch-virial-civ-vestergaard-peterson2006"


def _require_columns(frame: pd.DataFrame, fields: set[str], label: str) -> None:
    if missing := sorted(fields - set(frame.columns)):
        raise ValueError(f"{label} missing columns: {missing}")


def validate_shen19_sources(
    sample_table: pd.DataFrame,
    catalog_table: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Validate complete paired CDS tables and documented source anchors."""
    _require_columns(sample_table, {
        "measurement_id", "object_id", "ra_deg", "dec_deg", "systemic_redshift",
        "systemic_redshift_err", "comment",
    }, "Shen et al. Table 1")
    _require_columns(catalog_table, {
        "measurement_id", "object_id", "systemic_redshift", "log_lbol_erg_s",
        "log_mbh_civ_msun", "log_mbh_mgii_msun", "log_mbh_fiducial_msun",
        "log_mbh_fiducial_err", "log_edd_ratio", "log_edd_ratio_err",
    }, "Shen et al. Table 3")
    if len(sample_table) != 50 or not sample_table["measurement_id"].is_unique:
        raise ValueError("Shen et al. Table 1 must contain 50 unique objects")
    if len(catalog_table) != 50 or not catalog_table["measurement_id"].is_unique:
        raise ValueError("Shen et al. Table 3 must contain 50 unique objects")
    sample = sample_table.copy()
    catalog = catalog_table.copy()
    pairs = sample[["measurement_id", "object_id"]].merge(
        catalog[["measurement_id", "object_id"]],
        on=["measurement_id", "object_id"], how="outer", indicator=True,
    )
    if not pairs["_merge"].eq("both").all():
        raise ValueError("Shen et al. Tables 1 and 3 do not pair one-to-one")
    for field in ["ra_deg", "dec_deg", "systemic_redshift", "systemic_redshift_err"]:
        sample[field] = pd.to_numeric(sample[field], errors="raise")
    numeric_fields = [field for field in catalog if field not in {"measurement_id", "object_id"}]
    catalog[numeric_fields] = catalog[numeric_fields].apply(pd.to_numeric, errors="raise")
    if not sample["systemic_redshift"].between(5.63, 6.44).all():
        raise ValueError("Shen et al. systemic-redshift range mismatch")
    if catalog["log_mbh_fiducial_msun"].notna().sum() != 49:
        raise ValueError("Shen et al. must retain 49 fiducial masses and one missing mass")
    if catalog["log_mbh_mgii_msun"].notna().sum() != 29:
        raise ValueError("Shen et al. MgII mass count mismatch")
    missing = catalog.loc[catalog["log_mbh_fiducial_msun"].isna(), "object_id"].tolist()
    if missing != ["J0055+0146"]:
        raise ValueError("Shen et al. missing-mass anchor mismatch")
    comments = sample["comment"].fillna("")
    if comments.str.contains(r"\bBAL\b").sum() != 8:
        raise ValueError("Shen et al. must retain all eight BAL annotations")
    if comments.str.contains("radio-loud").sum() != 4:
        raise ValueError("Shen et al. must retain all four radio-loud annotations")
    if not np.isclose(
        catalog.set_index("object_id").loc["J0002+2550", "log_mbh_fiducial_msun"], 9.6767,
    ):
        raise ValueError("Shen et al. J0002+2550 mass anchor mismatch")
    return sample, catalog


def _stable_token(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").upper()


def build_shen19_admission(sample_table: pd.DataFrame, catalog_table: pd.DataFrame) -> pd.DataFrame:
    """Map all 50 source rows, including the explicitly massless object."""
    sample, catalog = validate_shen19_sources(sample_table, catalog_table)
    raw = sample.merge(
        catalog, on=["measurement_id", "object_id"], suffixes=("_sample", "_catalog"),
        validate="one_to_one",
    )
    has_mgii = raw["log_mbh_mgii_msun"].notna()
    has_mass = raw["log_mbh_fiducial_msun"].notna()
    log_edd = raw["log_edd_ratio"]
    log_edd_err = raw["log_edd_ratio_err"]
    edd = np.power(10.0, log_edd)
    canonical = pd.DataFrame({
        "measurement_id": raw["measurement_id"],
        "object_id": raw["object_id"],
        "ra_deg": raw["ra_deg"],
        "dec_deg": raw["dec_deg"],
        "redshift": raw["systemic_redshift_catalog"],
        "redshift_kind": "broad_uv_line_systemic",
        "survey": "Gemini-GNIRS LLP-7",
        "object_class": "luminous_quasar_comparison",
        # The legacy standardizer requires a numeric mass. The one source row
        # without a mass is cleared from every mass-derived field immediately
        # below, before admission validation or release assembly.
        "log_mbh_msun": raw["log_mbh_fiducial_msun"].fillna(0.0),
        "log_mbh_err_plus": raw["log_mbh_fiducial_err"].fillna(0.0),
        "log_mbh_err_minus": raw["log_mbh_fiducial_err"].fillna(0.0),
        "mbh_method": np.where(has_mgii, MGII_METHOD, CIV_METHOD),
        "detection_evidence": "individual_robust",
        "log_mstar_msun": np.nan,
        "log_mstar_err_plus": np.nan,
        "log_mstar_err_minus": np.nan,
        "mstar_method": "",
        "log_lbol_erg_s": raw["log_lbol_erg_s"],
        "log_lbol_err_plus": raw["log_lbol_err"],
        "log_lbol_err_minus": raw["log_lbol_err"],
        "lbol_method": "l3000_richards2006_bc5p15",
        "edd_ratio_reported": edd,
        "edd_ratio_err_plus": np.power(10.0, log_edd + log_edd_err) - edd,
        "edd_ratio_err_minus": edd - np.power(10.0, log_edd - log_edd_err),
        "agn_contam_flag": np.nan,
        "lensing_mu": np.nan,
        "lensing_mu_err": np.nan,
        "source_key": SOURCE_KEY,
        "source_table": "Shen et al. (2019) CDS Tables 1 and 3",
        "notes": "Published fiducial mass uses MgII when available, otherwise CIV.",
    })
    result = standardize_dataframe(
        canonical, project_version="v7.2", mbh_tag="source_fiducial_uv_virial",
        lbol_tag="l3000_richards2006_bc5p15", min_redshift=5.6,
    )
    no_mass = ~has_mass.to_numpy()
    for field in [
        "log_mbh_msun_std", "log_mbh_err_plus_std", "log_mbh_err_minus_std",
        "log_mbh_mstar_ratio", "log_mbh_mstar_ratio_err", "edd_ratio_from_mbh_lbol",
        "edd_ratio_log_residual_dex",
    ]:
        result.loc[no_mass, field] = np.nan
    result.loc[no_mass, "mbh_method"] = ""
    result.loc[no_mass, "mbh_interpretation_tag"] = "no-published-virial-mass"
    result.loc[no_mass, "edd_ratio_consistency_flag"] = "not_evaluable"

    tokens = raw["object_id"].map(_stable_token)
    result["physical_object_id"] = "HZA-GNIRS50-" + tokens
    result["host_system_id"] = "HZS-GNIRS50-" + tokens
    result["identity_resolution_status"] = "resolved"
    result["source_key"] = SOURCE_KEY
    result["survey"] = "Gemini-GNIRS LLP-7"
    result["field"] = "all_sky_optically_selected_quasar_sample"
    result["source_table"] = "Shen et al. (2019) CDS Tables 1 and 3"
    result["source_paper_version"] = PAPER_VERSION
    result["source_url"] = SOURCE_URL
    result["source_doi"] = SOURCE_DOI
    result["source_archive_url"] = SOURCE_ARCHIVE_URL
    result["source_archive_sha256"] = SOURCE_ARCHIVE_SHA256
    result["cds_table1_url"] = CDS_TABLE1_URL
    result["cds_table1_sha256"] = CDS_TABLE1_SHA256
    result["cds_table3_url"] = CDS_TABLE3_URL
    result["cds_table3_sha256"] = CDS_TABLE3_SHA256
    result["extraction_date"] = EXTRACTION_DATE
    result["extraction_date_status"] = "recorded"
    result["selection_criteria"] = SELECTION_CRITERIA
    comments = raw["comment"].fillna("")
    result["source_caveat_tags"] = comments.map(lambda value: ";".join(filter(None, [
        "broad_absorption_line" if "BAL" in value else "",
        "radio_loud" if "radio-loud" in value else "",
    ])))
    result["evidence_status"] = "secure"
    result["evidence_status_basis"] = "published_gnirs_type1_quasar_spectrum"
    result["spectroscopic_type"] = "type1_broad_line"
    result["selection_channels"] = "luminous_quasar;broad_uv_line"
    result["phenotype_tags"] = ""
    result["lrd_flag"] = np.nan
    result["lensing_status"] = "not_reported"
    result["lensing_mass_correction_status"] = "not_required"
    result["lensing_provenance"] = ""
    result["log_mbh_err_plus"] = raw["log_mbh_fiducial_err"]
    result["log_mbh_err_minus"] = raw["log_mbh_fiducial_err"]
    result["log_mstar_err_plus"] = np.nan
    result["log_mstar_err_minus"] = np.nan
    result["log_lbol_err_plus"] = raw["log_lbol_err"]
    result["log_lbol_err_minus"] = raw["log_lbol_err"]
    result["mbh_statistical_uncertainty_kind"] = np.where(
        has_mass, "published_monte_carlo_spectral_fit_measurement_error", "",
    )
    result["log_mbh_systematic_dex"] = np.where(has_mass, 0.4, np.nan)
    result["mbh_systematic_kind"] = np.where(
        has_mass, "source_stated_single_epoch_virial_systematic", "",
    )
    result["mbh_systematic_applied_flag"] = False
    result["mass_comparability_group"] = np.where(
        has_mass, "virial_uv_single_epoch", "no_numeric_mass",
    )
    result["conditional_mass_flag"] = False
    result["conditional_mass_reason"] = ""
    result["primary_mass_comparison_flag"] = has_mgii
    result["primary_mass_comparison_reason"] = np.select(
        [has_mgii, has_mass],
        ["mgii_luminous_quasar_comparison_stratum", "civ_only_excluded_from_primary_comparison"],
        default="no_published_virial_mass",
    )
    result["log_mstar_upper_limit_msun"] = np.nan
    result["host_property_scope"] = "not_published"
    growth_reasons = result.apply(expected_growth_eligibility_reason, axis=1)
    growth_flags = growth_reasons.eq(GROWTH_ELIGIBLE_REASON)
    primary_reasons = result.apply(
        lambda row: expected_primary_eligibility_reason(row, bool(growth_flags.loc[row.name])), axis=1,
    )
    result["growth_ranking_eligible_flag"] = growth_flags
    result["growth_ranking_eligibility_reason"] = growth_reasons
    result["primary_growth_ranking_flag"] = primary_reasons.eq(PRIMARY_ELIGIBLE_REASON)
    result["primary_growth_ranking_reason"] = primary_reasons
    result["preferred_measurement_flag"] = True
    result["preferred_measurement_reason"] = "only atlas measurement pending reviewed identity merge"
    result["match_method"] = "singleton assignment pending coordinate-redshift review"
    result["match_reference"] = "v7.1 coordinate-redshift candidate search"
    result["host_system_assignment_status"] = "source_verified_single_quasar_host"
    result["published_aliases"] = raw["object_id"]
    result["bal_flag"] = comments.str.contains(r"\bBAL\b")
    result["radio_loud_flag"] = comments.str.contains("radio-loud")
    result["fiducial_mass_line"] = np.select([has_mgii, has_mass], ["MgII", "CIV"], default="none")
    validate_v7_admission(result)
    return result


OBSERVABLES = {
    "log_l1350_erg_s": ("log_lambda_l1350", "log10(erg/s)", "log_l1350_err"),
    "log_l1700_erg_s": ("log_lambda_l1700", "log10(erg/s)", "log_l1700_err"),
    "log_l3000_erg_s": ("log_lambda_l3000", "log10(erg/s)", "log_l3000_err"),
    "mgii_fwhm_km_s": ("fwhm_mgii", "km/s", "mgii_fwhm_km_s_err"),
    "mgii_ew_angstrom": ("ew_mgii", "angstrom", "mgii_ew_angstrom_err"),
    "ciii_fwhm_km_s": ("fwhm_ciii_complex", "km/s", "ciii_fwhm_km_s_err"),
    "ciii_ew_angstrom": ("ew_ciii_complex", "angstrom", "ciii_ew_angstrom_err"),
    "civ_fwhm_km_s": ("fwhm_civ", "km/s", "civ_fwhm_km_s_err"),
    "civ_ew_angstrom": ("ew_civ", "angstrom", "civ_ew_angstrom_err"),
    "siiv_fwhm_km_s": ("fwhm_siiv_oiv_complex", "km/s", "siiv_fwhm_km_s_err"),
    "siiv_ew_angstrom": ("ew_siiv_oiv_complex", "angstrom", "siiv_ew_angstrom_err"),
    "log_mbh_civ_msun": ("log_mbh_civ", "log10(Msun)", "log_mbh_civ_err"),
    "log_mbh_mgii_msun": ("log_mbh_mgii", "log10(Msun)", "log_mbh_mgii_err"),
    "log_edd_ratio": ("log_edd_ratio", "log10(dimensionless)", "log_edd_ratio_err"),
}


def build_shen19_observables(catalog_table: pd.DataFrame) -> pd.DataFrame:
    """Retain every available supporting luminosity, line, and alternate mass."""
    rows = []
    for _, source in catalog_table.iterrows():
        for field, (name, unit, error_field) in OBSERVABLES.items():
            if pd.isna(source[field]):
                continue
            error = source[error_field]
            rows.append({
                "observable_id": f"{source['measurement_id']}__{name}",
                "measurement_id": source["measurement_id"],
                "observable_name": name,
                "value": source[field],
                "err_plus": error,
                "err_minus": error,
                "censoring": "detection",
                "unit": unit,
                "uncertainty_kind": (
                    "published_monte_carlo_spectral_fit_measurement_error"
                    if pd.notna(error) else "not_published"
                ),
                "source_location": "Shen et al. (2019) CDS Table 3",
            })
    result = pd.DataFrame(rows)
    validate_v7_observables(result, catalog_table["measurement_id"])
    return result
