# Results

`v1/`, `v2/`, and `v3/` have the same complete structure:

```text
results/<version>/
├── figures/               paper-ready summaries and all-object atlases
├── tables/                rankings, follow-up priorities, uncertainty, compatibility, and audits
└── parameter_maps/
    ├── fedd_mass_maps/             f_Edd versus seed-mass panels for every object
    └── seedredshift_mass_maps/     seed-redshift versus seed-mass panels for every object
```

v1 covers all 23 objects numerically; v2 covers all 211 numerically; v3
represents all 338 object records with 237 numerical products and 101 explicit
no-inference panels. Obsolete software-release result trees are not part of the
public repository contract; necessary assembly logic is isolated under
`src/internal/compatibility/`.

Individual growth-track panels are intentionally omitted. A combined
growth-track overview for each version remains under `figures/`. All combined
growth-track figures use the same observed-redshift range from 13 down to 3,
with their existing figure dimensions and plot margins retained. v3 also has
`v3_all_object_growth_tracks_full_assumptions.png`, which preserves the full
historical v1 curve and object-color encodings as a separate companion figure.
Its seed redshift is 30. The additional
`v3_all_object_growth_tracks_full_assumptions_zseed3400.png` changes only seed
redshift to 3400, preserving all 72 parameter combinations and identical axes.
Both use the adopted matter+Lambda age relation: radiation is neglected, so
the early-seed comparison is an extrapolation, not a physical seed-formation
model. Curves outside the shared mass-axis limits are clipped. Regeneration
through the atlas notebook produces both figures.

## v3 catalogue and atlas

Start with `data/processed/v3/v3_accreting_objects.csv`, which contains one
preferred row for each physical object. Companion files contain all 350
measurements, 810 source-native observables, 337 host systems, and catalogue
strata.

The main summary figures are:

- `v3_all_object_growth_tracks.png`
- `v3_all_object_growth_tracks_full_assumptions.png`
- `v3_all_object_growth_tracks_full_assumptions_zseed3400.png`
- `v3_compatibility_summary.png`
- `v3_monte_carlo_summary.png`
- `v3_uncertainty_robustness_top5.png`

The complete supplements are `v3_all_object_fedd_mass_map_gallery.png`,
`v3_all_object_compatibility_atlas.png`, and
`v3_all_object_monte_carlo_uncertainty.png`. The two parameter-map directories
contain 676 canonical panels, one of each map type for every object. Objects
without a supported canonical numerical black-hole mass receive explicit
no-inference panels; the pipeline does not invent masses or growth histories.

Regenerate and verify the atlas with `scripts/03_generate_atlas.ipynb` and
`scripts/04_verify.ipynb`.

Two source-supported duplicates were merged on 7 September 2026, preserving all
350 measurement rows. Three identity groups remain under review; counts are
provisional until the [identity audit](../docs/source-notes/redshift-identity-audit.md) closes.
