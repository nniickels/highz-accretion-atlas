"""Build the immutable, catalogue-only v7.2 GNIRS-50 extension."""

from __future__ import annotations

import pandas as pd

from src.identity import angular_separation_arcsec
from src.v7_admission import validate_v7_admission, validate_v7_observables
from src.v7_batch import SourceAdmissionBundle, assemble_source_family_batch
from src.v7_catalogue import _aggregate_objects, _build_host_systems, _build_strata
from src.v7_shen19 import SOURCE_KEY, build_shen19_admission, build_shen19_observables


CATALOGUE_RELEASE = "v7.2-accreting-atlas-catalogue"
EVIDENCE_FAMILY = "luminous_quasar_comparison"
EXPECTED_REVIEWED_IDENTITIES = 6


def build_v7_2_catalogues(
    v7_1_measurements: pd.DataFrame,
    v7_1_observables: pd.DataFrame,
    v7_1_aliases: pd.DataFrame,
    sample_table: pd.DataFrame,
    catalog_table: pd.DataFrame,
    identity_overrides: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Return v7.2 products without modifying any frozen earlier artifact."""
    new = build_shen19_admission(sample_table, catalog_table)
    new["catalogue_release"] = CATALOGUE_RELEASE
    new_observables = build_shen19_observables(catalog_table)
    batch = assemble_source_family_batch(
        v7_1_measurements.copy(),
        [SourceAdmissionBundle(
            source_key=SOURCE_KEY,
            evidence_family=EVIDENCE_FAMILY,
            measurements=new,
            observables=new_observables,
        )],
        identity_overrides=identity_overrides,
    )
    if len(batch.identity_candidates) != EXPECTED_REVIEWED_IDENTITIES:
        raise ValueError("v7.2 must preserve six reviewed GNIRS/XQR identity decisions")
    if not batch.identity_candidates["decision"].eq("accepted").all():
        raise ValueError("v7.2 GNIRS/XQR identity decisions must all be accepted")

    measurements = batch.measurements.copy()
    measurements["catalogue_release"] = CATALOGUE_RELEASE
    is_new = measurements["source_key"].eq(SOURCE_KEY)
    repeated_ids = set(
        measurements.loc[is_new, "physical_object_id"]
    ) & set(measurements.loc[~is_new, "physical_object_id"])
    repeated_new = is_new & measurements["physical_object_id"].isin(repeated_ids)
    measurements.loc[repeated_new, "preferred_measurement_flag"] = False
    measurements.loc[repeated_new, "preferred_measurement_reason"] = (
        "v7.1 XQR-30 measurement retained as preferred; GNIRS measurement preserved as alternate"
    )
    measurements.loc[repeated_new, "match_method"] = "reviewed literature identity"
    measurements.loc[repeated_new, "match_reference"] = "v7.2 reviewed identity registry"
    measurements.loc[is_new & ~repeated_new, "preferred_measurement_reason"] = (
        "only atlas measurement for this physical object"
    )
    measurements.loc[is_new & ~repeated_new, "match_method"] = (
        "singleton assignment after coordinate-redshift search"
    )
    measurements.loc[is_new & ~repeated_new, "match_reference"] = (
        "no v7.1 candidate within 0.5 arcsec and delta-z 0.01 and no manual identity assertion"
    )
    preferred = measurements.groupby("physical_object_id")["preferred_measurement_flag"].sum()
    if not preferred.eq(1).all():
        raise ValueError("v7.2 must retain one preferred measurement per physical object")
    measurements = measurements.sort_values(
        ["source_key", "redshift", "measurement_id"], ascending=[True, False, True],
    ).reset_index(drop=True)
    validate_v7_admission(measurements)
    objects = _aggregate_objects(measurements).sort_values(
        ["source_key", "redshift", "physical_object_id"], ascending=[True, False, True],
    ).reset_index(drop=True)
    validate_v7_admission(objects)
    hosts = _build_host_systems(measurements, catalogue_release=CATALOGUE_RELEASE)

    expected = (211, 198, 197)
    observed = (len(measurements), len(objects), len(hosts))
    if observed != expected:
        raise ValueError(f"v7.2 cardinality mismatch: expected {expected}, found {observed}")
    links = measurements[[
        "catalogue_release", "measurement_id", "physical_object_id", "host_system_id",
        "preferred_measurement_flag", "preferred_measurement_reason", "match_method",
        "match_reference", "identity_resolution_status",
    ]].copy().sort_values("measurement_id").reset_index(drop=True)
    object_host_links = objects[[
        "catalogue_release", "physical_object_id", "host_system_id",
        "host_system_assignment_status", "host_property_scope",
    ]].copy().sort_values("physical_object_id").reset_index(drop=True)

    aliases = v7_1_aliases.copy()
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

    prior_observables = v7_1_observables.copy()
    prior_observables["catalogue_release"] = CATALOGUE_RELEASE
    admitted_observables = batch.observables.copy()
    admitted_observables.insert(0, "catalogue_release", CATALOGUE_RELEASE)
    observables = pd.concat([prior_observables, admitted_observables], ignore_index=True, sort=False)
    validate_v7_observables(observables, measurements["measurement_id"])
    strata = _build_strata(measurements, objects, catalogue_release=CATALOGUE_RELEASE)
    candidates = batch.identity_candidates.copy()
    manual = candidates["match_origin"].eq("manual_assertion")
    measurement_lookup = measurements.set_index("measurement_id")
    for index, row in candidates.loc[manual].iterrows():
        new_row = measurement_lookup.loc[row["measurement_id"]]
        prior_row = measurement_lookup.loc[row["candidate_measurement_id"]]
        candidates.loc[index, "candidate_object_id"] = prior_row["object_id"]
        candidates.loc[index, "candidate_physical_object_id"] = prior_row["physical_object_id"]
        candidates.loc[index, "separation_arcsec"] = float(angular_separation_arcsec(
            new_row["ra_deg"], new_row["dec_deg"], prior_row["ra_deg"], prior_row["dec_deg"],
        ))
        candidates.loc[index, "redshift_delta"] = abs(
            float(new_row["redshift"]) - float(prior_row["redshift"])
        )
        candidates.loc[index, "match_scope"] = "prior_release_manual_assertion"
        candidates.loc[index, "candidate_source_key"] = prior_row["source_key"]
    candidates = candidates.sort_values(
        ["measurement_id", "candidate_measurement_id"],
    ).reset_index(drop=True)
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
