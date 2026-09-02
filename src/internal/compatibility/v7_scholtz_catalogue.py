"""Build the immutable catalogue-only v7 JADES narrow-line extension."""

from __future__ import annotations

import pandas as pd

from src.identity import CANDIDATE_COLUMNS
from src.internal.compatibility.v7_admission import validate_v7_admission, validate_v7_observables
from src.internal.compatibility.v7_batch import SourceAdmissionBundle, assemble_source_family_batch
from src.internal.compatibility.v7_core_catalogue import _aggregate_objects, _build_host_systems, _build_strata
from src.internal.compatibility.v7_scholtz import (
    EVIDENCE_FAMILY, SOURCE_KEY, build_scholtz_admission, build_scholtz_observables,
)


CATALOGUE_RELEASE = "v7-accreting-atlas-catalogue"


def build_v7_scholtz_catalogues(
    v7_measurements: pd.DataFrame,
    v7_observables: pd.DataFrame,
    v7_aliases: pd.DataFrame,
    scholtz_source: pd.DataFrame,
    identity_overrides: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    new = build_scholtz_admission(
        scholtz_source, template_columns=list(v7_measurements.columns),
        reserved_ids=set(v7_measurements["physical_object_id"].astype(str)),
    )
    new_observables = build_scholtz_observables(scholtz_source)
    batch = assemble_source_family_batch(
        v7_measurements.copy(),
        [SourceAdmissionBundle(SOURCE_KEY, EVIDENCE_FAMILY, new, new_observables)],
        identity_overrides=identity_overrides,
    )
    measurements = batch.measurements.copy()
    measurements["catalogue_release"] = CATALOGUE_RELEASE
    preferred = measurements.groupby("physical_object_id")["preferred_measurement_flag"].sum()
    if not preferred.eq(1).all():
        raise ValueError("v7 must retain one preferred measurement per physical object")
    measurements = measurements.sort_values(
        ["source_key", "redshift", "measurement_id"], ascending=[True, False, True],
    ).reset_index(drop=True)
    validate_v7_admission(measurements)
    objects = _aggregate_objects(measurements).sort_values(
        ["source_key", "redshift", "physical_object_id"], ascending=[True, False, True],
    ).reset_index(drop=True)
    validate_v7_admission(objects)
    hosts = _build_host_systems(measurements, catalogue_release=CATALOGUE_RELEASE)
    observed = (len(measurements), len(objects), len(hosts))
    if observed != (233, 218, 217):
        raise ValueError(f"v7 cardinality mismatch: {observed}")

    links = measurements[[
        "catalogue_release", "measurement_id", "physical_object_id", "host_system_id",
        "preferred_measurement_flag", "preferred_measurement_reason", "match_method",
        "match_reference", "identity_resolution_status",
    ]].copy().sort_values("measurement_id").reset_index(drop=True)
    object_host_links = objects[[
        "catalogue_release", "physical_object_id", "host_system_id",
        "host_system_assignment_status", "host_property_scope",
    ]].copy().sort_values("physical_object_id").reset_index(drop=True)

    aliases = v7_aliases.copy()
    aliases["catalogue_release"] = CATALOGUE_RELEASE
    new_aliases = measurements.loc[measurements["source_key"].eq(SOURCE_KEY), [
        "catalogue_release", "physical_object_id", "host_system_id", "measurement_id",
        "object_id", "source_key", "ra_deg", "dec_deg", "redshift",
    ]].copy()
    new_aliases["alias_kind"] = "source_object_id"
    aliases = pd.concat([aliases, new_aliases.reindex(columns=aliases.columns)], ignore_index=True)
    aliases = aliases.sort_values(["physical_object_id", "measurement_id", "alias_kind"]).reset_index(drop=True)

    prior_observables = v7_observables.copy()
    prior_observables["catalogue_release"] = CATALOGUE_RELEASE
    admitted = batch.observables.copy()
    admitted.insert(0, "catalogue_release", CATALOGUE_RELEASE)
    observables = pd.concat([prior_observables, admitted], ignore_index=True, sort=False)
    validate_v7_observables(observables, measurements["measurement_id"])
    strata = _build_strata(measurements, objects, catalogue_release=CATALOGUE_RELEASE)
    candidates = batch.identity_candidates.copy()
    if candidates.empty:
        candidates = candidates.reindex(columns=CANDIDATE_COLUMNS)
    candidates.insert(0, "catalogue_release", CATALOGUE_RELEASE)
    return {
        "measurements": measurements, "objects": objects, "host_systems": hosts,
        "measurement_object_links": links, "object_host_links": object_host_links,
        "aliases": aliases, "reviewed_match_candidates": candidates,
        "observables": observables, "strata": strata,
    }
