"""Admission builder for the post-review canonical-mass source additions."""

from __future__ import annotations

import re

import numpy as np
import pandas as pd

from src.models import cosmic_time_gyr
from src.internal.compatibility.v7_admission import validate_v7_admission
from src.internal.compatibility.v7_admission import validate_v7_observables
from src.internal.compatibility.v7_catalogue import _aggregate_objects_with_preferred_evidence
from src.internal.compatibility.v7_core_catalogue import _build_host_systems, _build_strata, _set_eligibility


SOURCE_METADATA = {
    "baccus26_nirspec_blagn": {
        "survey": "JWST/NIRSpec archival census", "field": "multi-field",
        "table": "Table 1, z>=4 new non-cluster subset",
        "version": "ApJ 1006, 165 (2026); arXiv:2512.03281v2",
        "url": "https://doi.org/10.3847/1538-4357/ae7de7",
        "doi": "10.3847/1538-4357/ae7de7",
        "archive": "https://arxiv.org/e-print/2512.03281v2",
        "sha": "b0e527296f6a71adb4782f0b57a416f494d33ec7c71a6afc6ee7db982659fa76",
        "selection": "JWST/NIRSpec broad-Halpha catalogue objects at z>=4 that are new to the atlas and do not require an unreported cluster-lensing correction",
    },
    "fei26_glimpse_blagn": {
        "survey": "GLIMPSE", "field": "Abell S1063",
        "table": "Tables 1 and 2",
        "version": "ApJ 1003, 244 (2026); arXiv:2509.20452v3",
        "url": "https://doi.org/10.3847/1538-4357/ae6248",
        "doi": "10.3847/1538-4357/ae6248",
        "archive": "https://arxiv.org/e-print/2509.20452v3",
        "sha": "c619ea23d3e29b15ceb78d6a75b276a55010ff0d31b47b0a377856c0e37acde1",
        "selection": "JWST/NIRSpec G395M broad-Halpha AGN at 4.5<z<7 with source-reported lensing corrections and numerical virial masses",
    },
    "greene24_uncover_blagn": {
        "survey": "UNCOVER", "field": "Abell 2744", "table": "Tables 1 and 3",
        "version": "ApJ 964, 39 (2024); arXiv:2309.05714",
        "url": "https://doi.org/10.3847/1538-4357/ad1e5f", "doi": "10.3847/1538-4357/ad1e5f",
        "archive": "https://arxiv.org/e-print/2309.05714",
        "sha": "85b361410e913c3c4f103b65cba079490d989c423dfa66d82c26d3c0c972dffe",
        "selection": "JWST/NIRSpec PRISM definitive broad-Balmer AGN with a published numerical virial mass",
    },
    "kocevski25_lrd_blagn": {
        "survey": "RUBIES", "field": "EGS/UDS", "table": "Table 5 canonical-mass z>=4 additions",
        "version": "ApJ 986, 126 (2025); arXiv:2404.03576v3",
        "url": "https://doi.org/10.3847/1538-4357/adbc7d", "doi": "10.3847/1538-4357/adbc7d",
        "archive": "https://arxiv.org/e-print/2404.03576v3",
        "sha": "d305676588e2dca634d350f11e20b69568e736de990faae0b681ed0b08ab5b69",
        "selection": "JWST/RUBIES secure new broad-line detections at z>=4 absent from the existing Taylor ingestion",
    },
    "skyfire26_ceers_blagn": {
        "survey": "Skyfire", "field": "EGS", "table": "Table 3 z>=4 rows with numerical black-hole masses",
        "version": "arXiv:2609.00112v1 (2026)",
        "url": "https://arxiv.org/abs/2609.00112v1", "doi": "10.48550/arXiv.2609.00112",
        "archive": "https://arxiv.org/e-print/2609.00112v1",
        "sha": "51ee2f02d36b8d07bf778fd739a231c2f7780a7465e4fbf41adb6e57779d8d1c",
        "selection": "JWST/NIRSpec G395M broad-Halpha sources at z>=4 with a published numerical mass",
    },
    "larson23_ceers1019": {
        "survey": "CEERS", "field": "EGS", "table": "Published CEERS 1019 measurements",
        "version": "ApJL 953, L29 (2023); arXiv:2303.08918",
        "url": "https://doi.org/10.3847/2041-8213/ace619", "doi": "10.3847/2041-8213/ace619",
        "archive": "https://arxiv.org/e-print/2303.08918v2",
        "sha": "aedc3f7bfb3064564e8ba1787c4a69747250d080b5917d7db3c702c50f8d9f18",
        "selection": "JWST/NIRSpec broad-Hbeta identification of CEERS 1019",
    },
    "killi24_j0647_lrd_blagn": {
        "survey": "JWST GO-1433", "field": "MACS J0647", "table": "Published J0647-1045 measurements",
        "version": "A&A 691, A52 (2024); arXiv:2312.03065",
        "url": "https://doi.org/10.1051/0004-6361/202348857", "doi": "10.1051/0004-6361/202348857",
        "archive": "https://arxiv.org/e-print/2312.03065",
        "sha": "09ebbff37380c784ba957221a7466cc378dab247cf930ddd5c031aca11d2bd3a",
        "selection": "JWST/NIRSpec PRISM broad-Halpha LRD with a published numerical virial mass",
    },
    "ubler24_zs7_offset_blagn": {
        "survey": "GA-NIFS", "field": "COSMOS", "table": "Table 2",
        "version": "MNRAS 531, 355 (2024); arXiv:2312.03589v2",
        "url": "https://doi.org/10.1093/mnras/stae943", "doi": "10.1093/mnras/stae943",
        "archive": "https://arxiv.org/e-print/2312.03589v2",
        "sha": "830ecf743046d0f848e83e0905972b0a8c16d86ddbb1a92c3e61816057642344",
        "selection": "JWST/NIRSpec IFU spatially offset broad-Hbeta Type-1 AGN in ZS7",
    },
    "maiolino24_gnz11_agn": {
        "survey": "JADES", "field": "GOODS-N", "table": "Published GN-z11 black-hole measurement",
        "version": "Nature 627, 59-63 (2024); arXiv:2305.12492",
        "url": "https://doi.org/10.1038/s41586-024-07052-5", "doi": "10.1038/s41586-024-07052-5",
        "archive": "https://arxiv.org/e-print/2305.12492",
        "sha": "54f9fff8eeb6cd36569fed43520a8de2aefebb393b37f4401a6d8cd8758ee2fe",
        "selection": "JWST/NIRSpec dense high-ionization and broad permitted-line evidence for accretion in GN-z11",
    },
}


def _identifier(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", value.upper()).strip("-")


def _first_published(record: dict[str, object], *fields: str) -> object:
    for field in fields:
        value = record.get(field)
        if pd.notna(value):
            return value
    return np.nan


def build_additions(raw: pd.DataFrame, template_columns: list[str]) -> pd.DataFrame:
    """Translate compact source-native rows into the canonical admission schema."""
    rows: list[dict[str, object]] = []
    for record in raw.to_dict("records"):
        source_key = str(record["source_key"])
        meta = SOURCE_METADATA[source_key]
        object_id = str(record["object_id"])
        line = record.get("broad_line_species")
        is_gnz11 = source_key == "maiolino24_gnz11_agn"
        is_lensed = source_key in {"greene24_uncover_blagn", "fei26_glimpse_blagn"}
        method_line = str(line).lower() if pd.notna(line) else "uv-permitted-lines"
        mass_group = "virial_uv_single_epoch" if is_gnz11 else "virial_balmer_single_epoch"
        selection_channels = "high_ionization_line;broad_uv_line" if is_gnz11 else (
            "broad_hbeta" if line == "Hbeta" else "broad_halpha"
        )
        physical_id = f"HZA-{_identifier(object_id)}"
        row = {column: np.nan for column in template_columns}
        row.update({
            "catalogue_release": "complete-catalogue",
            "measurement_id": record["measurement_id"], "object_id": object_id,
            "physical_object_id": physical_id, "host_system_id": f"HZS-{_identifier(object_id)}",
            "ra_deg": record["ra_deg"], "dec_deg": record["dec_deg"],
            "redshift": record["redshift"], "redshift_kind": "spec",
            "cosmic_time_gyr": float(cosmic_time_gyr(record["redshift"])),
            "survey": meta["survey"], "field": meta["field"],
            "object_class": "high_ionization_line_candidate" if is_gnz11 else "broad_line_agn",
            "log_mbh_msun_std": record["log_mbh_msun"],
            "log_mbh_err_plus_std": record["log_mbh_err_plus"],
            "log_mbh_err_minus_std": record["log_mbh_err_minus"],
            "log_mbh_err_plus": record["log_mbh_err_plus"],
            "log_mbh_err_minus": record["log_mbh_err_minus"],
            "mbh_method": f"single-epoch-virial-{method_line}",
            "detection_evidence": "individual_robust" if not is_gnz11 else "multi_diagnostic_spectroscopic",
            "mbh_interpretation_tag": f"single-epoch-virial-{method_line}",
            "quality_flag": "robust" if not is_gnz11 else "probable",
            "source_key": source_key, "source_table": meta["table"],
            "source_paper_version": meta["version"], "source_url": meta["url"],
            "source_doi": meta["doi"], "source_archive_url": meta["archive"],
            "source_archive_sha256": meta["sha"], "extraction_date": "2026-09-03",
            "selection_criteria": meta["selection"], "source_caveat_tags": "canonical_numeric_mass_only",
            "program": meta["survey"], "selection_channel": selection_channels.replace(";", "+"),
            "broad_line_species": line if pd.notna(line) else "UV permitted lines",
            "halpha_broad_fwhm_km_s": record.get("broad_fwhm_km_s") if line == "Halpha" else np.nan,
            "lrd_flag": True if source_key in {"greene24_uncover_blagn", "kocevski25_lrd_blagn", "killi24_j0647_lrd_blagn"} else np.nan,
            "lrd_definition": "source-classified compact red/LRD sample" if source_key in {"greene24_uncover_blagn", "kocevski25_lrd_blagn", "killi24_j0647_lrd_blagn"} else "not reported",
            "log_mbh_systematic_dex": (
                0.3 if source_key == "fei26_glimpse_blagn" else
                0.5 if source_key in {
                    "baccus26_nirspec_blagn", "kocevski25_lrd_blagn",
                    "skyfire26_ceers_blagn", "killi24_j0647_lrd_blagn",
                } else np.nan
            ),
            "mbh_systematic_kind": "single-epoch virial calibration scatter" if source_key in {
                "baccus26_nirspec_blagn", "fei26_glimpse_blagn",
                "kocevski25_lrd_blagn", "skyfire26_ceers_blagn",
                "killi24_j0647_lrd_blagn",
            } else "",
            "mbh_systematic_applied_flag": False,
            "mbh_formal_uncertainty_kind": "published measurement uncertainty",
            "mbh_statistical_uncertainty_kind": "published measurement uncertainty",
            "evidence_status": _first_published(record, "evidence_status") if pd.notna(record.get("evidence_status")) else ("probable" if is_gnz11 else "secure"),
            "evidence_status_basis": _first_published(record, "evidence_status_basis") if pd.notna(record.get("evidence_status_basis")) else ("published multi-diagnostic accreting-black-hole interpretation" if is_gnz11 else "published broad-line AGN identification"),
            "spectroscopic_type": "intermediate_or_ambiguous" if is_gnz11 else ("type1_broad_line_candidate" if record.get("evidence_status") == "candidate" else "type1_broad_line"),
            "selection_channels": selection_channels,
            "phenotype_tags": "compact" if is_gnz11 else ("merger;dual_nucleus" if source_key == "ubler24_zs7_offset_blagn" else ("lrd;compact;red" if source_key in {"greene24_uncover_blagn", "kocevski25_lrd_blagn", "killi24_j0647_lrd_blagn"} else "")),
            "lensing_status": "lensed" if is_lensed else "not_reported",
            "lensing_mu": record.get("lensing_mu") if is_lensed else np.nan,
            "lensing_mass_correction_status": "applied" if is_lensed else "not_required",
            "lensing_provenance": (
                "GLIMPSE source magnification; broad-Halpha flux and virial mass are demagnified"
                if source_key == "fei26_glimpse_blagn" else
                "UNCOVER v1.1 strong-lensing model; mass is demagnified" if is_lensed else ""
            ),
            "mass_comparability_group": mass_group,
            "conditional_mass_flag": False, "conditional_mass_reason": "",
            "primary_mass_comparison_flag": not is_gnz11,
            "primary_mass_comparison_reason": "uv_single_epoch_secondary_stratum" if is_gnz11 else "balmer_single_epoch_primary_stratum",
            "host_property_scope": "object_specific" if pd.notna(record.get("log_mstar_msun")) else "not_published",
            "identity_resolution_status": "resolved", "extraction_date_status": "recorded",
            "host_system_assignment_status": "source_verified_single_object_host",
            "preferred_measurement_flag": True,
            "preferred_measurement_reason": "only admitted measurement for this newly added physical object",
            "match_method": "coordinate-redshift audit against existing catalogue",
            "match_reference": "no existing object within 0.5 arcsec at consistent redshift",
            "published_aliases": "COSMOS13679;COSY-0237620370" if object_id == "ZS7" else "",
        })
        if pd.notna(record.get("log_mstar_msun")):
            row["log_mstar_msun_std"] = record["log_mstar_msun"]
            row["log_mstar_err_plus_std"] = _first_published(record, "log_mstar_err_plus", "log_mstar_err")
            row["log_mstar_err_minus_std"] = _first_published(record, "log_mstar_err_minus", "log_mstar_err")
            row["log_mstar_err_plus"] = _first_published(record, "log_mstar_err_plus", "log_mstar_err")
            row["log_mstar_err_minus"] = _first_published(record, "log_mstar_err_minus", "log_mstar_err")
            row["mstar_method"] = record.get("mstar_method", "")
            row["mstar_interpretation_tag"] = "source_reported_host_stellar_mass"
        if pd.notna(record.get("log_lbol_erg_s")):
            row["log_lbol_erg_s_std"] = record["log_lbol_erg_s"]
            row["log_lbol_err_plus_std"] = record.get("log_lbol_err_plus")
            row["log_lbol_err_minus_std"] = record.get("log_lbol_err_minus")
            row["log_lbol_err_plus"] = record.get("log_lbol_err_plus")
            row["log_lbol_err_minus"] = record.get("log_lbol_err_minus")
            row["lbol_method"] = record.get("lbol_method", "")
            row["lbol_interpretation_tag"] = "source_reported_bolometric_luminosity"
        if pd.notna(record.get("edd_ratio_reported")):
            row["edd_ratio_std"] = record["edd_ratio_reported"]
            row["edd_ratio_err_std"] = _first_published(record, "edd_ratio_err_plus", "edd_ratio_err")
            row["log_edd_ratio_published"] = np.log10(record["edd_ratio_reported"])
            row["edd_ratio_method"] = record.get("edd_ratio_method", "source_reported")
        row["missing_mstar_flag"] = pd.isna(row["log_mstar_msun_std"])
        row["missing_lbol_flag"] = pd.isna(row["log_lbol_erg_s_std"])
        row["missing_edd_ratio_flag"] = pd.isna(row["edd_ratio_std"])
        row["missing_lensing_flag"] = not is_lensed
        rows.append(row)
    additions = pd.DataFrame(rows, columns=template_columns)
    for column in (
        "growth_ranking_eligible_flag", "growth_ranking_eligibility_reason",
        "primary_growth_ranking_flag", "primary_growth_ranking_reason",
    ):
        if column in additions:
            additions[column] = additions[column].astype("object")
        else:
            additions[column] = pd.Series([None] * len(additions), dtype="object")
    additions = _set_eligibility(additions)
    validate_v7_admission(additions)
    return additions


def build_addition_observables(raw: pd.DataFrame) -> pd.DataFrame:
    """Preserve the compact additions' published values in long form."""
    rows: list[dict[str, object]] = []

    def add(record: dict[str, object], name: str, field: str, unit: str,
            *, err_plus: str | None = None, err_minus: str | None = None) -> None:
        value = record.get(field)
        if pd.isna(value):
            return
        plus = record.get(err_plus) if err_plus else np.nan
        minus = record.get(err_minus) if err_minus else np.nan
        has_errors = pd.notna(plus) and pd.notna(minus)
        uncertainty_kind = "not_published"
        if has_errors:
            uncertainty_kind = (
                "published_symmetric_1sigma"
                if np.isclose(float(plus), float(minus)) else "published_asymmetric"
            )
        rows.append({
            "observable_id": f"{record['measurement_id']}__{name}",
            "measurement_id": record["measurement_id"],
            "object_id": record["object_id"],
            "observable_name": name,
            "value": value,
            "err_plus": plus,
            "err_minus": minus,
            "censoring": "detection",
            "unit": unit,
            "uncertainty_kind": uncertainty_kind,
            "source_location": SOURCE_METADATA[str(record["source_key"])]["table"],
        })

    for record in raw.to_dict("records"):
        add(record, "log_mbh", "log_mbh_msun", "log10(Msun)",
            err_plus="log_mbh_err_plus", err_minus="log_mbh_err_minus")
        line = record.get("broad_line_species")
        if pd.notna(line):
            add(record, f"{str(line).lower()}_broad_fwhm", "broad_fwhm_km_s", "km/s",
                err_plus="broad_fwhm_err_plus", err_minus="broad_fwhm_err_minus")
        add(record, "log_mstar", "log_mstar_msun", "log10(Msun)",
            err_plus=("log_mstar_err_plus" if pd.notna(record.get("log_mstar_err_plus")) else "log_mstar_err"),
            err_minus=("log_mstar_err_minus" if pd.notna(record.get("log_mstar_err_minus")) else "log_mstar_err"))
        add(record, "log_lbol", "log_lbol_erg_s", "log10(erg/s)",
            err_plus="log_lbol_err_plus", err_minus="log_lbol_err_minus")
        add(record, "edd_ratio", "edd_ratio_reported", "dimensionless",
            err_plus=("edd_ratio_err_plus" if pd.notna(record.get("edd_ratio_err_plus")) else "edd_ratio_err"),
            err_minus=("edd_ratio_err_minus" if pd.notna(record.get("edd_ratio_err_minus")) else "edd_ratio_err"))
        add(record, "lensing_mu", "lensing_mu", "dimensionless")
    result = pd.DataFrame(rows)
    validate_v7_observables(result, raw["measurement_id"])
    return result


def append_additions(complete: dict[str, pd.DataFrame], raw: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Append additions and rebuild identity-derived complete-catalogue tables."""
    measurements = complete["measurements"].copy()
    additions = build_additions(raw, list(measurements.columns))
    if set(additions["physical_object_id"]) & set(measurements["physical_object_id"]):
        raise ValueError("Canonical-mass additions collide with an existing physical object ID")
    measurements = pd.concat([measurements, additions], ignore_index=True)
    measurements = measurements.sort_values(["source_key", "redshift", "measurement_id"], ascending=[True, False, True]).reset_index(drop=True)
    objects = _aggregate_objects_with_preferred_evidence(measurements)
    hosts = _build_host_systems(measurements, catalogue_release="complete-catalogue")
    links = measurements[["catalogue_release", "measurement_id", "physical_object_id", "host_system_id", "preferred_measurement_flag", "preferred_measurement_reason", "match_method", "match_reference", "identity_resolution_status"]].copy()
    object_host_links = objects[["catalogue_release", "physical_object_id", "host_system_id", "host_system_assignment_status", "host_property_scope"]].copy()
    aliases = complete["aliases"].copy()
    new_aliases = additions[["catalogue_release", "physical_object_id", "host_system_id", "measurement_id", "object_id", "source_key", "ra_deg", "dec_deg", "redshift"]].copy()
    new_aliases["alias_kind"] = "source_object_id"
    aliases = pd.concat([aliases, new_aliases], ignore_index=True)
    strata = _build_strata(measurements, objects, catalogue_release="complete-catalogue")
    observables = complete["observables"].copy()
    observable_additions = build_addition_observables(raw)
    observable_additions.insert(0, "catalogue_release", "complete-catalogue")
    observables = pd.concat([observables, observable_additions], ignore_index=True, sort=False)
    validate_v7_observables(observables, measurements["measurement_id"])
    result = dict(complete)
    result.update({"measurements": measurements, "objects": objects, "host_systems": hosts, "measurement_object_links": links, "object_host_links": object_host_links, "aliases": aliases, "observables": observables, "strata": strata})
    return result
