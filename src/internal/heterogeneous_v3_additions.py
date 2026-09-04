"""Admission adapter for the JWST-identified heterogeneous v3 expansion.

These sources broaden the evidence census but do not supply an unconditional
black-hole mass suitable for the catalogue's growth calculations.  Published
proxy, upper-limit, and assumed-Eddington masses are retained as observables.
"""

from __future__ import annotations

import re

import numpy as np
import pandas as pd

from src.models import cosmic_time_gyr
from src.internal.compatibility.v7_admission import validate_v7_admission, validate_v7_observables
from src.internal.compatibility.v7_catalogue import _aggregate_objects_with_preferred_evidence
from src.internal.compatibility.v7_core_catalogue import _build_host_systems, _build_strata, _set_eligibility


SOURCE_METADATA = {
    "treiber25_uncover_uv_emitters": ("ApJ 984, 93 (2025); arXiv:2409.12232v2", "https://doi.org/10.3847/1538-4357/adc38f", "10.3847/1538-4357/adc38f", "https://arxiv.org/e-print/2409.12232v2", "6b7b99e05ecf1e96b979c75b558d9c7208ba9f270698f4ee51c85d7a1b3b4d31"),
    "naidu26_mom_bhstar1": ("Nature 656, 329-333 (2026)", "https://doi.org/10.1038/s41586-026-10846-4", "10.1038/s41586-026-10846-4", "https://www.nature.com/articles/s41586-026-10846-4.pdf", "6145f8339ed2723fb2a1f2f068e8c5e429d54cdec3790d2702f791094eb4807c"),
    "chisholm24_gn42437_nev": ("MNRAS (2024); arXiv:2402.18643v1", "https://doi.org/10.1093/mnras/stae2199", "10.1093/mnras/stae2199", "https://arxiv.org/e-print/2402.18643v1", "ab98563fce8a805b69cee20b9f4e96bdb138e7028126cb2f4c09da3d0ce1d088"),
    "tang25_high_ionization": ("arXiv:2505.06359v2", "https://arxiv.org/abs/2505.06359v2", "10.48550/arXiv.2505.06359", "https://arxiv.org/e-print/2505.06359v2", "e983d2c0ebbba4a152af847de1331ce5adc1ae7d9653abffa2a4f5dfeb689b07"),
    "mazzolari24_ceers_nlagn": ("A&A 691, A338 (2024); arXiv:2408.15615v3", "https://arxiv.org/abs/2408.15615v3", "10.1051/0004-6361/202451860", "https://arxiv.org/e-print/2408.15615v3", "d0da56ea146d2caef47e37377c90bfe4ea27b6a72d91b6736b9592d80a48487c"),
    "meow26_miri_agn": ("arXiv:2607.02666v1", "https://arxiv.org/abs/2607.02666v1", "10.48550/arXiv.2607.02666", "https://arxiv.org/e-print/2607.02666v1", "9d1ac3b960b74594929da14c89f2a85737f508ff5e083ea6828b14cab36264b5"),
    "lyu24_smiles_miri_agn": ("ApJ 966, 229 (2024); arXiv:2310.12330v2", "https://doi.org/10.3847/1538-4357/ad3643", "10.3847/1538-4357/ad3643", "https://arxiv.org/e-print/2310.12330v2", "16d34d68edd1fbea66bd9c00938e440edac4d0c3606f49ccab1c9cca43da9d5d"),
    "napolitano25_ghz9": ("ApJ (2025); arXiv:2410.18763", "https://doi.org/10.3847/1538-4357/ade706", "10.3847/1538-4357/ade706", "https://arxiv.org/e-print/2410.18763", "744860e9ed4a4c9b25f00ccae1df29adf79546bf16b9d01694435901e99d6691"),
    "zhang25_narrow_line_lrds": ("arXiv:2506.04350v2", "https://arxiv.org/abs/2506.04350v2", "10.48550/arXiv.2506.04350", "https://arxiv.org/e-print/2506.04350v2", "003009915954c6eba18f137092bef56e5e4180c48ec5ba40b9a111dd74f0594b"),
    "chavezortiz26_ghz2": ("arXiv:2511.03035v2", "https://arxiv.org/abs/2511.03035v2", "10.48550/arXiv.2511.03035", "https://arxiv.org/e-print/2511.03035v2", "1e8def5725a3639afb6ba15e1f4e8b8b95e28f36501b7a974595f9f0b5c87c4a"),
    "mascia26_compact_blue_ble": ("arXiv:2608.25021v1", "https://arxiv.org/abs/2608.25021v1", "10.48550/arXiv.2608.25021", "https://arxiv.org/e-print/2608.25021v1", "0e63fcb489cfea4bc1bcf2a4dc6f39cb7be9fa202800ecd227203adaa8058c01"),
}


def _identifier(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", value.upper()).strip("-")


def build_additions(raw: pd.DataFrame, template_columns: list[str]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for record in raw.to_dict("records"):
        version, url, doi, archive, sha = SOURCE_METADATA[str(record["source_key"])]
        ident = _identifier(str(record["object_id"]))
        row = {column: np.nan for column in template_columns}
        row.update({
            "catalogue_release": "complete-catalogue",
            "measurement_id": record["measurement_id"], "object_id": record["object_id"],
            "physical_object_id": f"HZA-{ident}", "host_system_id": f"HZS-{ident}",
            "ra_deg": record.get("ra_deg"), "dec_deg": record.get("dec_deg"),
            "redshift": record["redshift"], "redshift_kind": record["redshift_kind"],
            "cosmic_time_gyr": float(cosmic_time_gyr(record["redshift"])),
            "survey": record["survey"], "program": record["survey"], "field": record["field"],
            "object_class": record["object_class"], "evidence_status": record["evidence_status"],
            "evidence_status_basis": record["evidence_status_basis"],
            "spectroscopic_type": record["spectroscopic_type"],
            "selection_channels": record["selection_channels"],
            "selection_channel": str(record["selection_channels"]).replace(";", "+"),
            "phenotype_tags": record.get("phenotype_tags", ""),
            "source_key": record["source_key"], "source_table": record["source_table"],
            "source_paper_version": version, "source_url": url, "source_doi": doi,
            "source_archive_url": archive, "source_archive_sha256": sha,
            "extraction_date": "2026-09-03", "extraction_date_status": "recorded",
            "selection_criteria": record["selection_criteria"],
            "source_caveat_tags": record["source_caveat_tags"],
            "detection_evidence": record["evidence_status_basis"],
            "quality_flag": record["evidence_status"],
            "lensing_status": record.get("lensing_status", "not_reported"),
            "lensing_mu": record.get("lensing_mu"),
            "lensing_mass_correction_status": record.get("lensing_mass_correction_status", "not_required"),
            "lensing_provenance": record.get("lensing_provenance", ""),
            "mbh_method": "", "mass_comparability_group": "no_numeric_mass",
            # Context-only proxy masses live in the observable table.  The
            # canonical mass fields are empty, so this canonical flag is false.
            "conditional_mass_flag": False, "conditional_mass_reason": "",
            "mbh_systematic_applied_flag": False,
            "primary_mass_comparison_flag": False,
            "primary_mass_comparison_reason": "no_unconditional_canonical_numeric_mass",
            "host_property_scope": "object_specific" if pd.notna(record.get("log_mstar")) else "not_published",
            "identity_resolution_status": "resolved",
            "host_system_assignment_status": "source_verified_single_object_host",
            "preferred_measurement_flag": True,
            "preferred_measurement_reason": "only admitted measurement for this newly added physical object",
            "match_method": "source-ID and coordinate/redshift audit",
            "match_reference": "no previously admitted physical object after explicit alias exclusions",
            "published_aliases": record.get("published_aliases", ""),
            "missing_mstar_flag": pd.isna(record.get("log_mstar")),
            "missing_lbol_flag": pd.isna(record.get("log_lbol")),
            "missing_edd_ratio_flag": True, "missing_lensing_flag": pd.isna(record.get("lensing_mu")),
        })
        if pd.notna(record.get("log_mstar")):
            row.update({"log_mstar_msun_std": record["log_mstar"], "mstar_method": record.get("mstar_method", "source_reported_sed_fit"), "mstar_interpretation_tag": "source_reported_host_stellar_mass"})
        if pd.notna(record.get("log_lbol")):
            row.update({"log_lbol_erg_s_std": record["log_lbol"], "lbol_method": record.get("lbol_method", "source_reported_bolometric_luminosity"), "lbol_interpretation_tag": "source_reported_bolometric_luminosity"})
        rows.append(row)
    additions = pd.DataFrame(rows, columns=template_columns)
    for column in ("growth_ranking_eligible_flag", "growth_ranking_eligibility_reason", "primary_growth_ranking_flag", "primary_growth_ranking_reason"):
        additions[column] = additions[column].astype("object")
    additions = _set_eligibility(additions)
    validate_v7_admission(additions)
    return additions


OBSERVABLES = {
    "log_mstar": ("log_mstar", "log10(Msun)", "detection"),
    "log_lbol": ("log_lbol", "log10(erg/s)", "detection"),
    "agn_fraction": ("agn_fraction", "dimensionless", "detection"),
    "log_mbh_context_low": ("log_mbh_context_low", "log10(Msun)", "lower_limit"),
    "log_mbh_context_high": ("log_mbh_context_high", "log10(Msun)", "upper_limit"),
    "log_mbh_context": ("log_mbh_context", "log10(Msun)", "detection"),
    "log_mbh_upper_limit": ("log_mbh_upper_limit", "log10(Msun)", "upper_limit"),
    "beta_uv": ("beta_uv", "dimensionless", "detection"),
    "beta_opt": ("beta_opt", "dimensionless", "detection"),
}


def build_observables(raw: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for record in raw.to_dict("records"):
        for field, (name, unit, censoring) in OBSERVABLES.items():
            if field not in record or pd.isna(record[field]):
                continue
            rows.append({"observable_id": f"{record['measurement_id']}__{name}", "measurement_id": record["measurement_id"], "object_id": record["object_id"], "observable_name": name, "value": record[field], "err_plus": np.nan, "err_minus": np.nan, "censoring": censoring, "unit": unit, "uncertainty_kind": "limit" if censoring != "detection" else "not_published", "source_location": record["source_table"]})
    result = pd.DataFrame(rows)
    validate_v7_observables(result, raw["measurement_id"])
    return result


def append_heterogeneous_v3(complete: dict[str, pd.DataFrame], raw: pd.DataFrame) -> dict[str, pd.DataFrame]:
    measurements = complete["measurements"].copy()
    additions = build_additions(raw, list(measurements.columns))
    collision = set(additions["physical_object_id"]) & set(measurements["physical_object_id"])
    if collision:
        raise ValueError(f"Heterogeneous additions collide with existing objects: {sorted(collision)}")
    measurements = pd.concat([measurements, additions], ignore_index=True).sort_values(["source_key", "redshift", "measurement_id"], ascending=[True, False, True]).reset_index(drop=True)
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
    result = dict(complete)
    result.update({"measurements": measurements, "objects": objects, "host_systems": hosts, "measurement_object_links": links, "object_host_links": object_host_links, "aliases": aliases, "observables": observables, "strata": _build_strata(measurements, objects, catalogue_release="complete-catalogue")})
    return result
