# v3 catalogue and visual atlas

v3 is one complete scientific dataset, analysis, and visual product. Its
catalogue combines every source family admitted to the v3 data model; there
are no v3 sub-versions or separate final-data aliases.

## Canonical processed data

Start with `data/processed/v3/v3_accreting_objects.csv`. It contains
one preferred row for each of 219 unique physical objects. Companion files hold
all 234 measurements, 1,106 source-native observables, 218 host systems, and the
catalogue strata. These are the canonical v3 files.

## Paper-ready summary figures

1. `v3_all_object_growth_tracks.png` — all 196 numerical objects plus the
   redshift locations of all 23 catalogue-only objects.
2. `v3_all_object_growth_tracks_full_assumptions.png` — the same v3 objects
   against all 72 historical v1 reference curves: three seed masses crossed
   with three $f_{Edd}$ values, four constant efficiencies, and two merger boosts.
3. `v3_all_object_growth_tracks_full_assumptions_uncertainty_filtered.png` —
   the same 72-curve view after excluding only the four luminous quasars whose
   maximum reported black-hole-mass uncertainty exceeds 0.7 dex. The excluded
   rows and criterion are recorded in `v3_growth_track_uncertainty_filter.csv`.
4. `v3_compatibility_summary.png` — all 196 computable objects summarized
   by class, seed family, spin, merger boost, and accretion rate.
5. `v3_monte_carlo_summary.png` — all 196 numerical posteriors plus an
   explicit accounting of the other 23 catalogue objects.

The existing catalogue landscape, class-aware pressure, and alternate-
measurement sensitivity figures remain valid supporting main-text figures
because they are calculated from the same v3 catalogue.

All combined growth-track figures use a common reversed observed-redshift axis
from 10 to 3. Figure dimensions and subplot margins are unchanged, placing the
observed catalogue points more centrally without changing any data or model.
Within these figures only, broad-line AGN are purple and luminous quasars are
red to maximize contrast; other repository figures retain their established
class palette.

## Complete supplement figures

- `v3_all_object_fedd_mass_map_gallery.png`: all 219 $f_{Edd}$-mass panels.
- `v3_all_object_compatibility_atlas.png`: object-by-object compatibility
  across all supported scenarios.
- `v3_all_object_monte_carlo_uncertainty.png`: every object label and every
  supported 16th--84th percentile interval.
- `results/v3/gallery/fedd_mass_maps/`: one $f_{Edd}$-mass map per object.
- `results/v3/gallery/seedredshift_mass_maps/`: one seed-redshift-mass map per object.

The gallery therefore contains 438 canonical per-object panels. Numerical
seed-redshift-mass maps solve for the lifetime-average Eddington fraction over seed
mass and seed redshift using the baseline efficiency and merger assumptions;
objects without a supported mass receive the same explicit no-inference
treatment as the $f_{Edd}$-mass maps. Growth tracks are provided only in
combined all-object figures, never as individual gallery panels.

For the 23 objects without a supported canonical numerical black-hole mass,
the visual atlas uses explicit no-inference panels. It does not invent masses,
posteriors, compatibility classifications, or growth histories.

Regenerate and verify with:

```bash
mkdir -p /tmp/highz-atlas-notebooks
.venv/bin/jupyter nbconvert --to notebook --execute --output-dir=/tmp/highz-atlas-notebooks scripts/03_generate_atlas.ipynb
.venv/bin/jupyter nbconvert --to notebook --execute --output-dir=/tmp/highz-atlas-notebooks scripts/04_verify.ipynb
```
