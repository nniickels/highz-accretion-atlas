"""Authoritative Ren et al. source extraction and v7 admission mapping.

This module validates the published seven-row Tables 1--2 source layer in
memory.  It deliberately does not build a combined v7 release.
"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

from src.identity import candidate_matches
from src.standardize_data import standardize_dataframe
from src.v7_admission import (
    GROWTH_ELIGIBLE_REASON,
    PRIMARY_ELIGIBLE_REASON,
    validate_v7_admission,
    validate_v7_observables,
)


SOURCE_KEY = "ren25_alpine_cristal_jwst_blagn_candidates"
MASS_METHOD = "single-epoch-virial-halpha-reines2013"
PAPER_VERSION = (
    "MNRAS 544, 211-233 (published 2025-10-25; corrected/typeset 2025-10-28); "
    "arXiv:2509.02027v2"
)
SOURCE_URL = "https://academic.oup.com/mnras/article/544/1/211/8301219"
SOURCE_DOI = "10.1093/mnras/staf1709"
SOURCE_ARCHIVE_URL = "https://arxiv.org/abs/2509.02027v2"
SOURCE_ARCHIVE_SHA256 = "c528c375fda9362433184cb35775a5f4ca107014f4b1c2f6536d7f15d4f85cca"
EXTRACTION_DATE = "2026-08-25"
SELECTION_CRITERIA = (
    "18 main-sequence galaxies with Mstar>10^9.5 Msun at z=4.4-5.7; 33 IFU "
    "photometric-centre apertures; narrow FWHM<600 km/s; added broad Halpha "
    "Gaussian constrained FWHM>600 km/s; DeltaBIC(narrow minus narrow+broad)>10; "
    "broad-flux S/N>3; OIII outflow comparison and broad-to-narrow flux-ratio veto"
)

EXPECTED_OBJECT_IDS = {
    "DC_417567", "DC_519281", "DC_536534", "DC_683613",
    "DC_848185_a", "DC_848185_b", "DC_873321",
}
EXPECTED_OBSERVABLES = {
    "sii6718_6733_flux", "nii6585_flux", "halpha_narrow_flux", "oiii5008_flux",
    "hbeta_narrow_flux", "heii4687_flux", "oiii4364_flux", "hgamma_flux",
    "neiii3870_flux", "oii3727_3730_flux",
}

PHYSICAL_IDS = {
    "DC_417567": "HZA-DC-417567",
    "DC_519281": "HZA-DC-519281",
    "DC_536534": "HZA-DC-536534",
    "DC_683613": "HZA-DC-683613",
    "DC_848185_a": "HZA-DC-848185-A",
    "DC_848185_b": "HZA-DC-848185-B",
    "DC_873321": "HZA-DC-873321",
}
HOST_SYSTEM_IDS = {
    "DC_417567": "HZS-DC-417567",
    "DC_519281": "HZS-DC-519281",
    "DC_536534": "HZS-DC-536534",
    "DC_683613": "HZS-DC-683613",
    "DC_848185_a": "HZS-DC-848185",
    "DC_848185_b": "HZS-DC-848185",
    "DC_873321": "HZS-DC-873321",
}

TABLE1_NUMERIC_FIELDS = [
    "ra_deg", "dec_deg", "redshift", "halpha_broad_flux_dustcorr_1e18",
    "halpha_broad_flux_err", "halpha_broad_fwhm_instrumentcorr_km_s",
    "halpha_broad_fwhm_err", "log_mstar_msun", "log_mstar_err_plus",
    "log_mstar_err_minus", "log_mbh_msun", "log_mbh_err_plus",
    "log_mbh_err_minus", "log_lbol_erg_s", "log_lbol_err_plus",
    "log_lbol_err_minus", "log_edd_ratio", "ebv_mag", "av_mag",
    "robust_candidate_flag", "oiii_outflow_detected_flag",
    "halpha_three_component_fit_flag", "mass_conditional_on_blr_flag",
]


def _require_columns(frame: pd.DataFrame, fields: Iterable[str], label: str) -> None:
    if missing := sorted(set(fields) - set(frame.columns)):
        raise ValueError(f"{label} missing columns: {missing}")


def validate_ren_table1(raw: pd.DataFrame) -> pd.DataFrame:
    """Validate every published Table 1 row and explicit narrative annotation."""
    required = {
        "measurement_id", "object_id", "host_system_source_id", "published_aliases",
        "lrd_flag", "source_caveat_tags", *TABLE1_NUMERIC_FIELDS,
    }
    _require_columns(raw, required, "Ren Table 1")
    if len(raw) != 7 or not raw["measurement_id"].is_unique:
        raise ValueError("Ren Table 1 must contain seven unique measurement rows")
    if set(raw["object_id"]) != EXPECTED_OBJECT_IDS:
        raise ValueError("Ren Table 1 object set mismatch")
    result = raw.copy()
    for field in TABLE1_NUMERIC_FIELDS:
        original = result[field]
        result[field] = pd.to_numeric(original, errors="coerce")
        invalid = result[field].isna() & original.notna() & original.astype(str).str.strip().ne("")
        if invalid.any():
            raise ValueError(f"Ren Table 1 field {field} contains nonnumeric values")
    if result[TABLE1_NUMERIC_FIELDS].isna().any().any():
        raise ValueError("Published Ren Table 1 numeric values cannot be missing")
    if not result["redshift"].between(5.1542, 5.6886).all():
        raise ValueError("Ren Table 1 redshift range mismatch")
    if result["lrd_flag"].notna().any():
        raise ValueError("Ren et al. do not publish row-level LRD classifications")
    bool_fields = [
        "robust_candidate_flag", "oiii_outflow_detected_flag",
        "halpha_three_component_fit_flag", "mass_conditional_on_blr_flag",
    ]
    for field in bool_fields:
        if not result[field].isin([0, 1]).all():
            raise ValueError(f"{field} must contain only 0/1")
    indexed = result.set_index("object_id")
    if set(indexed.index[indexed["robust_candidate_flag"].eq(1)]) != {"DC_536534"}:
        raise ValueError("DC_536534 must be the sole source-designated robust candidate")
    if set(indexed.index[indexed["halpha_three_component_fit_flag"].eq(1)]) != {"DC_536534"}:
        raise ValueError("DC_536534 must be the sole stable three-component Halpha fit")
    expected_outflows = {"DC_519281", "DC_536534", "DC_873321"}
    if set(indexed.index[indexed["oiii_outflow_detected_flag"].eq(1)]) != expected_outflows:
        raise ValueError("Ren object-level OIII outflow annotation mismatch")
    if set(indexed.index[indexed["mass_conditional_on_blr_flag"].eq(0)]) != {"DC_536534"}:
        raise ValueError("Only the robust candidate may have an unconditional BLR mass mapping")
    pair = result[result["host_system_source_id"].eq("DC_848185")]
    if set(pair["object_id"]) != {"DC_848185_a", "DC_848185_b"}:
        raise ValueError("DC_848185 must contain the published a/b candidate nuclei")
    if not pair["log_mstar_msun"].eq(10.37).all():
        raise ValueError("DC_848185 shared integrated host-mass anchor mismatch")
    if not np.isclose(indexed.loc["DC_536534", "log_mbh_msun"], 7.78):
        raise ValueError("DC_536534 mass anchor mismatch")
    if not np.isclose(indexed.loc["DC_417567", "halpha_broad_fwhm_instrumentcorr_km_s"], 596):
        raise ValueError("DC_417567 FWHM anchor mismatch")
    implied_log_edd = result["log_lbol_erg_s"] - (np.log10(1.26e38) + result["log_mbh_msun"])
    if not np.allclose(implied_log_edd, result["log_edd_ratio"], atol=0.015):
        raise ValueError("Published Ren Lbol, MBH, and Eddington ratios are inconsistent")
    return result


def validate_ren_table2(
    raw: pd.DataFrame,
    measurement_object_map: pd.DataFrame,
) -> pd.DataFrame:
    """Validate all 70 published Table 2 line entries and 3-sigma limits."""
    _require_columns(
        measurement_object_map, {"measurement_id", "object_id"},
        "Ren Table 1 measurement/object map",
    )
    if measurement_object_map[["measurement_id", "object_id"]].duplicated().any():
        raise ValueError("Ren Table 1 measurement/object map must contain unique pairs")
    expected_pairs = set(map(
        tuple,
        measurement_object_map[["measurement_id", "object_id"]].astype(str).to_numpy(),
    ))
    if len(expected_pairs) != 7:
        raise ValueError("Ren Table 1 measurement/object map must contain seven pairs")
    result = raw.copy()
    validate_v7_observables(result, measurement_object_map["measurement_id"])
    if len(result) != 70 or not result["observable_id"].is_unique:
        raise ValueError("Ren Table 2 must contain 70 unique line-observable rows")
    if set(result["object_id"]) != EXPECTED_OBJECT_IDS:
        raise ValueError("Ren Table 2 object set mismatch")
    if set(result["observable_name"]) != EXPECTED_OBSERVABLES:
        raise ValueError("Ren Table 2 observable set mismatch")
    actual_pairs = set(map(
        tuple, result[["measurement_id", "object_id"]].astype(str).to_numpy(),
    ))
    if actual_pairs != expected_pairs:
        raise ValueError("Ren Table 2 measurement/object mapping does not match Table 1")
    counts = result.groupby(["measurement_id", "object_id"])["observable_name"].nunique()
    if len(counts) != 7 or not counts.eq(10).all():
        raise ValueError("Every Ren Table 2 measurement/object pair must have ten line entries")
    for pair, group in result.groupby(["measurement_id", "object_id"]):
        if set(group["observable_name"]) != EXPECTED_OBSERVABLES:
            raise ValueError(f"Ren Table 2 observable set mismatch for {pair}")
    if int(result["censoring"].eq("upper_limit").sum()) != 12:
        raise ValueError("Ren Table 2 must preserve twelve published 3-sigma upper limits")
    robust_heii = result[result["observable_id"].eq("DC536534_heii4687")].iloc[0]
    if robust_heii["censoring"] != "detection" or not np.isclose(robust_heii["value"], 0.18):
        raise ValueError("DC_536534 HeII Table 2 anchor mismatch")
    return result


def build_ren_admission(raw_table1: pd.DataFrame) -> pd.DataFrame:
    """Map the complete Table 1 source layer into the v7 admission contract."""
    raw = validate_ren_table1(raw_table1)
    robust = raw["robust_candidate_flag"].astype(bool)
    canonical = pd.DataFrame(index=raw.index)
    canonical["measurement_id"] = raw["measurement_id"]
    canonical["object_id"] = raw["object_id"]
    canonical["ra_deg"] = raw["ra_deg"]
    canonical["dec_deg"] = raw["dec_deg"]
    canonical["redshift"] = raw["redshift"]
    canonical["redshift_kind"] = "far_ir_cii_spectroscopic"
    canonical["survey"] = "ALPINE-CRISTAL-JWST"
    canonical["object_class"] = "broad_line_agn"
    canonical["log_mbh_msun"] = raw["log_mbh_msun"]
    canonical["log_mbh_err_plus"] = raw["log_mbh_err_plus"]
    canonical["log_mbh_err_minus"] = raw["log_mbh_err_minus"]
    canonical["mbh_method"] = MASS_METHOD
    canonical["detection_evidence"] = np.where(
        robust, "individual_robust", "individual_tentative",
    )
    canonical["log_mstar_msun"] = raw["log_mstar_msun"]
    canonical["log_mstar_err_plus"] = raw["log_mstar_err_plus"]
    canonical["log_mstar_err_minus"] = raw["log_mstar_err_minus"]
    canonical["mstar_method"] = "faisst2020_integrated_pre_jwst_broadband_sed"
    canonical["log_lbol_erg_s"] = raw["log_lbol_erg_s"]
    canonical["log_lbol_err_plus"] = raw["log_lbol_err_plus"]
    canonical["log_lbol_err_minus"] = raw["log_lbol_err_minus"]
    canonical["lbol_method"] = "broad_halpha_to_l5100_greeneho2005_bc5100_9p26"
    canonical["edd_ratio_reported"] = np.power(10.0, raw["log_edd_ratio"])
    canonical["edd_ratio_err_plus"] = np.nan
    canonical["edd_ratio_err_minus"] = np.nan
    canonical["agn_contam_flag"] = np.nan
    canonical["lensing_mu"] = np.nan
    canonical["lensing_mu_err"] = np.nan
    canonical["source_key"] = SOURCE_KEY
    canonical["source_table"] = "Published Table 1"
    canonical["notes"] = (
        "Host-selected broad-Halpha candidate; primary eligibility is controlled "
        "separately by the v7 evidence and conditional-mass fields."
    )
    result = standardize_dataframe(
        canonical,
        project_version="v7",
        mbh_tag=MASS_METHOD,
        lbol_tag="broad_halpha_to_l5100_greeneho2005_bc5100_9p26",
        min_redshift=4.0,
    )
    result["physical_object_id"] = raw["object_id"].map(PHYSICAL_IDS)
    result["host_system_id"] = raw["object_id"].map(HOST_SYSTEM_IDS)
    result["identity_resolution_status"] = "resolved"
    result["source_key"] = SOURCE_KEY
    result["survey"] = "ALPINE-CRISTAL-JWST"
    result["field"] = "COSMOS"
    result["source_table"] = "Published Table 1"
    result["source_paper_version"] = PAPER_VERSION
    result["source_url"] = SOURCE_URL
    result["source_doi"] = SOURCE_DOI
    result["source_archive_url"] = SOURCE_ARCHIVE_URL
    result["source_archive_sha256"] = SOURCE_ARCHIVE_SHA256
    result["extraction_date"] = EXTRACTION_DATE
    result["selection_criteria"] = SELECTION_CRITERIA
    result["source_caveat_tags"] = raw["source_caveat_tags"]
    result["evidence_status"] = np.where(robust, "probable", "candidate")
    result["evidence_status_basis"] = np.where(
        robust,
        "source_most_robust_candidate_with_spatially_compact_blr_and_separate_outflow",
        "source_type1_candidate_with_intermediate_width_halpha_and_outflow_ambiguity",
    )
    result["spectroscopic_type"] = "type1_broad_line_candidate"
    result["selection_channels"] = "host_selected;broad_halpha"
    dual = raw["host_system_source_id"].eq("DC_848185")
    result["phenotype_tags"] = np.where(dual, "merger;dual_nucleus", "merger")
    result["lrd_flag"] = np.nan
    result["lensing_status"] = "not_reported"
    result["lensing_mu"] = np.nan
    result["lensing_mass_correction_status"] = "not_required"
    result["lensing_provenance"] = ""
    result["mbh_method"] = MASS_METHOD
    result["log_mbh_err_plus"] = raw["log_mbh_err_plus"]
    result["log_mbh_err_minus"] = raw["log_mbh_err_minus"]
    result["mbh_statistical_uncertainty_kind"] = (
        "published_formal_errors_propagated_from_broad_halpha_flux_and_fwhm"
    )
    result["log_mbh_systematic_dex"] = 0.4
    result["mbh_systematic_kind"] = "single_epoch_virial_calibration"
    result["mbh_systematic_applied_flag"] = False
    result["mass_comparability_group"] = "virial_balmer_single_epoch"
    conditional = raw["mass_conditional_on_blr_flag"].astype(bool)
    result["conditional_mass_flag"] = conditional
    result["conditional_mass_reason"] = np.where(
        conditional, "mass_valid_only_if_broad_component_is_blr", "",
    )
    result["primary_mass_comparison_flag"] = True
    result["primary_mass_comparison_reason"] = "balmer_single_epoch_primary_stratum"
    result["log_mstar_err_plus"] = raw["log_mstar_err_plus"]
    result["log_mstar_err_minus"] = raw["log_mstar_err_minus"]
    result["log_mstar_upper_limit_msun"] = np.nan
    result["host_property_scope"] = np.where(
        dual, "shared_host_system_total", "object_specific",
    )
    result["log_lbol_err_plus"] = raw["log_lbol_err_plus"]
    result["log_lbol_err_minus"] = raw["log_lbol_err_minus"]
    result["log_edd_ratio_published"] = raw["log_edd_ratio"]
    result["edd_ratio_method"] = "source_derived_from_same_lbol_and_virial_mbh"
    result["growth_ranking_eligible_flag"] = True
    result["growth_ranking_eligibility_reason"] = GROWTH_ELIGIBLE_REASON
    result["primary_growth_ranking_flag"] = robust
    result["primary_growth_ranking_reason"] = np.where(
        robust, PRIMARY_ELIGIBLE_REASON, "candidate_evidence_excluded",
    )
    result["selection_channel"] = "host-selected;broad-halpha"
    result["broad_line_species"] = "Halpha"
    result["halpha_flux_broad_1e18_erg_s_cm2"] = raw[
        "halpha_broad_flux_dustcorr_1e18"
    ]
    result["halpha_flux_broad_err_plus"] = raw["halpha_broad_flux_err"]
    result["halpha_flux_broad_err_minus"] = raw["halpha_broad_flux_err"]
    result["halpha_broad_fwhm_km_s"] = raw[
        "halpha_broad_fwhm_instrumentcorr_km_s"
    ]
    result["halpha_broad_fwhm_err_plus"] = raw["halpha_broad_fwhm_err"]
    result["halpha_broad_fwhm_err_minus"] = raw["halpha_broad_fwhm_err"]
    result["fwhm_instrument_corrected_flag"] = True
    result["lrd_definition"] = "not reported per published Table 1 row"
    result["dual_agn_candidate_flag"] = dual
    result["mbh_formal_uncertainty_kind"] = result[
        "mbh_statistical_uncertainty_kind"
    ]
    result["dust_correction_applied_flag"] = True
    for field in [
        "host_system_source_id", "published_aliases", "halpha_broad_flux_dustcorr_1e18",
        "halpha_broad_flux_err", "halpha_broad_fwhm_instrumentcorr_km_s",
        "halpha_broad_fwhm_err", "ebv_mag", "av_mag", "robust_candidate_flag",
        "oiii_outflow_detected_flag", "halpha_three_component_fit_flag",
    ]:
        result[field] = raw[field]
    validate_v7_admission(result)
    return result


def build_ren_observables(
    raw_table2: pd.DataFrame,
    measurement_object_map: pd.DataFrame,
) -> pd.DataFrame:
    """Return the validated, source-native long-form Table 2 observations."""
    return validate_ren_table2(raw_table2, measurement_object_map)


def v6_identity_candidates(
    admission: pd.DataFrame,
    v6_measurements: pd.DataFrame,
) -> pd.DataFrame:
    """Return any coordinate/redshift candidates against the frozen v6 graph."""
    return candidate_matches(admission, v6_measurements)
