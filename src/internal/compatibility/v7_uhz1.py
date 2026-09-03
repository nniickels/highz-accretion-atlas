"""UHZ1 X-ray evidence-history validation and v7 admission."""

from __future__ import annotations

import re

import numpy as np
import pandas as pd

from src.models import cosmic_time_gyr
from src.internal.compatibility.v7_admission import validate_v7_admission, validate_v7_observables


SOURCE_KEY = "uhz1_xray_evidence_history"
EVIDENCE_FAMILY = "xray_agn_candidate"
PHYSICAL_OBJECT_ID = "HZA-UHZ1"
HOST_SYSTEM_ID = "HZS-UHZ1"
EXPECTED_ARCHIVES = {
    "arXiv:2305.15458v2": "d1446d873c81c0ee83f7cc1c0648d85f8a93b0967eb5d14ef7b46d0564ab2e6c",
    "arXiv:2308.02750v3": "73628a4c4632871e6b3888b61f2e6cedf28ead1d1af7f45a20cac20f8988b729",
    "arXiv:2603.24893v2": "04397db6d5e88983e650542bc6032735738edeb63c1310df15a215dcc68ed9ab",
}


def validate_uhz1_sources(history: pd.DataFrame, miri: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    required = {
        "measurement_id", "object_id", "ra_deg", "dec_deg", "redshift",
        "redshift_kind", "lensing_mu", "evidence_status", "source_paper_version",
        "source_url", "source_archive_url", "source_archive_sha256",
        "hard_xray_significance_low_sigma", "hard_xray_significance_high_sigma",
        "log_lbol_erg_s", "lbol_censoring", "selection_criteria", "source_caveat_tags",
    }
    if missing := sorted(required - set(history.columns)):
        raise ValueError(f"UHZ1 evidence history missing columns: {missing}")
    if len(history) != 2 or not history["measurement_id"].is_unique:
        raise ValueError("UHZ1 evidence history must contain two unique measurement versions")
    if set(history["measurement_id"]) != {"UHZ1_bogdan24", "UHZ1_zou26"}:
        raise ValueError("UHZ1 evidence-history measurement anchors changed")
    if set(history["evidence_status"]) != {"candidate", "disputed"}:
        raise ValueError("UHZ1 must retain candidate and disputed evidence versions")
    numeric = [
        "ra_deg", "dec_deg", "redshift", "lensing_mu", "lensing_mu_err_plus",
        "lensing_mu_err_minus", "hard_xray_significance_low_sigma",
        "hard_xray_significance_high_sigma", "hard_xray_total_counts",
        "hard_xray_net_counts", "log_lx_intrinsic_2_10kev_erg_s", "log_lbol_erg_s",
        "assumed_log_mbh_lower", "assumed_log_mbh_upper",
    ]
    clean = history.copy()
    clean[numeric] = clean[numeric].apply(pd.to_numeric, errors="raise")
    for item in clean.itertuples(index=False):
        versions = re.findall(r"arXiv:\d{4}\.\d{5}v\d+", item.source_paper_version)
        if len(versions) != 1 or versions[0] not in EXPECTED_ARCHIVES:
            raise ValueError(f"Unexpected UHZ1 source version: {item.source_paper_version}")
        version = versions[0]
        expected_url = f"https://arxiv.org/e-print/{version.removeprefix('arXiv:')}"
        if item.source_archive_url != expected_url:
            raise ValueError(f"UHZ1 archive URL does not match {version}")
        if item.source_archive_sha256 != EXPECTED_ARCHIVES[version]:
            raise ValueError(f"UHZ1 archive hash does not match {version}")
    if not np.allclose(clean["ra_deg"], 3.567066666666667) or not np.allclose(
        clean["dec_deg"], -30.377856944444446
    ):
        raise ValueError("UHZ1 coordinate anchor changed")
    bogdan = clean.set_index("measurement_id").loc["UHZ1_bogdan24"]
    zou = clean.set_index("measurement_id").loc["UHZ1_zou26"]
    if (bogdan["assumed_log_mbh_lower"], bogdan["assumed_log_mbh_upper"]) != (7.0, 8.0):
        raise ValueError("UHZ1 assumed-Eddington mass range anchor changed")
    if not (zou["hard_xray_significance_low_sigma"] == 2.3 and zou["hard_xray_significance_high_sigma"] == 2.9):
        raise ValueError("UHZ1 reanalysis significance range changed")

    miri_required = {
        "band", "pivot_wavelength_micron", "exposure_time_s",
        "flux_density_upper_limit_microjy",
    }
    if missing := sorted(miri_required - set(miri.columns)):
        raise ValueError(f"Zou et al. MIRI table missing columns: {missing}")
    clean_miri = miri.copy()
    if len(clean_miri) != 9 or not clean_miri["band"].is_unique:
        raise ValueError("Zou et al. MIRI Table 3 must contain nine unique bands")
    clean_miri[list(miri_required - {"band"})] = clean_miri[
        list(miri_required - {"band"})
    ].apply(pd.to_numeric, errors="raise")
    if clean_miri.set_index("band").loc["F560W", "flux_density_upper_limit_microjy"] != 0.13:
        raise ValueError("Zou et al. F560W limit anchor changed")
    return clean, clean_miri


def build_uhz1_admission(
    history: pd.DataFrame,
    miri: pd.DataFrame,
    *,
    template_columns: list[str],
) -> pd.DataFrame:
    """Map both published evidence assessments without inventing a point mass."""
    source, _ = validate_uhz1_sources(history, miri)
    rows = pd.DataFrame(pd.NA, index=range(len(source)), columns=template_columns, dtype=object)
    for index, raw in source.reset_index(drop=True).iterrows():
        values = {
            "catalogue_release": "v7-accreting-atlas-catalogue",
            "physical_object_id": PHYSICAL_OBJECT_ID,
            "measurement_id": raw["measurement_id"],
            "object_id": raw["object_id"],
            "ra_deg": raw["ra_deg"],
            "dec_deg": raw["dec_deg"],
            "redshift": raw["redshift"],
            "redshift_kind": raw["redshift_kind"],
            "cosmic_time_gyr": float(cosmic_time_gyr(raw["redshift"])),
            "survey": "Chandra Abell 2744; JWST UNCOVER",
            "object_class": "xray_agn_candidate",
            "mbh_method": "",
            "detection_evidence": raw["evidence_status"],
            "log_lbol_erg_s_std": (
                raw["log_lbol_erg_s"] if raw["lbol_censoring"] == "detection" else np.nan
            ),
            "lbol_method": (
                "xray_bolometric_correction_duras2020" if raw["measurement_id"] == "UHZ1_bogdan24" else ""
            ),
            "edd_ratio_consistency_flag": "not_evaluable",
            "lensing_mu": raw["lensing_mu"],
            "lensing_mu_err": np.nan,
            "missing_mstar_flag": True,
            "missing_lbol_flag": raw["lbol_censoring"] != "detection",
            "missing_edd_ratio_flag": True,
            "missing_lensing_flag": False,
            "missing_optional_fields": (
                "mstar;edd_ratio" if raw["lbol_censoring"] == "detection" else "mstar;lbol;edd_ratio"
            ),
            "mbh_interpretation_tag": "no_canonical_numeric_mass_assumption_dependent_range_only",
            "mstar_interpretation_tag": "host_mass_retained_as_source_observable",
            "lbol_interpretation_tag": (
                "source_xray_bolometric_estimate" if raw["lbol_censoring"] == "detection"
                else "source_upper_limit_retained_as_censored_observable"
            ),
            "quality_flag": "tentative",
            "project_version": "v7",
            "source_key": SOURCE_KEY,
            "source_table": "UHZ1 X-ray evidence history; source text and Zou et al. Tables 2-3",
            "notes": (
                "Original X-ray interpretation retained as a historical measurement version."
                if raw["measurement_id"] == "UHZ1_bogdan24" else
                "Preferred current evidence assessment; no compelling luminous obscured AGN evidence."
            ),
            "field": "Abell 2744",
            "selection_channel": "xray",
            "lrd_flag": np.nan,
            "log_mbh_systematic_dex": np.nan,
            "mbh_systematic_kind": "",
            "mbh_systematic_applied_flag": False,
            "source_caveat_tags": raw["source_caveat_tags"],
            "source_paper_version": raw["source_paper_version"],
            "source_url": raw["source_url"],
            "source_doi": "" if pd.isna(raw["source_doi"]) else raw["source_doi"],
            "source_archive_url": raw["source_archive_url"],
            "source_archive_sha256": raw["source_archive_sha256"],
            "extraction_date": "2026-08-27",
            "selection_criteria": raw["selection_criteria"],
            "evidence_status": raw["evidence_status"],
            "evidence_status_basis": (
                "source_reported_4p2_to_4p4_sigma_hard_xray_excess_modelled_as_obscured_agn"
                if raw["measurement_id"] == "UHZ1_bogdan24" else
                "full_dataset_reanalysis_finds_only_2p3_to_2p9_sigma_nonpersistent_excess_and_miri_limits"
            ),
            "spectroscopic_type": "unknown",
            "selection_channels": "xray;photometric_sed",
            "phenotype_tags": "",
            "lensing_status": "lensed",
            "growth_ranking_eligible_flag": False,
            "primary_growth_ranking_flag": False,
            "preferred_measurement_flag": raw["measurement_id"] == "UHZ1_zou26",
            "preferred_measurement_reason": (
                "superseded by full 2.2 Ms Chandra and JWST MIRI reanalysis"
                if raw["measurement_id"] == "UHZ1_bogdan24" else
                "latest full-dataset multiwavelength evidence assessment"
            ),
            "match_method": "source-verified same object evidence history",
            "match_reference": "UHZ1 and UNCOVER-26185 aliases at identical published coordinates",
            "host_system_id": HOST_SYSTEM_ID,
            "host_system_assignment_status": "source_verified_single_galaxy_host",
            "identity_resolution_status": "resolved",
            "extraction_date_status": "recorded",
            "lensing_mass_correction_status": "not_required",
            "lensing_provenance": (
                f"source-reported magnification mu={raw['lensing_mu']}; no canonical numeric BH mass admitted"
            ),
            "log_mbh_err_plus": np.nan,
            "log_mbh_err_minus": np.nan,
            "log_mstar_err_plus": np.nan,
            "log_mstar_err_minus": np.nan,
            "log_lbol_err_plus": np.nan,
            "log_lbol_err_minus": np.nan,
            "mbh_statistical_uncertainty_kind": "",
            "mass_comparability_group": "no_numeric_mass",
            "conditional_mass_flag": False,
            "conditional_mass_reason": "",
            "primary_mass_comparison_flag": False,
            "primary_mass_comparison_reason": "no_canonical_numeric_mass",
            "log_mstar_upper_limit_msun": np.nan,
            "host_property_scope": "not_published",
            "growth_ranking_eligibility_reason": "missing_numeric_mbh",
            "primary_growth_ranking_reason": "not_exploratory_eligible",
            "published_aliases": "UHZ1;UHZ-1;UNCOVER-26185",
        }
        for compatibility in [
            "log_mbh_msun_std", "log_mbh_err_plus_std", "log_mbh_err_minus_std",
            "log_mstar_msun_std", "log_mstar_err_plus_std", "log_mstar_err_minus_std",
            "edd_ratio_std", "log_mbh_err_plus", "log_mbh_err_minus",
            "log_mstar_err_plus", "log_mstar_err_minus",
        ]:
            values.setdefault(compatibility, np.nan)
        for key, value in values.items():
            if key in rows.columns:
                rows.loc[index, key] = value
    rows = rows.infer_objects(copy=False)
    validate_v7_admission(rows)
    return rows


def _observable(
    measurement_id: str, name: str, value: float, unit: str, source_location: str,
    *, censoring: str = "detection", err_plus: float | None = None,
    err_minus: float | None = None,
) -> dict[str, object]:
    return {
        "observable_id": f"{measurement_id}__{name}",
        "measurement_id": measurement_id,
        "observable_name": name,
        "value": value,
        "err_plus": err_plus,
        "err_minus": err_minus,
        "censoring": censoring,
        "unit": unit,
        "uncertainty_kind": (
            "limit" if censoring != "detection" else
            "published_asymmetric" if err_plus is not None else "not_published"
        ),
        "source_location": source_location,
    }


def build_uhz1_observables(history: pd.DataFrame, miri: pd.DataFrame) -> pd.DataFrame:
    source, clean_miri = validate_uhz1_sources(history, miri)
    raw = source.set_index("measurement_id")
    rows: list[dict[str, object]] = []
    for measurement_id in raw.index:
        item = raw.loc[measurement_id]
        location = item["source_paper_version"]
        for suffix, field in [("low", "hard_xray_significance_low_sigma"), ("high", "hard_xray_significance_high_sigma")]:
            rows.append(_observable(measurement_id, f"hard_xray_significance_{suffix}", item[field], "sigma", location))
        rows.append(_observable(
            measurement_id, "lensing_mu", item["lensing_mu"], "dimensionless", location,
            err_plus=item["lensing_mu_err_plus"], err_minus=item["lensing_mu_err_minus"],
        ))
    bogdan = raw.loc["UHZ1_bogdan24"]
    for name, field, unit in [
        ("hard_xray_total_counts", "hard_xray_total_counts", "count"),
        ("hard_xray_net_counts", "hard_xray_net_counts", "count"),
        ("log_lx_intrinsic_2_10kev", "log_lx_intrinsic_2_10kev_erg_s", "log10(erg/s)"),
        ("log_lbol", "log_lbol_erg_s", "log10(erg/s)"),
    ]:
        rows.append(_observable("UHZ1_bogdan24", name, bogdan[field], unit, "Bogdan et al. (2024) source text"))
    rows.extend([
        _observable("UHZ1_bogdan24", "assumed_log_mbh_range_lower", 7.0, "log10(Msun)", "Bogdan et al. (2024) source text", censoring="lower_limit"),
        _observable("UHZ1_bogdan24", "assumed_log_mbh_range_upper", 8.0, "log10(Msun)", "Bogdan et al. (2024) source text", censoring="upper_limit"),
        _observable("UHZ1_zou26", "log_lbol_buried_agn", 45.11394335230683, "log10(erg/s)", "Zou et al. (2026) Section 4", censoring="upper_limit"),
    ])
    for _, item in clean_miri.iterrows():
        rows.append(_observable(
            "UHZ1_zou26", f"miri_{item['band'].lower()}_flux_density",
            item["flux_density_upper_limit_microjy"], "microJy",
            "Zou et al. (2026) Table 3", censoring="upper_limit",
        ))
    result = pd.DataFrame(rows)
    validate_v7_observables(result, source["measurement_id"])
    return result
