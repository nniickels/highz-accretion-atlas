# v4 conditional PBH growth analysis

This is a focused analysis extension using existing v3 measurements, not a new
catalogue or a PBH population-viability result. See
[methods, assumptions, source model, and commands](../../docs/reference/pbh-growth-v4.md).

Targets: the three highest-ranked eligible primary objects under the reference
model, plus GN-z11 as an expanded-sample UV-mass comparator.

## Tables

- `tables/v4_targets.csv`: measurement provenance, uncertainties, selection reasons,
  source caveats, and the unchanged reference ranking values.
- `tables/v4_minimum_seed_mass.csv`: minimum onset seeds at each rate cap,
  efficiency, mass offset, and onset; central masses and Monte Carlo percentiles.
- `tables/v4_seed_onset_compatibility.csv`: baseline seed/onset map, required
  mean rates, central compatibility status, conditional mass-draw support, and
  seed-overprediction fractions. Baseline: cap 1, epsilon 0.1, offset 0.
- `tables/v4_controls.csv`: specified stellar-remnant, heavy astrophysical, and
  PBH growth controls, with mean-rate requirements and uncertainty intervals.

## Figures

Each figure is exported to PNG and PDF:

- `figures/v4_minimum_seed_mass.*`: onset/rate/efficiency trade-offs; bands are
  16–84% mass-error percentiles, not formation-probability intervals.
- `figures/v4_seed_onset_maps.*`: fraction of mass-error draws reachable within
  the fixed baseline growth cap, excluding seeds that overpredict a draw.
- `figures/v4_controls.*`: selected seed/onset controls on a common cosmology.

`v4_manifest.json` pins configuration, inputs, code, row counts, cosmology, and
artifact hashes. It explicitly records external constraints and population
viability as **not assessed**. Equality-onset growth is an optimistic formal
benchmark; none of these plots verifies PBH formation or available fuel.
