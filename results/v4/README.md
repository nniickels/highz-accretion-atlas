# v4 growth tests

v4 uses four v3 objects: CAPERS-LRD-z9, UNCOVER-20466, CANUCS-LRD-z8.6,
and GN-z11. It calculates the seed masses and average accretion rates needed
to reach their measured masses. It varies starting time, efficiency, and mass
assumptions. See the [methods](../../docs/reference/pbh-growth-v4.md).

For all 241 usable v3 masses, see the [catalogue-wide minimum-seed table](../v3/tables/v3_minimum_seed_mass.csv).

## Tables

| File | Contents |
| --- | --- |
| `tables/v4_targets.csv` | Measurements, errors, source notes, and selection reasons. |
| `tables/v4_minimum_seed_mass.csv` | Minimum seeds for each starting time, rate limit, efficiency, and mass shift. |
| `tables/v4_seed_onset_compatibility.csv` | Required rates and the fraction of sampled masses reached by each seed and starting time. |
| `tables/v4_controls.csv` | Required rates for selected seed masses and starting times. |

The reference model uses an average Eddington ratio of at most 1, efficiency
0.1, and no mass shift. Seeds larger than the sampled final mass are rejected.
Reaching a measured mass does not establish the seed’s origin or abundance.

## Figures

Each figure has one PNG. See the
[previews](../../docs/reference/figures.md#v4-four-target-growth-study).

- `figures/v4_minimum_seed_mass.png`: minimum seeds versus starting time;
  bands show the 16th–84th percentiles from mass errors.
- `figures/v4_seed_onset_maps.png`: fraction of sampled masses reached under
  the reference rate limit.
- `figures/v4_controls.png`: required average rates for selected growth models.

## Generate and verify

From the repository root after [setup](../../README.md#getting-started):

```bash
.venv/bin/python -m src.internal.pbh_growth_v4 --write
.venv/bin/python -m src.internal.pbh_growth_v4 --verify
```

Notebook 05 runs the same calculation. `v4_manifest.json` records settings,
inputs, code, row counts, and file hashes. Writing outputs also updates
`results/results_inventory.csv`. Verification does not change files.
Follow the [reproduction guide](../../docs/guides/reproducibility.md) when
updating results.
