"""Verify the immutable v7.2 class-aware science release without writing files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from scripts.generate_v7_2_class_aware_science import OUTPUT_PATHS, build_outputs
from scripts.release_verification import (
    relative_artifact_paths, require_clean_worktree, verify_artifact_manifest,
)
from scripts.reproduction import assert_csv_reproduction
from src.v7_2_catalogue import CATALOGUE_RELEASE
from src.v7_2_science import DEFAULT_N_SAMPLES, DEFAULT_RANDOM_SEED, SCIENCE_RELEASE


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "releases/v7.2-science-manifest.json"
EXPECTED_COUNTS = {
    "measurement_point_ranking": 209,
    "physical_object_point_ranking": 196,
    "measurement_uncertainty_ranking": 209,
    "physical_object_uncertainty_ranking": 196,
    "class_method_summary": 36,
    "exclusion_audit": 4,
    "alternate_measurement_sensitivity": 13,
    "science_policy": 4,
}


def expected_artifact_paths() -> set[str]:
    return relative_artifact_paths(ROOT, OUTPUT_PATHS.values())


def observed_counts() -> dict[str, int]:
    return {
        "measurement_point_ranking": len(pd.read_csv(OUTPUT_PATHS["measurement_point_ranking"])),
        "physical_object_point_ranking": len(pd.read_csv(OUTPUT_PATHS["object_point_ranking"])),
        "measurement_uncertainty_ranking": len(pd.read_csv(OUTPUT_PATHS["measurement_uncertainty_ranking"])),
        "physical_object_uncertainty_ranking": len(pd.read_csv(OUTPUT_PATHS["object_uncertainty_ranking"])),
        "class_method_summary": len(pd.read_csv(OUTPUT_PATHS["class_method_summary"])),
        "exclusion_audit": len(pd.read_csv(OUTPUT_PATHS["exclusion_audit"])),
        "alternate_measurement_sensitivity": len(pd.read_csv(OUTPUT_PATHS["alternate_measurement_sensitivity"])),
        "science_policy": len(pd.read_csv(OUTPUT_PATHS["science_policy"])),
    }


def verify_manifest_metadata(manifest: dict[str, object]) -> None:
    expected = {
        "science_release": SCIENCE_RELEASE,
        "input_catalogue_release": CATALOGUE_RELEASE,
        "python": "3.12",
        "random_seed": DEFAULT_RANDOM_SEED,
        "n_samples": DEFAULT_N_SAMPLES,
        "product_counts": EXPECTED_COUNTS,
    }
    observed = {key: manifest.get(key) for key in expected}
    if observed != expected:
        raise AssertionError(
            f"v7.2 science manifest metadata mismatch; expected={expected}, observed={observed}"
        )
    if observed_counts() != EXPECTED_COUNTS:
        raise AssertionError(
            f"v7.2 science checked-in counts mismatch; expected={EXPECTED_COUNTS}, "
            f"observed={observed_counts()}"
        )


def verify_manifest(manifest: dict[str, object]) -> None:
    verify_artifact_manifest(
        root=ROOT, artifacts=manifest.get("artifacts"),
        expected_paths=expected_artifact_paths(), release_label="v7.2 science",
    )


def verify_reproduction() -> None:
    outputs = build_outputs(
        n_samples=DEFAULT_N_SAMPLES, random_seed=DEFAULT_RANDOM_SEED,
    )
    for name, frame in outputs.items():
        assert_csv_reproduction(OUTPUT_PATHS[name], frame)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reproduce", action="store_true")
    parser.add_argument("--require-clean", action="store_true")
    args = parser.parse_args()
    if args.require_clean:
        require_clean_worktree(ROOT, "v7.2 science")
    manifest = json.loads(MANIFEST_PATH.read_text())
    verify_manifest_metadata(manifest)
    verify_manifest(manifest)
    if args.reproduce:
        verify_reproduction()
    if args.require_clean:
        require_clean_worktree(ROOT, "v7.2 science")
    mode = "hashes and in-memory reproduction" if args.reproduce else "artifact hashes"
    print(f"Verified {manifest['science_release']} {mode}; no artifact was written")


if __name__ == "__main__":
    main()
