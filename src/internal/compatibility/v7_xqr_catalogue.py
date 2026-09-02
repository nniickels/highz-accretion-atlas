"""Build the immutable, catalogue-only v7 XQR-30 extension."""

from __future__ import annotations

import pandas as pd

from src.internal.compatibility.v7_admission import validate_v7_admission, validate_v7_observables
from src.internal.compatibility.v7_batch import SourceAdmissionBundle, assemble_source_family_batch
from src.internal.compatibility.v7_core_catalogue import _aggregate_objects, _build_host_systems, _build_strata
from src.internal.compatibility.v7_xqr30 import SOURCE_KEY, build_xqr30_admission, build_xqr30_observables


CATALOGUE_RELEASE = "v7-accreting-atlas-catalogue"
EVIDENCE_FAMILY = "luminous_quasar_comparison"
EXTERNAL_AUDIT_FIELDS = {
    "measurement_id", "object_id", "literature_alias", "literature_reference",
    "atlas_prior_candidate_count", "identity_disposition", "review_basis", "review_date",
}


def validate_external_identity_audit(
    audit: pd.DataFrame,
    xqr30_measurements: pd.DataFrame,
) -> None:
    if missing := sorted(EXTERNAL_AUDIT_FIELDS - set(audit.columns)):
        raise ValueError(f"XQR-30 external identity audit missing columns: {missing}")
    if len(audit) != 23 or not audit["measurement_id"].is_unique:
        raise ValueError("XQR-30 external identity audit must contain 23 unique paper repeats")
    expected = set(xqr30_measurements["measurement_id"])
    if unknown := set(audit["measurement_id"]) - expected:
        raise ValueError(f"XQR-30 external identity audit contains unknown measurements: {sorted(unknown)}")
    counts = pd.to_numeric(audit["atlas_prior_candidate_count"], errors="coerce")
    if counts.isna().any() or not counts.eq(0).all():
        raise ValueError("XQR-30 literature repeats must record zero prior-atlas candidates")
    required = ["literature_alias", "literature_reference", "identity_disposition", "review_basis", "review_date"]
    if audit[required].isna().any().any() or audit[required].astype(str).apply(
        lambda column: column.str.strip().eq("")
    ).any().any():
        raise ValueError("XQR-30 external identity audit requires complete review metadata")
    if "XQR30-WISEA-J0439-1634_mazzucchelli23" not in set(audit["measurement_id"]):
        raise ValueError("XQR-30 external identity audit must include the lensed J0439+1634 repeat")


def build_v7_xqr_catalogues(
    v7_measurements: pd.DataFrame,
    v7_observables: pd.DataFrame,
    raw_xqr30: pd.DataFrame,
    xqr30_coordinates: pd.DataFrame,
    identity_overrides: pd.DataFrame,
    external_identity_audit: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Return the v7 products after adding the XQR source family."""
    prior = v7_measurements.copy()
    xqr30 = build_xqr30_admission(raw_xqr30, xqr30_coordinates)
    xqr30["catalogue_release"] = CATALOGUE_RELEASE
    xqr30_observables = build_xqr30_observables(raw_xqr30)
    validate_external_identity_audit(external_identity_audit, xqr30)
    batch = assemble_source_family_batch(
        prior,
        [SourceAdmissionBundle(
            source_key=SOURCE_KEY,
            evidence_family=EVIDENCE_FAMILY,
            measurements=xqr30,
            observables=xqr30_observables,
        )],
        identity_overrides=identity_overrides,
    )
    if not batch.identity_candidates.empty:
        raise ValueError("XQR-30 must have no coordinate/redshift candidate in the v7 atlas")

    measurements = batch.measurements.copy()
    measurements["catalogue_release"] = CATALOGUE_RELEASE
    if len(measurements) != 161 or measurements["physical_object_id"].nunique() != 154:
        raise ValueError("v7 must contain 161 measurements and 154 physical objects")
    preferred = measurements.groupby("physical_object_id")["preferred_measurement_flag"].sum()
    if not preferred.eq(1).all():
        raise ValueError("v7 must retain one preferred measurement per physical object")
    measurements = measurements.sort_values(
        ["source_key", "redshift", "measurement_id"], ascending=[True, False, True]
    ).reset_index(drop=True)
    validate_v7_admission(measurements)
    objects = _aggregate_objects(measurements).sort_values(
        ["source_key", "redshift", "physical_object_id"], ascending=[True, False, True]
    ).reset_index(drop=True)
    validate_v7_admission(objects)
    hosts = _build_host_systems(
        measurements, catalogue_release=CATALOGUE_RELEASE,
    )
    if len(objects) != 154 or len(hosts) != 153:
        raise ValueError("v7 must contain 154 objects and 153 host systems")

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
    table_aliases = raw_xqr30[["measurement_id", "table_alias"]].merge(
        xqr30[["measurement_id", "physical_object_id", "host_system_id", "source_key", "ra_deg", "dec_deg", "redshift"]],
        on="measurement_id", validate="one_to_one",
    ).rename(columns={"table_alias": "object_id"})
    table_aliases.insert(0, "catalogue_release", CATALOGUE_RELEASE)
    table_aliases["alias_kind"] = "mass_table_alias"
    aliases = pd.concat([aliases, table_aliases.reindex(columns=aliases.columns)], ignore_index=True)
    aliases = aliases.sort_values(
        ["physical_object_id", "measurement_id", "alias_kind"]
    ).reset_index(drop=True)

    prior_observables = v7_observables.copy()
    prior_observables["catalogue_release"] = CATALOGUE_RELEASE
    new_observables = batch.observables.copy()
    new_observables.insert(0, "catalogue_release", CATALOGUE_RELEASE)
    observables = pd.concat([prior_observables, new_observables], ignore_index=True, sort=False)
    validate_v7_observables(observables, measurements["measurement_id"])
    strata = _build_strata(
        measurements, objects, catalogue_release=CATALOGUE_RELEASE,
    )
    audit = external_identity_audit.copy().sort_values("measurement_id").reset_index(drop=True)
    audit.insert(0, "catalogue_release", CATALOGUE_RELEASE)
    return {
        "measurements": measurements,
        "objects": objects,
        "host_systems": hosts,
        "measurement_object_links": links,
        "object_host_links": object_host_links,
        "aliases": aliases,
        "reviewed_match_candidates": batch.identity_candidates,
        "external_literature_identity_audit": audit,
        "observables": observables,
        "strata": strata,
    }
