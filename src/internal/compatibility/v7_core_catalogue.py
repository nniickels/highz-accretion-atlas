"""Build the non-breaking, catalogue-only v7 heterogeneous atlas layer."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.identity import CANDIDATE_COLUMNS
from src.internal.compatibility.v7_batch import SourceAdmissionBundle, assemble_source_family_batch
from src.internal.compatibility.v7_admission import (
    GROWTH_ELIGIBLE_REASON,
    PRIMARY_ELIGIBLE_REASON,
    expected_growth_eligibility_reason,
    expected_primary_eligibility_reason,
    normalize_v7_vocabulary,
    validate_v7_admission,
    validate_v7_observables,
)
from src.internal.compatibility.v7_ren import build_ren_admission, build_ren_observables


CATALOGUE_RELEASE = "v7-accreting-atlas-catalogue"
JADES_SOURCE_KEY = "juodzbalis25_jades_blagn"
JADES_SOURCE_URL = "https://arxiv.org/abs/2504.03551"
JADES_PAPER_VERSION = "MNRAS 546, stag086 (2026); arXiv:2504.03551"
JADES_SELECTION = "JADES spectroscopic Type 1 broad-line AGN sample"
EVIDENCE_PRIORITY = {"secure": 0, "probable": 1, "candidate": 2, "disputed": 3}


def _nonempty(value: object) -> bool:
    return not pd.isna(value) and bool(str(value).strip())


def _host_id(physical_object_id: str) -> str:
    if not str(physical_object_id).startswith("HZA-"):
        raise ValueError(f"Cannot derive inherited host ID from {physical_object_id}")
    return "HZS-" + str(physical_object_id)[4:]


def _jades_field(object_id: object) -> str:
    token = str(object_id).upper()
    if token.startswith("GN-"):
        return "GOODS-N"
    if token.startswith("GS-"):
        return "GOODS-S"
    raise ValueError(f"Unexpected JADES object identifier: {object_id}")


def _set_eligibility(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    for index, row in result.iterrows():
        growth_reason = expected_growth_eligibility_reason(row)
        growth = growth_reason == GROWTH_ELIGIBLE_REASON
        primary_reason = expected_primary_eligibility_reason(row, growth)
        result.loc[index, "growth_ranking_eligible_flag"] = growth
        result.loc[index, "growth_ranking_eligibility_reason"] = growth_reason
        result.loc[index, "primary_growth_ranking_flag"] = (
            primary_reason == PRIMARY_ELIGIBLE_REASON
        )
        result.loc[index, "primary_growth_ranking_reason"] = primary_reason
    return result


def adapt_v6_measurements(v6: pd.DataFrame) -> pd.DataFrame:
    """Copy frozen v6 rows into the v7 contract without changing v6 files."""
    required = {
        "measurement_id", "object_id", "physical_object_id", "source_key",
        "preferred_measurement_flag", "preferred_measurement_reason",
    }
    if missing := sorted(required - set(v6.columns)):
        raise ValueError(f"v6 measurements missing columns: {missing}")
    result = normalize_v7_vocabulary(v6)
    result["catalogue_release"] = CATALOGUE_RELEASE
    result["host_system_id"] = result["physical_object_id"].map(_host_id)
    result["host_system_assignment_status"] = (
        "inherited_provisional_one_to_one_no_verified_multinucleus_link"
    )
    result["identity_resolution_status"] = "resolved"
    result["extraction_date_status"] = "recorded"

    jades = result["source_key"].eq(JADES_SOURCE_KEY)
    result.loc[jades, "field"] = result.loc[jades, "object_id"].map(_jades_field)
    result.loc[jades, "source_paper_version"] = JADES_PAPER_VERSION
    result.loc[jades, "source_url"] = JADES_SOURCE_URL
    result.loc[jades, "source_doi"] = ""
    result.loc[jades, "source_archive_url"] = JADES_SOURCE_URL
    result.loc[jades, "extraction_date"] = "not_recorded_in_frozen_v1_source_layer"
    result.loc[jades, "extraction_date_status"] = "not_recorded"
    result.loc[jades, "selection_criteria"] = JADES_SELECTION
    result.loc[
        jades & pd.to_numeric(result["edd_ratio_std"], errors="coerce").notna(),
        "edd_ratio_method",
    ] = "source_derived_from_same_lbol_and_virial_mbh"

    harikane = result["source_key"].eq("harikane23_nirspec_blagn")
    result.loc[
        harikane & pd.to_numeric(result["edd_ratio_std"], errors="coerce").notna(),
        "edd_ratio_method",
    ] = "source_derived_from_same_lbol_and_virial_mbh"

    result["source_caveat_tags"] = result["source_caveat_tags"].fillna("")
    result["selection_channels"] = result["selection_channels"].fillna("broad_balmer_line")
    result["phenotype_tags"] = result["phenotype_tags"].fillna("")
    result["lensing_status"] = "not_reported"
    result["lensing_mu"] = np.nan
    result["lensing_mass_correction_status"] = "not_required"
    result["lensing_provenance"] = ""
    result["log_mbh_err_plus"] = result["log_mbh_err_plus_std"]
    result["log_mbh_err_minus"] = result["log_mbh_err_minus_std"]
    result["log_mstar_err_plus"] = result["log_mstar_err_plus_std"]
    result["log_mstar_err_minus"] = result["log_mstar_err_minus_std"]
    result["log_lbol_err_plus"] = result["log_lbol_err_plus_std"]
    result["log_lbol_err_minus"] = result["log_lbol_err_minus_std"]
    result["mbh_statistical_uncertainty_kind"] = result[
        "mbh_formal_uncertainty_kind"
    ].fillna("published_asymmetric_table_uncertainty_semantics_not_further_specified_in_v1")
    result["mbh_systematic_applied_flag"] = False
    jades_halpha = jades & result["mbh_method"].eq("single-epoch-virial-halpha")
    result.loc[jades_halpha, "log_mbh_systematic_dex"] = 0.3
    result.loc[jades_halpha, "mbh_systematic_kind"] = (
        "source_stated_single_epoch_virial_calibration_uncertainty"
    )
    result["mass_comparability_group"] = "virial_balmer_single_epoch"
    candidate = result["evidence_status"].eq("candidate")
    result["conditional_mass_flag"] = candidate
    result["conditional_mass_reason"] = np.where(
        candidate, "mass_valid_only_if_broad_component_is_blr", "",
    )
    result["primary_mass_comparison_flag"] = True
    result["primary_mass_comparison_reason"] = "balmer_single_epoch_primary_stratum"
    result["log_mstar_upper_limit_msun"] = result["log_mstar_upper_limit_msun"]
    has_host = (
        pd.to_numeric(result["log_mstar_msun_std"], errors="coerce").notna()
        | pd.to_numeric(result["log_mstar_upper_limit_msun"], errors="coerce").notna()
    )
    result["host_property_scope"] = np.where(has_host, "object_specific", "not_published")
    result = _set_eligibility(result)
    validate_v7_admission(result)
    return result


def _aggregate_objects(measurements: pd.DataFrame) -> pd.DataFrame:
    grouped = measurements.groupby("physical_object_id", sort=False)
    aggregate = grouped.agg(
        n_measurements=("measurement_id", "size"),
        available_measurement_ids=("measurement_id", lambda x: ";".join(x.astype(str))),
        available_object_ids=("object_id", lambda x: ";".join(x.astype(str))),
        available_source_keys=("source_key", lambda x: ";".join(dict.fromkeys(x.astype(str)))),
    ).reset_index()
    priority = measurements["evidence_status"].map(EVIDENCE_PRIORITY)
    worst = priority.groupby(measurements["physical_object_id"]).max()
    status = worst.map({value: key for key, value in EVIDENCE_PRIORITY.items()})
    evidence_rows = measurements[priority.eq(measurements["physical_object_id"].map(worst))]
    bases = evidence_rows.groupby("physical_object_id")["evidence_status_basis"].agg(
        lambda x: ";".join(dict.fromkeys(x.astype(str)))
    )
    phenotypes = grouped["phenotype_tags"].agg(
        lambda values: ";".join(dict.fromkeys(
            tag for value in values.dropna().astype(str)
            for tag in value.split(";") if tag
        ))
    )
    lrd_known = grouped["lrd_flag"].agg(lambda x: x.notna().any())
    lrd_any = grouped["lrd_flag"].agg(
        lambda x: any(pd.notna(value) and bool(value) for value in x)
    )
    objects = measurements[measurements["preferred_measurement_flag"].astype(bool)].copy()
    if len(objects) != measurements["physical_object_id"].nunique():
        raise ValueError("v7 requires exactly one preferred measurement per physical object")
    objects = objects.merge(aggregate, on="physical_object_id", validate="one_to_one")
    objects["evidence_status"] = objects["physical_object_id"].map(status)
    objects["evidence_status_basis"] = objects["physical_object_id"].map(bases)
    objects["phenotype_tags"] = objects["physical_object_id"].map(phenotypes).fillna("")
    objects["lrd_flag"] = objects["physical_object_id"].map(
        lambda physical_id: bool(lrd_any.loc[physical_id]) if lrd_known.loc[physical_id] else np.nan
    )
    objects = _set_eligibility(objects)
    return objects


def _build_host_systems(
    measurements: pd.DataFrame,
    *,
    catalogue_release: str = CATALOGUE_RELEASE,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for host_system_id, group in measurements.groupby("host_system_id", sort=True):
        physical_ids = list(dict.fromkeys(group["physical_object_id"].astype(str)))
        measurement_ids = list(group["measurement_id"].astype(str))
        source_keys = list(dict.fromkeys(group["source_key"].astype(str)))
        scopes = set(group["host_property_scope"].astype(str))
        shared = "shared_host_system_total" in scopes
        host_values = pd.to_numeric(group["log_mstar_msun_std"], errors="coerce").dropna().unique()
        host_limits = pd.to_numeric(group["log_mstar_upper_limit_msun"], errors="coerce").dropna().unique()
        rows.append({
            "catalogue_release": catalogue_release,
            "host_system_id": host_system_id,
            "n_physical_objects": len(physical_ids),
            "n_measurements": len(measurement_ids),
            "physical_object_ids": ";".join(physical_ids),
            "measurement_ids": ";".join(measurement_ids),
            "source_keys": ";".join(source_keys),
            "host_system_assignment_status": (
                "source_verified_multinucleus_host" if len(physical_ids) > 1
                else "inherited_or_source_verified_single_object_host"
            ),
            "host_property_scope": "shared_host_system_total" if shared else (
                "object_specific" if "object_specific" in scopes else "not_published"
            ),
            "log_mstar_msun_std": host_values[0] if shared and len(host_values) == 1 else np.nan,
            "log_mstar_upper_limit_msun": host_limits[0] if shared and len(host_limits) == 1 else np.nan,
            "host_mass_note": (
                "published integrated system value; do not assign independently to each nucleus"
                if shared else "no cross-object host quantity asserted at host-system level"
            ),
        })
    return pd.DataFrame(rows)


def _build_strata(
    measurements: pd.DataFrame,
    objects: pd.DataFrame,
    *,
    catalogue_release: str = CATALOGUE_RELEASE,
) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for level, frame in [("measurement", measurements), ("physical_object", objects)]:
        dimensions = {
            "all": pd.Series("all", index=frame.index),
            "source_key": frame["source_key"],
            "survey": frame["survey"],
            "field": frame["field"],
            "evidence_status": frame["evidence_status"],
            "object_class": frame["object_class"],
            "lrd_phenotype": frame["lrd_flag"].map(
                lambda x: "not_reported" if pd.isna(x) else ("lrd" if bool(x) else "not_lrd")
            ),
        }
        for dimension, values in dimensions.items():
            for value, indexes in values.groupby(values, dropna=False).groups.items():
                subset = frame.loc[indexes]
                records.append({
                    "catalogue_release": catalogue_release,
                    "entity_level": level,
                    "stratum_dimension": dimension,
                    "stratum_value": value,
                    "count": len(subset),
                    "growth_eligible_count": int(subset["growth_ranking_eligible_flag"].astype(bool).sum()),
                    "primary_eligible_count": int(subset["primary_growth_ranking_flag"].astype(bool).sum()),
                })
    return pd.DataFrame(records).sort_values(
        ["entity_level", "stratum_dimension", "stratum_value"]
    ).reset_index(drop=True)


def build_v7_base_catalogues(
    v6_measurements: pd.DataFrame,
    ren_table1: pd.DataFrame,
    ren_table2: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Return catalogue-only v7 products; no science ranking is generated."""
    inherited = adapt_v6_measurements(v6_measurements)
    ren = build_ren_admission(ren_table1)
    ren["catalogue_release"] = CATALOGUE_RELEASE
    ren["extraction_date_status"] = "recorded"
    ren["host_system_assignment_status"] = np.where(
        ren["host_system_id"].eq("HZS-DC-848185"),
        "source_verified_multinucleus_host", "source_verified_single_object_host",
    )
    ren["preferred_measurement_flag"] = True
    ren["preferred_measurement_reason"] = "only catalogue measurement for this physical object"
    ren["match_method"] = "singleton assignment after coordinate-redshift search"
    ren["match_reference"] = "no v6 candidate within 0.5 arcsec and delta-z 0.01"
    validate_v7_admission(ren)

    ren_observables = build_ren_observables(
        ren_table2, ren[["measurement_id", "object_id"]],
    )
    batch = assemble_source_family_batch(
        inherited,
        [SourceAdmissionBundle(
            source_key=ren["source_key"].iloc[0],
            evidence_family="host_selected_broad_halpha_candidates",
            measurements=ren,
            observables=ren_observables,
        )],
    )
    measurements = batch.measurements
    candidates = batch.identity_candidates
    if len(measurements) != 119 or measurements["physical_object_id"].nunique() != 112:
        raise ValueError("v7 must contain 119 measurements and 112 physical objects")
    preferred = measurements.groupby("physical_object_id")["preferred_measurement_flag"].sum()
    if not preferred.eq(1).all():
        raise ValueError("v7 must retain one preferred measurement per physical object")
    measurements = measurements.sort_values(
        ["source_key", "redshift", "measurement_id"], ascending=[True, False, True]
    ).reset_index(drop=True)
    objects = _aggregate_objects(measurements).sort_values(
        ["source_key", "redshift", "physical_object_id"], ascending=[True, False, True]
    ).reset_index(drop=True)
    validate_v7_admission(objects)
    hosts = _build_host_systems(measurements)
    if len(objects) != 112 or len(hosts) != 111:
        raise ValueError("v7 must contain 112 objects and 111 host systems")

    links = measurements[[
        "catalogue_release", "measurement_id", "physical_object_id", "host_system_id",
        "preferred_measurement_flag", "preferred_measurement_reason", "match_method",
        "match_reference", "identity_resolution_status",
    ]].copy().sort_values("measurement_id").reset_index(drop=True)
    object_host_links = objects[[
        "catalogue_release", "physical_object_id", "host_system_id",
        "host_system_assignment_status", "host_property_scope",
    ]].copy().sort_values("physical_object_id").reset_index(drop=True)
    aliases = measurements[[
        "catalogue_release", "physical_object_id", "host_system_id", "measurement_id",
        "object_id", "source_key", "ra_deg", "dec_deg", "redshift",
    ]].copy()
    aliases["alias_kind"] = "source_object_id"
    aliases = aliases.sort_values(["physical_object_id", "measurement_id"]).reset_index(drop=True)
    observables = batch.observables.copy()
    observables.insert(0, "catalogue_release", CATALOGUE_RELEASE)
    validate_v7_observables(observables, ren["measurement_id"])
    strata = _build_strata(measurements, objects)
    return {
        "measurements": measurements,
        "objects": objects,
        "host_systems": hosts,
        "measurement_object_links": links,
        "object_host_links": object_host_links,
        "aliases": aliases,
        "reviewed_match_candidates": candidates.reindex(columns=CANDIDATE_COLUMNS),
        "observables": observables,
        "strata": strata,
    }
