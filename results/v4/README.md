# v4 growth analysis

This analysis uses four targets from the existing v3 catalogue: the three
highest-ranked primary objects under the reference growth model and GN-z11,
whose mass is estimated from ultraviolet lines. It tests growth from assumed
seeds, including primordial black holes (PBHs); it does not add measurements or
model the abundance of PBHs. See the [methods and assumptions](../../docs/reference/pbh-growth-v4.md).

## Tables

| File | Contents |
| --- | --- |
| `tables/v4_targets.csv` | Adopted measurements, uncertainties, source caveats, and selection reasons. |
| `tables/v4_minimum_seed_mass.csv` | Minimum seeds for each starting time, rate cap, efficiency, and mass shift, with mass-error percentiles. |
| `tables/v4_seed_onset_compatibility.csv` | Required average rates and fractions of mass-error draws reachable from each seed and starting time. |
| `tables/v4_controls.csv` | Specified stellar-remnant, heavy astrophysical, and primordial seed scenarios. |

The baseline uses an average Eddington-ratio cap of 1, radiative efficiency 0.1,
and no mass shift. A seed that already exceeds a sampled final mass is counted
as overpredicting it, rather than as a successful growth history.

## Figures

Each figure has PNG and PDF exports:

- `figures/v4_minimum_seed_mass.*`: dependence on starting time, rate cap, and
  efficiency. Bands show the 16th–84th percentiles from mass-error draws.
- `figures/v4_seed_onset_maps.*`: fractions of draws reachable under the baseline
  growth cap, excluding seeds that overpredict the sampled mass.
- `figures/v4_controls.*`: specified seed scenarios using the same cosmology.

These fractions describe mass-error draws under fixed assumptions. They are
not probabilities of seed formation. Starting accretion at matter–radiation
equality is an optimistic benchmark; the calculation does not establish seed
formation, sustained gas supply, or consistency with external PBH constraints.

## Generate and verify

From the repository root, after [setup](../../README.md#getting-started):

```bash
.venv/bin/python -m src.internal.pbh_growth_v4 --write
.venv/bin/python -m src.internal.pbh_growth_v4 --verify
```

Notebook 05 runs the same analysis. `v4_manifest.json` records configuration,
inputs, code, cosmology, row counts, and output hashes. Writing to this folder
also updates `results/results_inventory.csv`; retain that inventory with the
outputs. Verification is read-only. Follow the
[reproduction guide](../../docs/guides/reproducibility.md) before changing reviewed inputs.
