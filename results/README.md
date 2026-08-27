# Results Directory Guide

This directory contains immutable historical release artifacts plus organized
current compilations. Existing root-level CSVs and release figure paths remain
in place because manifests, reproduction commands, documentation, and citations
refer to those exact paths. New collections use descriptive subdirectories.

## Find a result

- `results_inventory.csv`: machine-readable index of every result artifact,
  including release, category, byte size, SHA-256 hash, and path policy.
- `compiled_object_grids/`: high-resolution lossless grids containing every v1
  object map. There are six spin/merger parameter-map grids and one baseline
  seed-redshift grid. `grid_inventory.csv` records dimensions and hashes.
- `v1_parameter_maps/`: 138 individual parameter maps: 23 objects across three
  spin efficiencies and two merger assumptions.
- `v1_seed_redshift_maps/`: 23 individual seed-redshift maps.
- `v2_main_text_figures/` through `v5_main_text_figures/`: release-specific
  paper-facing or prototype figures.
- Root-level `v1_*.csv` through `v7_2_*.csv`: frozen science tables retained at
  their original manifest-covered paths.

## Regeneration

After the individual v1 maps exist, regenerate the all-object grids and index:

```bash
python -m scripts.generate_all_object_grid_figures
python -m scripts.build_results_inventory
```

The compilation step reads but does not rewrite individual maps. The inventory
step is non-scientific metadata and does not move or alter an artifact.

## Interpretation boundary

The grids are appendix/supplement navigation products. Each panel retains the
assumptions and labels of its source map. They help compare all objects under
one fixed scenario; they do not turn heterogeneous selections into a
demographically complete sample or identify a unique formation history.
