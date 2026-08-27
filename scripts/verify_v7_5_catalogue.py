"""Verify the immutable v7.5 provenance-corrected catalogue release."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from scripts.process_v7_5_catalogue import OUTPUTS, build_outputs
from scripts.release_verification import (
    relative_artifact_paths,
    require_clean_worktree,
    verify_artifact_manifest,
)
from scripts.reproduction import assert_csv_reproduction
from src.v7_4_scholtz import EXPECTED_ARCHIVES, SOURCE_KEY
from src.v7_5_catalogue import CATALOGUE_RELEASE, OBJECT_EVIDENCE_POLICY


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "releases/v7.5-catalogue-manifest.json"
EXPECTED_COUNTS = {
    "measurements": 234, "physical_objects": 219, "host_systems": 218,
    "growth_eligible_measurements": 209, "primary_measurements": 182,
    "growth_eligible_physical_objects": 196, "primary_physical_objects": 171,
    "measurement_object_links": 234, "object_host_links": 219, "aliases": 276,
    "reviewed_identity_records": 1, "source_observables": 1106,
    "scholtz_zge4_measurements": 21, "scholtz_physical_objects": 21,
    "scholtz_numeric_masses": 0, "scholtz_tentative_rows": 3,
    "scholtz_high_ionization_fluxes": 7,
}


def expected_artifact_paths() -> set[str]:
    return relative_artifact_paths(ROOT, OUTPUTS.values())


def observed_catalogue_counts() -> dict[str, int]:
    measurements = pd.read_csv(OUTPUTS["measurements"])
    objects = pd.read_csv(OUTPUTS["objects"])
    source = measurements["source_key"].eq(SOURCE_KEY)
    observables = pd.read_csv(OUTPUTS["observables"])
    high = observables["observable_name"].isin(
        {"neiv2424_flux", "nev3427_flux", "nv1240_flux"}
    )
    return {
        "measurements": len(measurements), "physical_objects": len(objects),
        "host_systems": len(pd.read_csv(OUTPUTS["host_systems"])),
        "growth_eligible_measurements": int(measurements["growth_ranking_eligible_flag"].sum()),
        "primary_measurements": int(measurements["primary_growth_ranking_flag"].sum()),
        "growth_eligible_physical_objects": int(objects["growth_ranking_eligible_flag"].sum()),
        "primary_physical_objects": int(objects["primary_growth_ranking_flag"].sum()),
        "measurement_object_links": len(pd.read_csv(OUTPUTS["measurement_object_links"])),
        "object_host_links": len(pd.read_csv(OUTPUTS["object_host_links"])),
        "aliases": len(pd.read_csv(OUTPUTS["aliases"])),
        "reviewed_identity_records": len(pd.read_csv(OUTPUTS["reviewed_match_candidates"])),
        "source_observables": len(observables), "scholtz_zge4_measurements": int(source.sum()),
        "scholtz_physical_objects": measurements.loc[source, "physical_object_id"].nunique(),
        "scholtz_numeric_masses": int(measurements.loc[source, "log_mbh_msun_std"].notna().sum()),
        "scholtz_tentative_rows": int(measurements.loc[source, "quality_flag"].eq("tentative").sum()),
        "scholtz_high_ionization_fluxes": int(high.sum()),
    }


def verify_manifest_metadata(manifest: dict[str, object]) -> None:
    expected = {
        "catalogue_release": CATALOGUE_RELEASE,
        "parent_catalogue_release": "v7.4-accreting-atlas-catalogue",
        "python": "3.12", "catalogue_counts": EXPECTED_COUNTS,
        "source_archives": EXPECTED_ARCHIVES,
        "object_evidence_policy": OBJECT_EVIDENCE_POLICY,
    }
    observed = {key: manifest.get(key) for key in expected}
    if observed != expected:
        raise AssertionError(f"v7.5 catalogue manifest metadata mismatch; expected={expected}, observed={observed}")
    actual = observed_catalogue_counts()
    if actual != EXPECTED_COUNTS:
        raise AssertionError(f"v7.5 checked-in counts mismatch; expected={EXPECTED_COUNTS}, observed={actual}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reproduce", action="store_true")
    parser.add_argument("--require-clean", action="store_true")
    args = parser.parse_args()
    if args.require_clean:
        require_clean_worktree(ROOT, "v7.5 catalogue")
    manifest = json.loads(MANIFEST_PATH.read_text())
    verify_manifest_metadata(manifest)
    verify_artifact_manifest(
        root=ROOT, artifacts=manifest.get("artifacts"),
        expected_paths=expected_artifact_paths(), release_label="v7.5 catalogue",
    )
    if args.reproduce:
        for name, frame in build_outputs().items():
            assert_csv_reproduction(OUTPUTS[name], frame)
    if args.require_clean:
        require_clean_worktree(ROOT, "v7.5 catalogue")
    print(f"Verified {manifest['catalogue_release']} hashes and in-memory reproduction; no artifact was written")


if __name__ == "__main__":
    main()
