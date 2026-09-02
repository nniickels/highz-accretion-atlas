"""Build v1, v2, and v3 with one corrected catalogue pipeline."""

from pathlib import Path
from src.internal.compatibility.build_complete_catalogue import build_outputs as build_complete_catalogue
from src.datasets import DATASET_SPECS, materialize_version

ROOT = Path(__file__).resolve().parents[2]

def output_paths(version: str):
    p, c = ROOT / "data/processed" / version, ROOT / "data/crossmatch" / version
    return {"measurements": p / f"{version}_accreting_measurements.csv", "objects": p / f"{version}_accreting_objects.csv", "host_systems": p / f"{version}_host_systems.csv", "observables": p / f"{version}_source_observables.csv", "strata": p / f"{version}_catalogue_strata.csv", "measurement_object_links": c / f"{version}_measurement_object_links.csv", "object_host_links": c / f"{version}_object_host_links.csv", "aliases": c / f"{version}_object_aliases.csv", "reviewed_match_candidates": c / f"{version}_reviewed_match_candidates.csv", "external_literature_identity_audit": c / f"{version}_external_literature_identity_audit.csv"}

def build_versions():
    complete = build_complete_catalogue()
    return {version: materialize_version(complete, spec) for version, spec in DATASET_SPECS.items()}

def main():
    for version, outputs in build_versions().items():
        for name, frame in outputs.items():
            path = output_paths(version)[name]; path.parent.mkdir(parents=True, exist_ok=True); frame.to_csv(path, index=False)
            print(f"Wrote {len(frame):4d} rows: {path.relative_to(ROOT)}")

if __name__ == "__main__": main()
