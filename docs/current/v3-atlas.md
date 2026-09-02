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
2. `v3_compatibility_summary.png` — all 196 computable objects summarized
   by class, seed family, spin, merger boost, and accretion rate.
3. `v3_monte_carlo_summary.png` — all 196 numerical posteriors plus an
   explicit accounting of the other 23 catalogue objects.

The existing catalogue landscape, class-aware pressure, and alternate-
measurement sensitivity figures remain valid supporting main-text figures
because they are calculated from the same v3 catalogue.

## Complete supplement figures

- `v3_all_object_parameter_map_gallery.png`: all 219 parameter panels.
- `v3_all_object_compatibility_atlas.png`: object-by-object compatibility
  across all supported scenarios.
- `v3_all_object_monte_carlo_uncertainty.png`: every object label and every
  supported 16th--84th percentile interval.
- `results/v3/gallery/per_object/`: a parameter map, growth track, and
  seed-redshift map for every object.

The gallery therefore contains 657 canonical per-object panels. Numerical
seed-redshift maps solve for the lifetime-average Eddington fraction over seed
mass and seed redshift using the baseline efficiency and merger assumptions;
objects without a supported mass receive the same explicit no-inference
treatment as the other gallery products.

For the 23 objects without a supported canonical numerical black-hole mass,
the visual atlas uses explicit no-inference panels. It does not invent masses,
posteriors, compatibility classifications, or growth histories.

Regenerate and verify with:

```bash
mkdir -p /tmp/highz-atlas-notebooks
.venv/bin/jupyter nbconvert --to notebook --execute --output-dir=/tmp/highz-atlas-notebooks scripts/03_generate_atlas.ipynb
.venv/bin/jupyter nbconvert --to notebook --execute --output-dir=/tmp/highz-atlas-notebooks scripts/04_verify.ipynb
```
