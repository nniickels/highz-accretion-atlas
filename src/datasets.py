"""Materialize dataset versions from the single corrected atlas catalogue."""

from __future__ import annotations

from dataclasses import dataclass
import pandas as pd

from src.internal.compatibility.v7_catalogue import _aggregate_objects_with_preferred_evidence
from src.internal.compatibility.v7_core_catalogue import _build_host_systems, _build_strata
from src.internal.compatibility.v7_admission import (
    validate_v7_admission as validate_admission,
    validate_v7_observables as validate_observables,
)


@dataclass(frozen=True)
class DatasetSpec:
    version: str
    title: str
    source_keys: frozenset[str]
    expected_measurements: int
    expected_objects: int
    expected_hosts: int

    @property
    def catalogue_release(self) -> str:
        return f"{self.version}-dataset-catalogue"


V1_SOURCES = frozenset({"juodzbalis25_jades_blagn"})
V2_SOURCES = V1_SOURCES | frozenset({
    "taylor24_ceers_rubies_blagn", "matthee23_eiger_fresco_blagn",
    "lin24_aspire_blagn", "harikane23_nirspec_blagn",
    "davis26_thrils_blagn", "ren25_alpine_cristal_jwst_blagn_candidates",
    "greene24_uncover_blagn", "kocevski25_lrd_blagn",
    "skyfire26_ceers_blagn", "larson23_ceers1019",
    "killi24_j0647_lrd_blagn", "ubler24_zs7_offset_blagn",
    "baccus26_nirspec_blagn", "fei26_glimpse_blagn",
})
V3_SOURCES = V2_SOURCES | frozenset({
    "uhz1_xray_evidence_history", "scholtz25_jades_narrow_line_agn",
    "maiolino24_gnz11_agn",
    "chisholm24_gn42437_nev", "tang25_high_ionization",
    "mazzolari24_ceers_nlagn", "meow26_miri_agn",
    "lyu24_smiles_miri_agn", "napolitano25_ghz9",
    "zhang25_narrow_line_lrds", "chavezortiz26_ghz2",
    "mascia26_compact_blue_ble",
    "treiber25_uncover_uv_emitters", "naidu26_mom_bhstar1",
})
DATASET_SPECS = {
    "v1": DatasetSpec("v1", "Original JADES BLAGN catalogue", V1_SOURCES, 23, 23, 23),
    "v2": DatasetSpec("v2", "Expanded comparable BLAGN catalogue", V2_SOURCES, 218, 211, 210),
    "v3": DatasetSpec("v3", "JWST-identified heterogeneous accretion atlas", V3_SOURCES, 320, 311, 310),
}


def _scope(frame: pd.DataFrame, field: str, values: set[str]) -> pd.DataFrame:
    return frame[frame[field].astype(str).isin(values)].copy() if field in frame else frame.iloc[0:0].copy()


def materialize_version(complete: dict[str, pd.DataFrame], spec: DatasetSpec) -> dict[str, pd.DataFrame]:
    measurements = complete["measurements"].copy()
    if spec.source_keys:
        measurements = measurements[measurements["source_key"].isin(spec.source_keys)].copy()
    measurements["catalogue_release"] = spec.catalogue_release
    measurements["project_version"] = spec.version
    measurements = measurements.sort_values(["source_key", "redshift", "measurement_id"], ascending=[True, False, True]).reset_index(drop=True)
    validate_admission(measurements)
    objects = _aggregate_objects_with_preferred_evidence(measurements)
    objects["catalogue_release"] = spec.catalogue_release
    objects["project_version"] = spec.version
    objects = objects.sort_values(["source_key", "redshift", "physical_object_id"], ascending=[True, False, True]).reset_index(drop=True)
    hosts = _build_host_systems(measurements, catalogue_release=spec.catalogue_release)
    mids, pids = set(measurements["measurement_id"].astype(str)), set(measurements["physical_object_id"].astype(str))
    observables = _scope(complete["observables"], "measurement_id", mids)
    observables["catalogue_release"] = spec.catalogue_release
    validate_observables(observables, measurements["measurement_id"])
    aliases = _scope(complete["aliases"], "physical_object_id", pids)
    aliases["catalogue_release"] = spec.catalogue_release
    links = measurements[["catalogue_release", "measurement_id", "physical_object_id", "host_system_id", "preferred_measurement_flag", "preferred_measurement_reason", "match_method", "match_reference", "identity_resolution_status"]].copy().sort_values("measurement_id").reset_index(drop=True)
    object_host_links = objects[["catalogue_release", "physical_object_id", "host_system_id", "host_system_assignment_status", "host_property_scope"]].copy().sort_values("physical_object_id").reset_index(drop=True)
    strata = _build_strata(measurements, objects, catalogue_release=spec.catalogue_release)
    reviewed = _scope(complete["reviewed_match_candidates"], "measurement_id", mids)
    if "catalogue_release" in reviewed: reviewed["catalogue_release"] = spec.catalogue_release
    audit = complete["external_literature_identity_audit"].copy()
    if spec.version != "v3": audit = audit.iloc[0:0].copy()
    if "catalogue_release" in audit: audit["catalogue_release"] = spec.catalogue_release
    expected = (spec.expected_measurements, spec.expected_objects, spec.expected_hosts)
    observed = (len(measurements), len(objects), len(hosts))
    if observed != expected: raise ValueError(f"{spec.version} membership changed: {observed} != {expected}")
    if int(measurements["preferred_measurement_flag"].astype(bool).sum()) != len(objects): raise ValueError("one preferred measurement is required per object")
    return {"measurements": measurements, "objects": objects, "host_systems": hosts, "measurement_object_links": links, "object_host_links": object_host_links, "aliases": aliases, "reviewed_match_candidates": reviewed, "external_literature_identity_audit": audit, "observables": observables, "strata": strata}
