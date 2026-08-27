"""Build the immutable catalogue-only v7.3 UHZ1 evidence-history extension."""

from __future__ import annotations

import pandas as pd

from src.identity import CANDIDATE_COLUMNS
from src.v7_admission import validate_v7_admission, validate_v7_observables
from src.v7_batch import SourceAdmissionBundle, assemble_source_family_batch
from src.v7_catalogue import _aggregate_objects, _build_host_systems, _build_strata
from src.v7_3_uhz1 import (
    EVIDENCE_FAMILY, SOURCE_KEY, build_uhz1_admission, build_uhz1_observables,
)


CATALOGUE_RELEASE = "v7.3-accreting-atlas-catalogue"


def build_v7_3_catalogues(
    v7_2_measurements: pd.DataFrame,
    v7_2_observables: pd.DataFrame,
    v7_2_aliases: pd.DataFrame,
    uhz1_history: pd.DataFrame,
    miri_table3: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Append two UHZ1 evidence versions without changing frozen v7.2."""
    new = build_uhz1_admission(
        uhz1_history, miri_table3, template_columns=list(v7_2_measurements.columns),
    )
    observables_new = build_uhz1_observables(uhz1_history, miri_table3)
    batch = assemble_source_family_batch(
        v7_2_measurements.copy(),
        [SourceAdmissionBundle(
            source_key=SOURCE_KEY,
            evidence_family=EVIDENCE_FAMILY,
            measurements=new,
            observables=observables_new,
        )],
    )
    if not batch.identity_candidates.empty:
        raise ValueError("UHZ1 must not silently match a prior-release object")

    measurements = batch.measurements.copy()
    measurements["catalogue_release"] = CATALOGUE_RELEASE
    preferred = measurements.groupby("physical_object_id")["preferred_measurement_flag"].sum()
    if not preferred.eq(1).all():
        raise ValueError("v7.3 must retain one preferred measurement per physical object")
    measurements = measurements.sort_values(
        ["source_key", "redshift", "measurement_id"], ascending=[True, False, True],
    ).reset_index(drop=True)
    validate_v7_admission(measurements)
    objects = _aggregate_objects(measurements).sort_values(
        ["source_key", "redshift", "physical_object_id"], ascending=[True, False, True],
    ).reset_index(drop=True)
    validate_v7_admission(objects)
    hosts = _build_host_systems(measurements, catalogue_release=CATALOGUE_RELEASE)
    expected = (213, 199, 198)
    observed = (len(measurements), len(objects), len(hosts))
    if observed != expected:
        raise ValueError(f"v7.3 cardinality mismatch: expected {expected}, found {observed}")

    links = measurements[[
        "catalogue_release", "measurement_id", "physical_object_id", "host_system_id",
        "preferred_measurement_flag", "preferred_measurement_reason", "match_method",
        "match_reference", "identity_resolution_status",
    ]].copy().sort_values("measurement_id").reset_index(drop=True)
    object_host_links = objects[[
        "catalogue_release", "physical_object_id", "host_system_id",
        "host_system_assignment_status", "host_property_scope",
    ]].copy().sort_values("physical_object_id").reset_index(drop=True)

    aliases = v7_2_aliases.copy()
    aliases["catalogue_release"] = CATALOGUE_RELEASE
    new_aliases = measurements.loc[measurements["source_key"].eq(SOURCE_KEY), [
        "catalogue_release", "physical_object_id", "host_system_id", "measurement_id",
        "object_id", "source_key", "ra_deg", "dec_deg", "redshift",
    ]].copy()
    new_aliases["alias_kind"] = "source_object_id"
    aliases = pd.concat([aliases, new_aliases.reindex(columns=aliases.columns)], ignore_index=True)
    aliases = aliases.sort_values(
        ["physical_object_id", "measurement_id", "alias_kind"],
    ).reset_index(drop=True)

    prior_observables = v7_2_observables.copy()
    prior_observables["catalogue_release"] = CATALOGUE_RELEASE
    admitted_observables = batch.observables.copy()
    admitted_observables.insert(0, "catalogue_release", CATALOGUE_RELEASE)
    observables = pd.concat([prior_observables, admitted_observables], ignore_index=True, sort=False)
    validate_v7_observables(observables, measurements["measurement_id"])
    strata = _build_strata(measurements, objects, catalogue_release=CATALOGUE_RELEASE)
    candidates = batch.identity_candidates.reindex(columns=CANDIDATE_COLUMNS)
    candidates.insert(0, "catalogue_release", CATALOGUE_RELEASE)
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
