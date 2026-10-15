# Results

This folder contains growth calculations and figures derived from the
[catalogue](../data/README.md). Publication samples and the four-target v4
analysis have separate output folders.

## Catalogue outputs

Each of `v1/`, `v2/`, and `v3/` has this structure:

```text
results/<version>/
├── figures/                    summary plots and combined object galleries
├── tables/                     growth rates, uncertainties, rankings, and audits
└── parameter_maps/
    ├── fedd_mass_maps/          Eddington ratio versus seed mass
    └── seedredshift_mass_maps/  starting redshift versus seed mass
```

v1 and v2 have numerical growth products for all 23 and 211 objects,
respectively. v3 has 237 objects with eligible numerical masses and 101 without.
Its 676 parameter-map panels include one of each map type for every stored
object. Panels without a usable mass state why no growth calculation is made.
The three open identity groups make the v3 object count provisional; see the
[identity audit](../docs/source-notes/redshift-identity-audit.md).

## v3 figures

| Figure | Purpose |
| --- | --- |
| `v3_all_object_growth_tracks.png` | Selected growth tracks and adopted object masses. |
| `v3_compatibility_summary.png` | Compatibility with the specified growth scenarios. |
| `v3_monte_carlo_summary.png` | Mass-error sampling results. |
| `v3_uncertainty_robustness_top5.png` | Uncertainty comparisons for five selected targets. |
| `v3_all_object_fedd_mass_map_gallery.png` | Combined Eddington-ratio/seed-mass maps. |
| `v3_all_object_compatibility_atlas.png` | Combined growth-compatibility panels. |
| `v3_all_object_monte_carlo_uncertainty.png` | Combined mass-error results. |

These files are in `v3/figures/`. Numerical tables and individual maps are in
the adjacent folders. The underlying object table is
[`v3_accreting_objects.csv`](../data/processed/v3/v3_accreting_objects.csv);
companion tables retain 350 measurements, 810 reported observables, and 337 hosts.

## Full-assumption growth figures

`v3_all_object_growth_tracks_full_assumptions.png` retains all 72 parameter
combinations and the original curve and object-colour conventions. Its
`_zseed3400.png` companion changes only the starting redshift from 30 to 3400.
Both use the same axes and the matter-plus-Lambda cosmic-age approximation,
which neglects radiation. They illustrate available growth time, not a
seed-formation model. Curves outside the plotted mass range are clipped.

All combined growth-track figures show observed redshifts from 13 down to 3.
Individual growth-track panels are omitted. Notebook 03 generates these figures;
see the [notebook sequence](../scripts/README.md) and
[reproduction guide](../docs/guides/reproducibility.md) for the complete procedure.

## Other analyses

- [Manuscript results](for_manuscript/README.md): tables and figures for the
  220-object primary and 234-object expanded samples.
- [v4 outputs](v4/README.md): minimum seed masses, starting-time tests, and
  specified growth scenarios for four selected targets.

`results_inventory.csv` records generated files, sizes, and hashes. Follow the
reproduction guide before updating it or changing reviewed outputs.
