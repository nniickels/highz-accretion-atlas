"""Scholtz et al. JADES narrow/high-ionization AGN admission."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.identity import stable_object_id
from src.models import cosmic_time_gyr
from src.v7_admission import validate_v7_admission, validate_v7_observables


SOURCE_KEY = "scholtz25_jades_narrow_line_agn"
EVIDENCE_FAMILY = "narrow_line_and_high_ionization_agn_candidates"
PAPER_ARCHIVE_SHA256 = "1754f005be9e77cc619e52c42b9d47f27fa66fd4d0e80cfd0406afdeca463624"
COORDINATE_ARCHIVE_SHA256 = "e30d7cc9be5c997e73b47023b03df79658e8f797407ea9361295dd7d488b56ba"
EXPECTED_ARCHIVES = {
    "arXiv:2311.18731v4": PAPER_ARCHIVE_SHA256,
    "JADES-DR3-GOODS-S-prism-v3.1.3": COORDINATE_ARCHIVE_SHA256,
}


def validate_scholtz_source(source: pd.DataFrame) -> pd.DataFrame:
    required = {
        "measurement_id", "object_id", "nirspec_id", "program_id", "ra_deg",
        "dec_deg", "redshift", "selection_method", "tentative_flag",
        "log_mstar_msun", "log_mstar_err_plus", "log_mstar_err_minus",
        "sfr_msun_yr", "sfr_err_plus", "sfr_err_minus", "muv",
        "log_lbol_erg_s", "notes", "neiv2424_flux_1e19",
        "neiv2424_err_1e19", "nev3427_flux_1e19", "nev3427_err_1e19",
        "nv1240_flux_1e19", "nv1240_err_1e19",
    }
    if missing := sorted(required - set(source.columns)):
        raise ValueError(f"Scholtz source extraction missing columns: {missing}")
    clean = source.copy()
    if len(clean) != 20 or not clean["measurement_id"].is_unique:
        raise ValueError("Scholtz z>=4 extraction must contain 20 unique tabulated rows")
    numeric = sorted(required - {"measurement_id", "object_id", "selection_method", "tentative_flag", "notes"})
    clean[numeric] = clean[numeric].apply(pd.to_numeric, errors="raise")
    clean["tentative_flag"] = clean["tentative_flag"].map(
        lambda value: value if isinstance(value, bool) else str(value).strip().lower() == "true"
    )
    if clean["redshift"].lt(4).any():
        raise ValueError("Scholtz atlas extraction contains a row below z=4")
    if int(clean["tentative_flag"].sum()) != 3:
        raise ValueError("Expected three z>=4 S2-VO87 tentative rows")
    if int(clean[["neiv2424_flux_1e19", "nev3427_flux_1e19", "nv1240_flux_1e19"]].notna().sum().sum()) != 7:
        raise ValueError("Expected seven published high-ionization-line detections")
    anchor = clean.set_index("nirspec_id").loc[10058975]
    if (anchor["redshift"], anchor["log_lbol_erg_s"], anchor["neiv2424_flux_1e19"]) != (9.437, 44.4, 1.88):
        raise ValueError("JADES 10058975 source anchors changed")
    return clean


def _selection_channels(method: str) -> str:
    high = "High ion" in method or "HeII" in method
    return "narrow_line_diagnostics;high_ionization_line" if high else "narrow_line_diagnostics"


def build_scholtz_admission(
    source: pd.DataFrame, *, template_columns: list[str], reserved_ids: set[str],
) -> pd.DataFrame:
    clean = validate_scholtz_source(source)
    rows = pd.DataFrame(pd.NA, index=range(len(clean)), columns=template_columns, dtype=object)
    allocated = set(reserved_ids)
    for index, raw in clean.reset_index(drop=True).iterrows():
        is_8083 = int(raw["nirspec_id"]) == 8083
        physical_id = stable_object_id(
            raw["object_id"], source_key=SOURCE_KEY, reserved_ids=allocated,
        )
        allocated.add(physical_id)
        values = {
            "catalogue_release": "v7.4-accreting-atlas-catalogue",
            "physical_object_id": physical_id,
            "host_system_id": physical_id.replace("HZA-", "HZS-", 1),
            "measurement_id": raw["measurement_id"],
            "object_id": raw["object_id"],
            "ra_deg": raw["ra_deg"], "dec_deg": raw["dec_deg"],
            "redshift": raw["redshift"], "redshift_kind": "spec",
            "cosmic_time_gyr": float(cosmic_time_gyr(raw["redshift"])),
            "survey": "JWST JADES NIRSpec", "field": "GOODS-S",
            "object_class": "broad_line_agn" if is_8083 else "narrow_line_agn_candidate",
            "mbh_method": "", "detection_evidence": "candidate",
            "log_mstar_msun_std": raw["log_mstar_msun"],
            "log_mstar_err_plus_std": raw["log_mstar_err_plus"],
            "log_mstar_err_minus_std": raw["log_mstar_err_minus"],
            "log_lbol_erg_s_std": raw["log_lbol_erg_s"],
            "lbol_method": "Halpha_or_Hbeta_narrow_line_bolometric_correction",
            "edd_ratio_consistency_flag": "not_evaluable",
            "lensing_mu": np.nan, "lensing_mu_err": np.nan,
            "missing_mstar_flag": False, "missing_lbol_flag": False,
            "missing_edd_ratio_flag": True, "missing_lensing_flag": True,
            "missing_optional_fields": "edd_ratio;lensing",
            "mbh_interpretation_tag": "no_numeric_black_hole_mass_published",
            "mstar_interpretation_tag": "source_host_sed_fit",
            "lbol_interpretation_tag": "source_narrow_line_bolometric_estimate",
            "quality_flag": "tentative" if raw["tentative_flag"] else "source_candidate",
            "project_version": "v7.4", "source_key": SOURCE_KEY,
            "source_table": "Scholtz et al. Table 1; Appendix Table A.1; JADES DR3 target coordinates",
            "notes": str(raw["notes"]) if pd.notna(raw["notes"]) else "",
            "selection_channel": "narrow_line_spectroscopy",
            "lrd_flag": np.nan, "log_mbh_systematic_dex": np.nan,
            "mbh_systematic_kind": "", "mbh_systematic_applied_flag": False,
            "source_caveat_tags": (
                "paper_abstract_reports_42_but_table_contains_41;tentative_within_0p1dex_of_s2_demarcation"
                if raw["tentative_flag"] else "paper_abstract_reports_42_but_table_contains_41"
            ),
            "source_paper_version": "A&A 697 A175 (2025); arXiv:2311.18731v4",
            "source_url": "https://arxiv.org/abs/2311.18731",
            "source_doi": "10.1051/0004-6361/202348804",
            "source_archive_url": "https://arxiv.org/e-print/2311.18731v4",
            "source_archive_sha256": PAPER_ARCHIVE_SHA256,
            "extraction_date": "2026-08-27",
            "selection_criteria": f"z>=4; source-classified AGN in {raw['selection_method']}",
            "evidence_status": "candidate",
            "evidence_status_basis": (
                "source_classified_candidate_tentative_s2_boundary" if raw["tentative_flag"]
                else "source_classified_narrow_or_high_ionization_line_agn_candidate"
            ),
            "spectroscopic_type": "type1_broad_line" if is_8083 else "type2_narrow_line",
            "selection_channels": _selection_channels(raw["selection_method"]),
            "phenotype_tags": "", "lensing_status": "not_reported",
            "growth_ranking_eligible_flag": False, "primary_growth_ranking_flag": False,
            "preferred_measurement_flag": not is_8083,
            "preferred_measurement_reason": (
                "existing broad-line mass measurement remains preferred" if is_8083
                else "only catalogue measurement in this release"
            ),
            "match_method": "manual source-ID assertion" if is_8083 else "singleton assignment",
            "match_reference": "JADES NIRSpec ID 8083" if is_8083 else "Scholtz et al. source table",
            "host_system_assignment_status": "source_verified_single_galaxy_host",
            "identity_resolution_status": "resolved", "extraction_date_status": "recorded",
            "lensing_mass_correction_status": "not_required",
            "lensing_provenance": "not reported; no numeric black-hole mass admitted",
            "log_mbh_err_plus": np.nan, "log_mbh_err_minus": np.nan,
            "log_mstar_err_plus": raw["log_mstar_err_plus"],
            "log_mstar_err_minus": raw["log_mstar_err_minus"],
            "log_lbol_err_plus": np.nan, "log_lbol_err_minus": np.nan,
            "mbh_statistical_uncertainty_kind": "", "mass_comparability_group": "no_numeric_mass",
            "conditional_mass_flag": False, "conditional_mass_reason": "",
            "primary_mass_comparison_flag": False,
            "primary_mass_comparison_reason": "no_canonical_numeric_mass",
            "log_mstar_upper_limit_msun": np.nan, "host_property_scope": "object_specific",
            "growth_ranking_eligibility_reason": "missing_numeric_mbh",
            "primary_growth_ranking_reason": "not_exploratory_eligible",
            "published_aliases": raw["object_id"],
        }
        for compatibility in [
            "log_mbh_msun_std", "log_mbh_err_plus_std", "log_mbh_err_minus_std",
            "edd_ratio_std",
        ]:
            values[compatibility] = np.nan
        for key, value in values.items():
            if key in rows.columns:
                rows.loc[index, key] = value
    rows = rows.infer_objects(copy=False)
    validate_v7_admission(rows)
    return rows


def build_scholtz_observables(source: pd.DataFrame) -> pd.DataFrame:
    clean = validate_scholtz_source(source)
    rows: list[dict[str, object]] = []
    def add(mid: str, name: str, value: float, unit: str, *, ep=np.nan, em=np.nan, location="Table 1") -> None:
        rows.append({
            "observable_id": f"{mid}__{name}", "measurement_id": mid,
            "observable_name": name, "value": value, "err_plus": ep, "err_minus": em,
            "censoring": "detection", "unit": unit,
            "uncertainty_kind": "published_asymmetric" if pd.notna(ep) else "not_published",
            "source_location": f"Scholtz et al. (2025) {location}",
        })
    for _, raw in clean.iterrows():
        mid = raw["measurement_id"]
        add(mid, "log_mstar", raw["log_mstar_msun"], "log10(Msun)", ep=raw["log_mstar_err_plus"], em=raw["log_mstar_err_minus"])
        add(mid, "sfr", raw["sfr_msun_yr"], "Msun/yr", ep=raw["sfr_err_plus"], em=raw["sfr_err_minus"])
        add(mid, "muv", raw["muv"], "AB mag")
        add(mid, "log_lbol", raw["log_lbol_erg_s"], "log10(erg/s)")
        for name, value_col, err_col in [
            ("neiv2424_flux", "neiv2424_flux_1e19", "neiv2424_err_1e19"),
            ("nev3427_flux", "nev3427_flux_1e19", "nev3427_err_1e19"),
            ("nv1240_flux", "nv1240_flux_1e19", "nv1240_err_1e19"),
        ]:
            if pd.notna(raw[value_col]):
                add(mid, name, raw[value_col], "1e-19 erg/s/cm2", ep=raw[err_col], em=raw[err_col], location="Appendix Table A.1")
    result = pd.DataFrame(rows)
    validate_v7_observables(result, clean["measurement_id"])
    return result
