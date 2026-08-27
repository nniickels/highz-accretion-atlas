"""Build the v7.5 provenance and object-evidence-policy catalogue layer."""

from __future__ import annotations

import pandas as pd

from src.v7_admission import validate_v7_admission, validate_v7_observables
from src.v7_catalogue import _aggregate_objects, _build_host_systems, _build_strata, _set_eligibility
from src.v7_4_scholtz import (
    SOURCE_KEY,
    build_scholtz_admission,
    build_scholtz_observables,
    validate_full_table_selection,
    validate_scholtz_99671_correction,
)


CATALOGUE_RELEASE = "v7.5-accreting-atlas-catalogue"
OBJECT_EVIDENCE_POLICY = (
    "preferred_measurement_controls_object_status;all_measurement_statuses_retained"
)


def _aggregate_objects_with_preferred_evidence(measurements: pd.DataFrame) -> pd.DataFrame:
    """Keep all evidence history without letting weaker alternates downgrade objects."""
    objects = _aggregate_objects(measurements)
    preferred = (
        measurements[measurements["preferred_measurement_flag"].astype(bool)]
        .set_index("physical_object_id")
    )
    if len(preferred) != measurements["physical_object_id"].nunique():
        raise ValueError("v7.5 requires exactly one preferred measurement per object")
    objects["evidence_status"] = objects["physical_object_id"].map(preferred["evidence_status"])
    objects["evidence_status_basis"] = objects["physical_object_id"].map(
        preferred["evidence_status_basis"]
    )
    status_history = measurements.groupby("physical_object_id")["evidence_status"].agg(
        lambda values: ";".join(dict.fromkeys(values.astype(str)))
    )
    basis_history = measurements.groupby("physical_object_id")["evidence_status_basis"].agg(
        lambda values: ";".join(dict.fromkeys(values.astype(str)))
    )
    objects["all_measurement_evidence_statuses"] = objects["physical_object_id"].map(status_history)
    objects["all_measurement_evidence_status_bases"] = objects["physical_object_id"].map(basis_history)
    objects["object_evidence_aggregation_policy"] = OBJECT_EVIDENCE_POLICY
    objects = _set_eligibility(objects)
    validate_v7_admission(objects)
    return objects


def build_v7_5_catalogues(
    v7_4_measurements: pd.DataFrame,
    v7_4_observables: pd.DataFrame,
    v7_4_aliases: pd.DataFrame,
    v7_4_reviewed_candidates: pd.DataFrame,
    scholtz_admitted: pd.DataFrame,
    scholtz_correction: pd.DataFrame,
    scholtz_full_table_path: str,
) -> dict[str, pd.DataFrame]:
    """Correct source membership and apply the preferred-measurement evidence policy."""
    complete_scholtz = pd.concat(
        [scholtz_admitted, scholtz_correction], ignore_index=True,
    )
    validate_full_table_selection(scholtz_full_table_path, complete_scholtz)
    correction = build_scholtz_admission(
        scholtz_correction,
        template_columns=list(v7_4_measurements.columns),
        reserved_ids=set(v7_4_measurements["physical_object_id"]),
        source_validator=validate_scholtz_99671_correction,
        catalogue_release=CATALOGUE_RELEASE,
        project_version="v7.5",
    )
    measurements = pd.concat(
        [v7_4_measurements, correction.dropna(axis=1, how="all")], ignore_index=True,
    )
    measurements["catalogue_release"] = CATALOGUE_RELEASE
    measurements = measurements.sort_values(
        ["source_key", "redshift", "measurement_id"], ascending=[True, False, True],
    ).reset_index(drop=True)
    validate_v7_admission(measurements)
    objects = _aggregate_objects_with_preferred_evidence(measurements).sort_values(
        ["source_key", "redshift", "physical_object_id"], ascending=[True, False, True],
    ).reset_index(drop=True)
    hosts = _build_host_systems(measurements, catalogue_release=CATALOGUE_RELEASE)

    links = measurements[[
        "catalogue_release", "measurement_id", "physical_object_id", "host_system_id",
        "preferred_measurement_flag", "preferred_measurement_reason", "match_method",
        "match_reference", "identity_resolution_status",
    ]].copy().sort_values("measurement_id").reset_index(drop=True)
    object_host_links = objects[[
        "catalogue_release", "physical_object_id", "host_system_id",
        "host_system_assignment_status", "host_property_scope",
    ]].copy().sort_values("physical_object_id").reset_index(drop=True)
    aliases = v7_4_aliases.copy()
    aliases["catalogue_release"] = CATALOGUE_RELEASE
    correction_alias = correction[[
        "catalogue_release", "physical_object_id", "host_system_id", "measurement_id",
        "object_id", "source_key", "ra_deg", "dec_deg", "redshift",
    ]].copy()
    correction_alias["alias_kind"] = "source_object_id"
    aliases = pd.concat([aliases, correction_alias], ignore_index=True).sort_values(
        ["physical_object_id", "measurement_id"],
    ).reset_index(drop=True)
    correction_observables = build_scholtz_observables(
        scholtz_correction, source_validator=validate_scholtz_99671_correction,
    )
    correction_observables.insert(0, "catalogue_release", CATALOGUE_RELEASE)
    observables = pd.concat([v7_4_observables, correction_observables], ignore_index=True)
    observables["catalogue_release"] = CATALOGUE_RELEASE
    validate_v7_observables(observables, measurements["measurement_id"])
    candidates = v7_4_reviewed_candidates.copy()
    candidates["catalogue_release"] = CATALOGUE_RELEASE
    strata = _build_strata(measurements, objects, catalogue_release=CATALOGUE_RELEASE)

    if (len(measurements), len(objects), len(hosts)) != (234, 219, 218):
        raise ValueError("v7.5 cardinality changed unexpectedly")
    jades8083 = objects[objects["physical_object_id"].eq("HZA-GS-8083")].iloc[0]
    if jades8083["evidence_status"] != "secure" or not bool(
        jades8083["primary_growth_ranking_flag"]
    ):
        raise ValueError("v7.5 preferred-evidence policy failed for JADES 8083")
    if objects["primary_growth_ranking_flag"].sum() != 171:
        raise ValueError("v7.5 primary object count must be 171")
    if set(measurements.loc[measurements["source_key"].eq(SOURCE_KEY), "object_id"]) != set(
        complete_scholtz["object_id"]
    ):
        raise ValueError("v7.5 Scholtz catalogue membership changed")
    return {
        "measurements": measurements,
        "objects": objects,
        "host_systems": hosts,
        "measurement_object_links": links,
        "object_host_links": object_host_links,
        "aliases": aliases,
        "reviewed_match_candidates": candidates,
        "observables": observables,
        "strata": strata,
    }
