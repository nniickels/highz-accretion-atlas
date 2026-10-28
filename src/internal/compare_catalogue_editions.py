"""Compare stored scientific editions at identical reference growth assumptions.

Run with --baseline-root pointing to an unchanged export of the earlier
revision. This descriptive comparison is separate from artifact reproduction.
"""

import argparse
from pathlib import Path
import pandas as pd
from src import models

ROOT = Path(__file__).resolve().parents[2]


def edition_metrics(root):
    values = {}
    for version in ("v1", "v2", "v3"):
        for table, label in [
            ("accreting_measurements", "measurements"),
            ("accreting_objects", "object_records"),
            ("host_systems", "hosts"),
        ]:
            values[f"{version}.{label}"] = len(
                pd.read_csv(root / f"data/processed/{version}/{version}_{table}.csv")
            )
    for version in ("v2", "v3"):
        objects = pd.read_csv(
            root / f"data/processed/{version}/{version}_accreting_objects.csv"
        )
        values[f"{version}.growth_eligible_objects"] = int(
            objects.growth_ranking_eligible_flag.sum()
        )
        values[f"{version}.method_primary_objects"] = int(
            objects.primary_growth_ranking_flag.sum()
        )
        values[f"{version}.source_families"] = int(objects.source_key.nunique())
    summary = pd.read_csv(
        root / "results/v3/selected_samples/tables/identity_exclusion_sensitivity.csv"
    )
    for row in summary.query(
        'scope == "publication" and scenario == "reference"'
    ).to_dict("records"):
        for field in (
            "n_objects",
            "above_unity",
            "p16_above_unity",
            "probability_ge_095",
            "q25",
            "median",
            "q75",
            "top_five",
        ):
            values[row["sample"] + "." + field] = row[field]
    offsets = pd.read_csv(
        root / "results/v3/selected_samples/tables/mass_offset_sensitivity.csv"
    )
    for r in offsets.itertuples():
        if r.mass_offset_dex in (-0.3, -0.5):
            for field in ("above_unity", "p16_above_unity", "probability_ge_095"):
                values[f"{r.sample}.offset{r.mass_offset_dex}.{field}"] = getattr(
                    r, field
                )
    point = pd.read_csv(root / "results/v3/tables/v3_object_point_ranking.csv")
    selection = pd.read_csv(
        root / "results/v3/selected_samples/tables/publication_object_selection.csv"
    )
    ids = set(
        selection.loc[selection.publication_exploratory_flag, "physical_object_id"]
    )
    point = point.loc[point.physical_object_id.isin(ids)]
    eps = float(models.thin_disk_radiative_efficiency(0))
    f = models.required_fedd_for_seed(
        2, point.log_mbh_msun_std, eps, 30, point.redshift
    )
    values["exploratory.nonspinning_maximum"] = float(max(f))
    values["exploratory.nonspinning_above_unity"] = int((f > 1).sum())
    errors = pd.read_csv(root / "results/v3/tables/v3_object_uncertainty_ranking.csv")
    values["exploratory.no_reported_mass_errors"] = int(
        errors.loc[errors.physical_object_id.isin(ids), "mbh_uncertainty_mode"]
        .eq("point_estimate_no_reported_mbh_error")
        .sum()
    )
    for r in pd.read_csv(root / "results/v4/tables/v4_targets.csv").itertuples():
        values[f"v4.{r.object_id}.reference_required_ratio"] = (
            r.reference_required_fedd_matter_lambda
        )
    return values


def compare(baseline, current=ROOT):
    if baseline.resolve() == current.resolve():
        raise ValueError("Scientific baseline must be independent")
    old, new = edition_metrics(baseline), edition_metrics(current)
    rows = []
    for key in sorted(old.keys() | new.keys()):
        a, b = old.get(key), new.get(key)
        rows.append(
            dict(
                metric=key,
                before=a,
                after=b,
                baseline_revision="fc0c5501ad2271865b1c040307cad8dd8ca5721a",
                reference_assumptions="100 Msun seed; z_seed=30; epsilon=0.1 unless nonspinning; no mergers",
            )
        )
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-root", required=True, type=Path)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "results/catalogue_edition_comparison.csv"
    )
    args = parser.parse_args()
    result = compare(args.baseline_root)
    result.to_csv(args.output, index=False)
    print(result[["metric", "before", "after"]].to_string(index=False))


if __name__ == "__main__":
    main()
