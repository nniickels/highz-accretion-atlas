"""Admission adapter for the final JWST-identified v3 completion sources."""

from __future__ import annotations

import re

import numpy as np
import pandas as pd

from src.models import cosmic_time_gyr
from src.internal.compatibility.v7_admission import validate_v7_admission, validate_v7_observables
from src.internal.compatibility.v7_catalogue import _aggregate_objects_with_preferred_evidence
from src.internal.compatibility.v7_core_catalogue import _build_host_systems, _build_strata, _set_eligibility


SOURCE_METADATA = {
    "zhuang25_nexus_wfss": {
        "survey": "NEXUS-Wide EDR", "field": "North Ecliptic Pole",
        "version": "arXiv:2505.20393v1 submitted to ApJ",
        "url": "https://arxiv.org/abs/2505.20393v1",
        "doi": "10.48550/arXiv.2505.20393",
        "archive": "https://arxiv.org/e-print/2505.20393v1",
        "sha": "e0fd19d3b0a079efeccea6fda92faa54876a5c293b24bdda7106f7df80978048",
    },
    "lin25_cosmos3d_blagn": {
        "survey": "COSMOS-3D", "field": "COSMOS",
        "version": "ApJ accepted; arXiv:2504.08039v2",
        "url": "https://doi.org/10.3847/1538-4357/ae1b9b",
        "doi": "10.3847/1538-4357/ae1b9b",
        "archive": "https://arxiv.org/e-print/2504.08039v2",
        "sha": "3a056a22de95bf81524433d955905d15f65176e16e138fd00128826e5fa5bb52",
    },
    "napolitano25_seven_wonders": {
        "survey": "GLASS-JWST GO-3073", "field": "Abell 2744",
        "version": "A&A 693, A50 (2025); arXiv:2410.10967v1",
        "url": "https://doi.org/10.1051/0004-6361/202452090",
        "doi": "10.1051/0004-6361/202452090",
        "archive": "https://arxiv.org/e-print/2410.10967v1",
        "sha": "a8eb5e6c2ea10e65d70d5a7cee5e9d5df4681f24f262296f6c19477faa024b31",
    },
}

NX10835_PRIOR_OBJECT_ID = "nexus-obs3_5105_10835"


def _identifier(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", value.upper()).strip("-")


def _number(record: dict[str, object], field: str) -> float:
    value = record.get(field)
    return float(value) if pd.notna(value) else np.nan


def _physical_ids(record: dict[str, object], existing: pd.DataFrame) -> tuple[str, str]:
    if record["source_key"] == "zhuang25_nexus_wfss" and record["object_id"] == "NX10835":
        prior = existing.loc[existing["object_id"].eq(NX10835_PRIOR_OBJECT_ID)]
        if len(prior) != 1:
            raise ValueError("NX10835 requires exactly one pre-existing Mascia identity")
        return str(prior.iloc[0]["physical_object_id"]), str(prior.iloc[0]["host_system_id"])
    ident = _identifier(str(record["object_id"]))
    return f"HZA-{ident}", f"HZS-{ident}"


def build_additions(
    raw: pd.DataFrame, template_columns: list[str], existing: pd.DataFrame,
) -> pd.DataFrame:
    """Translate the three source tables into the canonical measurement schema."""
    rows: list[dict[str, object]] = []
    for record in raw.to_dict("records"):
        source_key = str(record["source_key"])
        meta = SOURCE_METADATA[source_key]
        physical_id, host_id = _physical_ids(record, existing)
        mass = _number(record, "log_mbh_msun")
        has_mass = np.isfinite(mass)
        line = str(record.get("broad_line_species")) if pd.notna(record.get("broad_line_species")) else ""
        is_nexus = source_key == "zhuang25_nexus_wfss"
        mass_method = ""
        if has_mass:
            calibration = "reines2015" if is_nexus else "greene2005"
            mass_method = f"single-epoch-virial-{line.lower()}-{calibration}"
        row = {column: np.nan for column in template_columns}
        row.update({
            "catalogue_release": "complete-catalogue",
            "measurement_id": record["measurement_id"], "object_id": record["object_id"],
            "physical_object_id": physical_id, "host_system_id": host_id,
            "ra_deg": record["ra_deg"], "dec_deg": record["dec_deg"],
            "redshift": record["redshift"], "redshift_kind": record["redshift_kind"],
            "redshift_err": _number(record, "redshift_err_plus"),
            "cosmic_time_gyr": float(cosmic_time_gyr(record["redshift"])),
            "survey": meta["survey"], "program": meta["survey"], "field": meta["field"],
            "object_class": record["object_class"], "evidence_status": record["evidence_status"],
            "evidence_status_basis": record["evidence_status_basis"],
            "spectroscopic_type": record["spectroscopic_type"],
            "selection_channels": record["selection_channels"],
            "selection_channel": str(record["selection_channels"]).replace(";", "+"),
            "phenotype_tags": record.get("phenotype_tags", ""),
            "source_key": source_key, "source_table": record["source_table"],
            "source_paper_version": meta["version"], "source_url": meta["url"],
            "source_doi": meta["doi"], "source_archive_url": meta["archive"],
            "source_archive_sha256": meta["sha"], "extraction_date": "2026-09-03",
            "extraction_date_status": "recorded", "selection_criteria": record["selection_criteria"],
            "source_caveat_tags": record["source_caveat_tags"],
            "notes": record.get("notes", ""), "quality_flag": record["evidence_status"],
            "detection_evidence": record["evidence_status_basis"],
            "log_mbh_msun_std": mass, "log_mbh_err_plus_std": _number(record, "log_mbh_err_plus"),
            "log_mbh_err_minus_std": _number(record, "log_mbh_err_minus"),
            "log_mbh_err_plus": _number(record, "log_mbh_err_plus"),
            "log_mbh_err_minus": _number(record, "log_mbh_err_minus"),
            "mbh_method": mass_method,
            "mbh_interpretation_tag": mass_method if has_mass else "no_numeric_black_hole_mass_published",
            "mbh_formal_uncertainty_kind": record.get("mbh_statistical_uncertainty_kind", "") if has_mass else "",
            "mbh_statistical_uncertainty_kind": record.get("mbh_statistical_uncertainty_kind", "") if has_mass else "",
            "log_mbh_systematic_dex": _number(record, "log_mbh_systematic_dex"),
            "mbh_systematic_kind": record.get("mbh_systematic_kind", "") if has_mass else "",
            "mbh_systematic_applied_flag": False,
            "mass_comparability_group": "virial_balmer_single_epoch" if has_mass else "no_numeric_mass",
            "conditional_mass_flag": False, "conditional_mass_reason": "",
            "primary_mass_comparison_flag": has_mass,
            "primary_mass_comparison_reason": "balmer_single_epoch_primary_stratum" if has_mass else "no_canonical_numeric_mass",
            "host_property_scope": "not_published", "mstar_method": "", "lbol_method": "", "edd_ratio_method": "",
            "identity_resolution_status": "resolved",
            "host_system_assignment_status": "source_verified_single_object_host",
            "preferred_measurement_flag": True,
            "preferred_measurement_reason": "canonical mass-bearing NEXUS measurement for existing object" if record["object_id"] == "NX10835" else "only admitted measurement for this newly added physical object",
            "match_method": "source alias plus 0.066 arcsec coordinate and redshift match" if record["object_id"] == "NX10835" else "coordinate-redshift and alias audit against existing catalogue",
            "match_reference": NX10835_PRIOR_OBJECT_ID if record["object_id"] == "NX10835" else "no existing object within 10 arcsec at consistent redshift",
            "published_aliases": record.get("published_aliases", ""),
            "lensing_status": record["lensing_status"], "lensing_mu": _number(record, "lensing_mu"),
            "lensing_mass_correction_status": "not_required",
            "lensing_provenance": record.get("lensing_provenance", ""),
            "missing_mstar_flag": True, "missing_lbol_flag": True,
            "missing_edd_ratio_flag": True, "missing_lensing_flag": pd.isna(record.get("lensing_mu")),
            "broad_line_species": line,
            "halpha_broad_fwhm_km_s": _number(record, "broad_fwhm_km_s") if line == "Halpha" else np.nan,
            "halpha_broad_fwhm_err_plus": _number(record, "broad_fwhm_err_plus") if line == "Halpha" else np.nan,
            "halpha_broad_fwhm_err_minus": _number(record, "broad_fwhm_err_minus") if line == "Halpha" else np.nan,
            "halpha_lum_broad_1e42": _number(record, "line_luminosity_1e42") if line == "Halpha" else np.nan,
            "halpha_lum_broad_err_plus": _number(record, "line_luminosity_err_plus") if line == "Halpha" else np.nan,
            "halpha_lum_broad_err_minus": _number(record, "line_luminosity_err_minus") if line == "Halpha" else np.nan,
            "halpha_lum_broad_erg_s": 10 ** _number(record, "log_line_luminosity") if line == "Halpha" and pd.notna(record.get("log_line_luminosity")) else np.nan,
            "fwhm_instrument_corrected_flag": True if has_mass else False,
            "lrd_flag": record.get("lrd_flag"),
            "lrd_definition": (
                "source-classified LRD or reddened compact broad-line source"
                if pd.notna(record.get("lrd_flag")) and bool(record.get("lrd_flag"))
                else "not source-classified as LRD"
            ),
            "photometry_band": "F444W" if pd.notna(record.get("f444w_mag")) else "",
            "photometry_mag": _number(record, "f444w_mag"),
            "photometry_mag_err_plus": _number(record, "f444w_err"),
            "photometry_mag_err_minus": _number(record, "f444w_err"),
            "muv": _number(record, "muv"), "muv_err_plus": _number(record, "muv_err_plus"),
            "muv_err_minus": _number(record, "muv_err_minus"),
            "beta_opt": _number(record, "beta_opt"), "beta_opt_err_plus": _number(record, "beta_opt_err"),
            "beta_opt_err_minus": _number(record, "beta_opt_err"),
            "beta_uv": _number(record, "beta_uv"), "beta_uv_err_plus": _number(record, "beta_uv_err"),
            "beta_uv_err_minus": _number(record, "beta_uv_err"),
        })
        rows.append(row)
    additions = pd.DataFrame(rows, columns=template_columns)
    for column in ("growth_ranking_eligible_flag", "growth_ranking_eligibility_reason", "primary_growth_ranking_flag", "primary_growth_ranking_reason"):
        additions[column] = additions[column].astype("object")
    additions = _set_eligibility(additions)
    validate_v7_admission(additions)
    return additions


def build_observables(raw: pd.DataFrame) -> pd.DataFrame:
    """Preserve source-native values, uncertainties, and limits in long form."""
    specs = (
        ("log_mbh", "log_mbh_msun", "log10(Msun)"),
        ("broad_line_fwhm", "broad_fwhm_km_s", "km/s"),
        ("log_broad_line_luminosity", "log_line_luminosity", "log10(erg/s)"),
        ("broad_line_luminosity", "line_luminosity_1e42", "1e42 erg/s"),
        ("f444w_mag", "f444w_mag", "AB mag"), ("muv", "muv", "AB mag"),
        ("beta_opt", "beta_opt", "dimensionless"), ("beta_uv", "beta_uv", "dimensionless"),
        ("lensing_mu", "lensing_mu", "dimensionless"),
    )
    errors = {
        "log_mbh_msun": ("log_mbh_err_plus", "log_mbh_err_minus"),
        "broad_fwhm_km_s": ("broad_fwhm_err_plus", "broad_fwhm_err_minus"),
        "log_line_luminosity": ("log_line_luminosity_err_plus", "log_line_luminosity_err_minus"),
        "line_luminosity_1e42": ("line_luminosity_err_plus", "line_luminosity_err_minus"),
        "f444w_mag": ("f444w_err", "f444w_err"), "muv": ("muv_err_plus", "muv_err_minus"),
        "beta_opt": ("beta_opt_err", "beta_opt_err"), "beta_uv": ("beta_uv_err", "beta_uv_err"),
        "lensing_mu": (None, None),
    }
    rows = []
    for record in raw.to_dict("records"):
        for name, field, unit in specs:
            if pd.isna(record.get(field)):
                continue
            plus_field, minus_field = errors[field]
            plus = record.get(plus_field) if plus_field else np.nan
            minus = record.get(minus_field) if minus_field else np.nan
            censoring = record.get("muv_censoring", "detection") if field == "muv" else "detection"
            censoring = censoring if pd.notna(censoring) and censoring else "detection"
            rows.append({
                "observable_id": f"{record['measurement_id']}__{name}",
                "measurement_id": record["measurement_id"], "object_id": record["object_id"],
                "observable_name": name, "value": record[field],
                "err_plus": np.nan if censoring != "detection" else plus,
                "err_minus": np.nan if censoring != "detection" else minus,
                "censoring": censoring, "unit": unit,
                "uncertainty_kind": "limit" if censoring != "detection" else ("published_asymmetric_or_symmetric" if pd.notna(plus) and pd.notna(minus) else "not_published"),
                "source_location": record["source_table"],
            })
    result = pd.DataFrame(rows)
    validate_v7_observables(result, raw["measurement_id"])
    return result


def append_v3_completion(complete: dict[str, pd.DataFrame], raw: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Append completion sources, resolving NX10835 to its existing physical object."""
    measurements = complete["measurements"].copy()
    prior_mask = measurements["object_id"].eq(NX10835_PRIOR_OBJECT_ID)
    if prior_mask.sum() != 1:
        raise ValueError("Expected exactly one prior NX10835 candidate")
    additions = build_additions(raw, list(measurements.columns), measurements)
    existing_ids = set(measurements["physical_object_id"])
    collisions = set(additions["physical_object_id"]) & existing_ids
    allowed = {str(measurements.loc[prior_mask, "physical_object_id"].iloc[0])}
    if collisions != allowed:
        raise ValueError(f"Unexpected completion-source identity collisions: {sorted(collisions)}")
    prior = measurements.loc[prior_mask].iloc[0]
    nx = additions.loc[additions["object_id"].eq("NX10835")].iloc[0]
    dra = (float(prior["ra_deg"]) - float(nx["ra_deg"])) * np.cos(np.radians(float(nx["dec_deg"])))
    separation_arcsec = 3600 * np.hypot(dra, float(prior["dec_deg"]) - float(nx["dec_deg"]))
    if separation_arcsec > 0.5 or abs(float(prior["redshift"]) - float(nx["redshift"])) > 0.01:
        raise ValueError("NX10835 identity match failed coordinate/redshift tolerances")
    measurements.loc[prior_mask, "preferred_measurement_flag"] = False
    measurements.loc[prior_mask, "preferred_measurement_reason"] = "superseded by mass-bearing NEXUS WFSS measurement for the same physical object"
    measurements = pd.concat([measurements, additions], ignore_index=True).sort_values(
        ["source_key", "redshift", "measurement_id"], ascending=[True, False, True],
    ).reset_index(drop=True)
    objects = _aggregate_objects_with_preferred_evidence(measurements)
    hosts = _build_host_systems(measurements, catalogue_release="complete-catalogue")
    links = measurements[["catalogue_release", "measurement_id", "physical_object_id", "host_system_id", "preferred_measurement_flag", "preferred_measurement_reason", "match_method", "match_reference", "identity_resolution_status"]].copy()
    object_host_links = objects[["catalogue_release", "physical_object_id", "host_system_id", "host_system_assignment_status", "host_property_scope"]].copy()
    aliases = complete["aliases"].copy()
    new_aliases = additions[["catalogue_release", "physical_object_id", "host_system_id", "measurement_id", "object_id", "source_key", "ra_deg", "dec_deg", "redshift"]].copy()
    new_aliases["alias_kind"] = "source_object_id"
    aliases = pd.concat([aliases, new_aliases], ignore_index=True)
    observables = complete["observables"].copy()
    new_observables = build_observables(raw)
    new_observables.insert(0, "catalogue_release", "complete-catalogue")
    observables = pd.concat([observables, new_observables], ignore_index=True, sort=False)
    validate_v7_observables(observables, measurements["measurement_id"])
    audit = complete["external_literature_identity_audit"].copy()
    audit = pd.concat([audit, pd.DataFrame([{
        "catalogue_release": "complete-catalogue", "measurement_id": nx["measurement_id"],
        "object_id": nx["object_id"], "literature_alias": NX10835_PRIOR_OBJECT_ID,
        "literature_reference": "Zhuang et al. 2025 Table 1; Mascia et al. 2026 Table 2",
        "atlas_prior_candidate_count": 1, "identity_disposition": "same_physical_object",
        "review_basis": f"published alias plus {separation_arcsec:.3f} arcsec separation and delta-z=0.001",
        "review_date": "2026-09-03",
    }])], ignore_index=True)
    result = dict(complete)
    result.update({"measurements": measurements, "objects": objects, "host_systems": hosts,
                   "measurement_object_links": links, "object_host_links": object_host_links,
                   "aliases": aliases, "observables": observables,
                   "strata": _build_strata(measurements, objects, catalogue_release="complete-catalogue"),
                   "external_literature_identity_audit": audit})
    return result
