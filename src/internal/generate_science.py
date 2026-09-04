"""Generate the same complete science suite for v1, v2, and v3."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.datasets import DATASET_SPECS
from src.science import DEFAULT_N_SAMPLES, DEFAULT_RANDOM_SEED, build_outputs


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("versions", nargs="*", choices=DATASET_SPECS)
    parser.add_argument("--n-samples", type=int, default=DEFAULT_N_SAMPLES)
    parser.add_argument("--seed", type=int, default=DEFAULT_RANDOM_SEED)
    args = parser.parse_args()
    versions = args.versions or list(DATASET_SPECS)
    for version in versions:
        base = ROOT / "data/processed" / version
        measurements = pd.read_csv(
            base / f"{version}_accreting_measurements.csv", low_memory=False,
        )
        objects = pd.read_csv(base / f"{version}_accreting_objects.csv", low_memory=False)
        outputs = build_outputs(
            version, measurements, objects,
            n_samples=args.n_samples, random_seed=args.seed,
        )
        if version == "v3":
            from src.internal.assess_baccus_revision import build_revision_outputs
            outputs.update(build_revision_outputs(objects, n_samples=args.n_samples, random_seed=args.seed))
        destination = ROOT / "results" / version / "tables"
        destination.mkdir(parents=True, exist_ok=True)
        for name, frame in outputs.items():
            path = destination / f"{version}_{name}.csv"
            frame.to_csv(path, index=False)
            print(f"Wrote {len(frame):4d} rows: {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
