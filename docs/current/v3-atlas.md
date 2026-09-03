# v3 catalogue and visual atlas

v3 is one complete scientific dataset, analysis, and visual product. Its
catalogue combines every source family admitted to the v3 data model; there
are no v3 sub-versions or separate final-data aliases.

## Canonical processed data

Start with `data/processed/v3/v3_accreting_objects.csv`. It contains
one preferred row for each of 174 unique physical objects. Companion files hold
all 183 measurements, 183 source-native observables, 173 host systems, and the
catalogue strata. These are the canonical v3 files.

## Paper-ready summary figures

1. `v3_all_object_growth_tracks.png` — all 153 numerical objects plus the
   redshift locations of all 21 catalogue-only objects.
2. `v3_all_object_growth_tracks_full_assumptions.png` — the same v3 objects
   against all 72 historical v1 reference curves: three seed masses crossed
   with three $f_{Edd}$ values, four constant efficiencies, and two merger boosts.
   Seed mass uses color, $f_{Edd}$ uses line style, efficiency uses line width,
   and merger boost uses opacity, matching the pre-contrast companion design.
3. `v3_compatibility_summary.png` — all 153 computable objects summarized
   by class, seed family, spin, merger boost, and accretion rate.
4. `v3_monte_carlo_summary.png` — all 153 numerical posteriors plus an
   explicit accounting of the other 21 catalogue objects.
5. `v3_uncertainty_robustness_top5.png` — a presentation-ready crop showing
   the five objects with the strongest uncertainty-aware growth pressure.

The existing catalogue landscape, class-aware pressure, and alternate-
measurement sensitivity figures remain valid supporting main-text figures
because they are calculated from the same v3 catalogue.

All combined growth-track figures use a common reversed observed-redshift axis
from 10 to 3. Figure dimensions and subplot margins are unchanged, placing the
observed catalogue points more centrally without changing any data or model.
In the overview growth-track figures, broad-line AGN are purple. The
full-assumption companion retains its historical curve encodings. In its
no-mass lower panel, narrow-line candidates are blue and the X-ray candidate is
gray.

## Complete supplement figures

- `v3_all_object_fedd_mass_map_gallery.png`: all 174 $f_{Edd}$-mass panels.
- `v3_all_object_compatibility_atlas.png`: object-by-object compatibility
  across all supported scenarios.
- `v3_all_object_monte_carlo_uncertainty.png`: every object label and every
  supported 16th--84th percentile interval.
- `results/v3/parameter_maps/fedd_mass_maps/`: one $f_{Edd}$-mass map per object.
- `results/v3/parameter_maps/seedredshift_mass_maps/`: one seed-redshift-mass map per object.

The parameter-map directories therefore contain 348 canonical per-object panels. Numerical
seed-redshift-mass maps solve for the lifetime-average Eddington fraction over seed
mass and seed redshift using the baseline efficiency and merger assumptions;
objects without a supported mass receive the same explicit no-inference
treatment as the $f_{Edd}$-mass maps. Growth tracks are provided only in
combined all-object figures, never as individual parameter-map panels.

For the 21 objects without a supported canonical numerical black-hole mass,
the visual atlas uses explicit no-inference panels. It does not invent masses,
posteriors, compatibility classifications, or growth histories.

Regenerate and verify with:

```bash
mkdir -p /tmp/highz-atlas-notebooks
.venv/bin/jupyter nbconvert --to notebook --execute --output-dir=/tmp/highz-atlas-notebooks scripts/03_generate_atlas.ipynb
.venv/bin/jupyter nbconvert --to notebook --execute --output-dir=/tmp/highz-atlas-notebooks scripts/04_verify.ipynb
```
