"""Generic source-family batch assembly for heterogeneous catalogue layers.

Source-specific modules remain responsible for extraction, scientific mapping,
and stable identity assignments.  This module supplies the common batch gate:
source isolation, referential integrity, duplicate-ID checks, and candidate
crossmatches against both the prior release and other sources in the batch.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from src.identity import (
    CANDIDATE_COLUMNS,
    apply_reviewed_identity_overrides,
    candidate_matches,
    cross_source_candidate_matches,
)
from src.v7_admission import OBJECT_CLASSES, validate_v7_admission, validate_v7_observables


STANDARD_COMPATIBILITY_ALIASES = {
    "log_mbh_err_plus": "log_mbh_err_plus_std",
    "log_mbh_err_minus": "log_mbh_err_minus_std",
    "log_mstar_err_plus": "log_mstar_err_plus_std",
    "log_mstar_err_minus": "log_mstar_err_minus_std",
    "log_lbol_err_plus": "log_lbol_err_plus_std",
    "log_lbol_err_minus": "log_lbol_err_minus_std",
}
SOURCE_REGISTRY_STATUSES = {
    "selected_pending_source_audit", "extracted", "admitted",
    "released_catalogue_layer",
}
SOURCE_REGISTRY_FIELDS = {
    "batch_id", "evidence_family", "source_key", "status", "admission_module",
    "object_class", "notes",
}


def validate_source_family_registry(registry: pd.DataFrame) -> None:
    """Validate released and planned source-family batch declarations."""
    if missing := sorted(SOURCE_REGISTRY_FIELDS - set(registry.columns)):
        raise ValueError(f"Source-family registry missing columns: {missing}")
    if registry.empty:
        raise ValueError("Source-family registry cannot be empty")
    for field in ["batch_id", "evidence_family", "source_key", "status", "object_class"]:
        if registry[field].isna().any() or registry[field].astype(str).str.strip().eq("").any():
            raise ValueError(f"Source-family registry requires nonblank {field}")
    for field in ["batch_id", "source_key"]:
        if not registry[field].is_unique:
            raise ValueError(f"Source-family registry requires unique {field}")
    if invalid := set(registry["status"]) - SOURCE_REGISTRY_STATUSES:
        raise ValueError(f"Invalid source-family registry statuses: {sorted(invalid)}")
    if invalid := set(registry["object_class"]) - OBJECT_CLASSES:
        raise ValueError(f"Invalid source-family object classes: {sorted(invalid)}")
    implemented = registry["status"].isin({"admitted", "released_catalogue_layer"})
    modules = registry["admission_module"].fillna("").astype(str).str.strip()
    if modules.loc[implemented].eq("").any():
        raise ValueError("Admitted/released sources require an admission_module")


def load_source_family_registry(path: str | Path) -> pd.DataFrame:
    """Load and validate the source-family registry without mutating it."""
    registry = pd.read_csv(path)
    validate_source_family_registry(registry)
    return registry


def validate_standardized_compatibility(measurements: pd.DataFrame) -> None:
    """Require canonical v7 values to agree with retained legacy aliases."""
    required = {
        "project_version", "cosmic_time_gyr", *STANDARD_COMPATIBILITY_ALIASES,
        *STANDARD_COMPATIBILITY_ALIASES.values(),
    }
    if missing := sorted(required - set(measurements.columns)):
        raise ValueError(f"v7 standardized compatibility fields missing: {missing}")
    if measurements["project_version"].isna().any() or (
        measurements["project_version"].astype(str).str.strip().eq("").any()
    ):
        raise ValueError("Every v7 measurement requires a project_version")
    cosmic_time = pd.to_numeric(measurements["cosmic_time_gyr"], errors="coerce")
    if cosmic_time.isna().any() or cosmic_time.le(0).any():
        raise ValueError("Every v7 measurement requires a positive cosmic_time_gyr")
    for canonical, compatibility in STANDARD_COMPATIBILITY_ALIASES.items():
        left = pd.to_numeric(measurements[canonical], errors="coerce").to_numpy()
        right = pd.to_numeric(measurements[compatibility], errors="coerce").to_numpy()
        if not np.allclose(left, right, rtol=0.0, atol=0.0, equal_nan=True):
            raise ValueError(
                f"v7 canonical field {canonical} disagrees with {compatibility}"
            )


@dataclass(frozen=True)
class SourceAdmissionBundle:
    """One independently audited source mapping ready for a family batch."""

    source_key: str
    evidence_family: str
    measurements: pd.DataFrame
    observables: pd.DataFrame | None = None

    def validate(self) -> None:
        if not self.source_key.strip() or not self.evidence_family.strip():
            raise ValueError("Source bundles require nonblank source_key and evidence_family")
        validate_v7_admission(self.measurements)
        validate_standardized_compatibility(self.measurements)
        actual_sources = set(self.measurements["source_key"].astype(str))
        if actual_sources != {self.source_key}:
            raise ValueError(
                f"Source bundle {self.source_key} contains source keys {sorted(actual_sources)}"
            )
        if self.observables is not None:
            validate_v7_observables(
                self.observables, self.measurements["measurement_id"],
            )


@dataclass(frozen=True)
class BatchAssembly:
    """Validated concatenation plus identity candidates requiring review."""

    measurements: pd.DataFrame
    observables: pd.DataFrame
    identity_candidates: pd.DataFrame


def assemble_source_family_batch(
    prior_measurements: pd.DataFrame,
    bundles: list[SourceAdmissionBundle],
    *,
    identity_overrides: pd.DataFrame | None = None,
    require_resolved_identity: bool = True,
) -> BatchAssembly:
    """Combine audited bundles without silently resolving scientific identity.

    Coordinate/redshift matches are review candidates, never automatic links.
    The default release gate therefore stops when any candidate remains.  A
    source adapter or reviewed-identity registry must resolve it before the
    batch can be frozen.
    """
    if not bundles:
        raise ValueError("A source-family batch requires at least one bundle")
    validate_v7_admission(prior_measurements)
    validate_standardized_compatibility(prior_measurements)
    source_keys = [bundle.source_key for bundle in bundles]
    if len(source_keys) != len(set(source_keys)):
        raise ValueError("A source-family batch cannot repeat a source_key")
    families = {bundle.evidence_family for bundle in bundles}
    if len(families) != 1:
        raise ValueError(
            "A source-family batch must contain one coherent evidence family"
        )
    for bundle in bundles:
        bundle.validate()

    new_measurements = pd.concat(
        [bundle.measurements for bundle in bundles], ignore_index=True, sort=False,
    )
    if new_measurements["measurement_id"].duplicated().any():
        raise ValueError("Source-family batch contains duplicate measurement_id values")
    overlap = set(prior_measurements["measurement_id"]) & set(
        new_measurements["measurement_id"]
    )
    if overlap:
        raise ValueError(f"Batch measurement IDs already exist: {sorted(overlap)}")

    candidate_frames = [candidate_matches(new_measurements, prior_measurements)]
    if len(bundles) > 1:
        candidate_frames.append(cross_source_candidate_matches(new_measurements))
    identity_candidates = pd.concat(
        candidate_frames, ignore_index=True,
    ).reindex(columns=CANDIDATE_COLUMNS)
    if identity_overrides is not None:
        identity_candidates, accepted_map = apply_reviewed_identity_overrides(
            identity_candidates,
            identity_overrides,
            known_measurement_ids=pd.concat(
                [prior_measurements["measurement_id"], new_measurements["measurement_id"]],
                ignore_index=True,
            ),
        )
        new_ids = set(new_measurements["measurement_id"].astype(str))
        prior_hosts = (
            prior_measurements[["physical_object_id", "host_system_id"]]
            .drop_duplicates()
            .groupby("physical_object_id")["host_system_id"]
            .agg(lambda values: list(dict.fromkeys(values.astype(str))))
        )
        for measurement_id, physical_object_id in accepted_map.items():
            if measurement_id not in new_ids:
                continue
            mask = new_measurements["measurement_id"].astype(str).eq(measurement_id)
            new_measurements.loc[mask, "physical_object_id"] = physical_object_id
            if physical_object_id in prior_hosts.index:
                hosts = prior_hosts.loc[physical_object_id]
                if len(hosts) != 1:
                    raise ValueError(
                        f"Reviewed identity {physical_object_id} has ambiguous prior host systems"
                    )
                new_measurements.loc[mask, "host_system_id"] = hosts[0]
        validate_v7_admission(new_measurements)
        validate_standardized_compatibility(new_measurements)
    elif require_resolved_identity and not identity_candidates.empty:
        ids = sorted(identity_candidates["measurement_id"].astype(str).unique())
        raise ValueError(f"Source-family batch has unresolved identity candidates: {ids}")

    columns = list(dict.fromkeys([
        *prior_measurements.columns, *new_measurements.columns,
    ]))
    measurements = pd.concat([
        prior_measurements.reindex(columns=columns),
        new_measurements.reindex(columns=columns),
    ], ignore_index=True)
    validate_v7_admission(measurements)
    validate_standardized_compatibility(measurements)

    observable_frames = [
        bundle.observables for bundle in bundles
        if bundle.observables is not None and not bundle.observables.empty
    ]
    observables = (
        pd.concat(observable_frames, ignore_index=True, sort=False)
        if observable_frames else pd.DataFrame()
    )
    if not observables.empty:
        if observables["observable_id"].duplicated().any():
            raise ValueError("Source-family batch contains duplicate observable_id values")
        validate_v7_observables(observables, new_measurements["measurement_id"])
    return BatchAssembly(measurements, observables, identity_candidates)
