"""Apply explicit source-reviewed duplicate decisions after catalogue assembly."""
from pathlib import Path
import json
import pandas as pd
from src.identity import angular_separation_arcsec
from src.internal.compatibility.v7_catalogue import _aggregate_objects_with_preferred_evidence
from src.internal.compatibility.v7_core_catalogue import _build_host_systems, _build_strata

REGISTRY = Path(__file__).resolve().parents[2] / "data/assembly/reconciled_identity_pairs.json"


def reconcile_identities(complete):
    result = {key: frame.copy() for key, frame in complete.items()}
    measurements = result["measurements"]
    audit = []
    for decision in json.loads(REGISTRY.read_text()):
        selected = []
        for role in ("preferred_measurement_id", "alternate_measurement_id"):
            rows = measurements.loc[measurements.measurement_id.eq(decision[role])]
            if len(rows) != 1:
                raise ValueError("Reviewed identity must identify exactly one measurement")
            selected.append(rows.iloc[0])
        preferred, alternate = selected
        separation = float(angular_separation_arcsec(preferred.ra_deg, preferred.dec_deg,
                                                     alternate.ra_deg, alternate.dec_deg))
        if not separation <= decision["max_separation_arcsec"] or not abs(preferred.redshift-alternate.redshift) <= decision["max_redshift_delta"]:
            raise ValueError("Reviewed duplicate no longer meets source position/redshift bounds")
        if not bool(preferred.growth_ranking_eligible_flag) or bool(alternate.growth_ranking_eligible_flag):
            raise ValueError("Reviewed preference requires a mass-bearing row and a mass-free alternate")
        old_id = alternate.physical_object_id
        if (measurements.physical_object_id.eq(old_id)).sum() != 1:
            raise ValueError("Duplicate group changed; re-review preferred-measurement policy")
        mask = measurements.physical_object_id.eq(old_id)
        measurements.loc[mask, "physical_object_id"] = preferred.physical_object_id
        measurements.loc[mask, "host_system_id"] = preferred.host_system_id
        measurements.loc[mask, "preferred_measurement_flag"] = False
        measurements.loc[mask, "preferred_measurement_reason"] = "source-reviewed duplicate; prefer mass-bearing measurement " + preferred.measurement_id
        measurements.loc[mask, "match_method"] = "explicit source-reviewed coordinate/redshift identity"
        measurements.loc[mask, "match_reference"] = decision["review_reference"]
        for name, frame in result.items():
            if name == "measurements" or "physical_object_id" not in frame:
                continue
            affected = frame.physical_object_id.eq(old_id)
            frame.loc[affected, "physical_object_id"] = preferred.physical_object_id
            if "host_system_id" in frame:
                frame.loc[affected, "host_system_id"] = preferred.host_system_id
        audit.append(dict(catalogue_release=preferred.catalogue_release,
            measurement_id=alternate.measurement_id, object_id=alternate.object_id,
            literature_alias=preferred.object_id, literature_reference=decision["review_reference"],
            atlas_prior_candidate_count=1, identity_disposition="same_physical_object",
            review_basis=decision["review_basis"], review_date=decision["review_date"]))
    result["objects"] = _aggregate_objects_with_preferred_evidence(measurements)
    result["host_systems"] = _build_host_systems(measurements, catalogue_release="complete-catalogue")
    result["strata"] = _build_strata(measurements, result["objects"], catalogue_release="complete-catalogue")
    for name in ("measurement_object_links", "object_host_links"):
        # Public materialization rebuilds these projections from preferred rows.
        source = measurements if name == "measurement_object_links" else result["objects"]
        result[name] = source[result[name].columns].copy()
    result["external_literature_identity_audit"] = pd.concat([
        result["external_literature_identity_audit"], pd.DataFrame(audit)
    ], ignore_index=True)
    return result
