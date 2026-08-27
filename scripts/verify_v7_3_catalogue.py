"""Verify the immutable v7.3 UHZ1 catalogue release without writing files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from scripts.process_v7_3_catalogue import OUTPUTS, build_outputs
from scripts.release_verification import (
    relative_artifact_paths, require_clean_worktree, verify_artifact_manifest,
)
from scripts.reproduction import assert_csv_reproduction
from src.v7_3_catalogue import CATALOGUE_RELEASE
from src.v7_3_uhz1 import EXPECTED_ARCHIVES


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "releases/v7.3-catalogue-manifest.json"
EXPECTED_COUNTS = {
    "measurements": 213,
    "physical_objects": 199,
    "host_systems": 198,
    "growth_eligible_measurements": 209,
    "primary_measurements": 182,
    "growth_eligible_physical_objects": 196,
    "primary_physical_objects": 171,
    "measurement_object_links": 213,
    "object_host_links": 199,
    "aliases": 255,
    "reviewed_identity_records": 0,
    "source_observables": 1015,
    "uhz1_measurement_versions": 2,
    "uhz1_physical_objects": 1,
    "uhz1_numeric_masses": 0,
}


def expected_artifact_paths() -> set[str]:
    return relative_artifact_paths(ROOT, OUTPUTS.values())


def observed_catalogue_counts() -> dict[str, int]:
    measurements = pd.read_csv(OUTPUTS["measurements"])
    objects = pd.read_csv(OUTPUTS["objects"])
    uhz1 = measurements["source_key"].eq("uhz1_xray_evidence_history")
    return {
        "measurements": len(measurements),
        "physical_objects": len(objects),
        "host_systems": len(pd.read_csv(OUTPUTS["host_systems"])),
        "growth_eligible_measurements": int(measurements["growth_ranking_eligible_flag"].sum()),
        "primary_measurements": int(measurements["primary_growth_ranking_flag"].sum()),
        "growth_eligible_physical_objects": int(objects["growth_ranking_eligible_flag"].sum()),
        "primary_physical_objects": int(objects["primary_growth_ranking_flag"].sum()),
        "measurement_object_links": len(pd.read_csv(OUTPUTS["measurement_object_links"])),
        "object_host_links": len(pd.read_csv(OUTPUTS["object_host_links"])),
        "aliases": len(pd.read_csv(OUTPUTS["aliases"])),
        "reviewed_identity_records": len(pd.read_csv(OUTPUTS["reviewed_match_candidates"])),
        "source_observables": len(pd.read_csv(OUTPUTS["observables"])),
        "uhz1_measurement_versions": int(uhz1.sum()),
        "uhz1_physical_objects": measurements.loc[uhz1, "physical_object_id"].nunique(),
        "uhz1_numeric_masses": int(measurements.loc[uhz1, "log_mbh_msun_std"].notna().sum()),
    }


def verify_manifest_metadata(manifest: dict[str, object]) -> None:
    expected = {
        "catalogue_release": CATALOGUE_RELEASE,
        "parent_catalogue_release": "v7.2-accreting-atlas-catalogue",
        "python": "3.12",
        "catalogue_counts": EXPECTED_COUNTS,
        "source_archives": EXPECTED_ARCHIVES,
    }
    observed = {key: manifest.get(key) for key in expected}
    if observed != expected:
        raise AssertionError(
            f"v7.3 catalogue manifest metadata mismatch; expected={expected}, observed={observed}"
        )
    actual_counts = observed_catalogue_counts()
    if actual_counts != EXPECTED_COUNTS:
        raise AssertionError(
            f"v7.3 checked-in counts mismatch; expected={EXPECTED_COUNTS}, observed={actual_counts}"
        )


def verify_manifest(manifest: dict[str, object]) -> None:
    verify_artifact_manifest(
        root=ROOT, artifacts=manifest.get("artifacts"),
        expected_paths=expected_artifact_paths(), release_label="v7.3 catalogue",
    )


def verify_reproduction() -> None:
    for name, frame in build_outputs().items():
        assert_csv_reproduction(OUTPUTS[name], frame)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reproduce", action="store_true")
    parser.add_argument("--require-clean", action="store_true")
    args = parser.parse_args()
    if args.require_clean:
        require_clean_worktree(ROOT, "v7.3 catalogue")
    manifest = json.loads(MANIFEST_PATH.read_text())
    verify_manifest_metadata(manifest)
    verify_manifest(manifest)
    if args.reproduce:
        verify_reproduction()
    if args.require_clean:
        require_clean_worktree(ROOT, "v7.3 catalogue")
    mode = "hashes and in-memory reproduction" if args.reproduce else "artifact hashes"
    print(f"Verified {manifest['catalogue_release']} {mode}; no artifact was written")


if __name__ == "__main__":
    main()
