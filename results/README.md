# Results Directory Guide

Current paper-ready products are placed first by artifact type. Historical
results are retained separately as frozen snapshots for reproduction and
comparison.

## Layout

```text
results/
├── README.md
├── results_inventory.csv
├── figures/             four current v7.5 paper figures
├── tables/              current v7.5 science and coverage tables
├── galleries/           current gallery guide
└── past_releases/
    └── <release>/       frozen historical tables, figures, and galleries
```

Historical release names use underscores for minor versions in paths (`v7_2`,
`v7_3`) because artifact filenames follow the same convention.

## Current paper products

- [`figures/`](figures/) contains the four high-resolution figures referenced
  by the current manuscript.
- [`tables/`](tables/) contains the eight current class-aware science tables and
  the complete 219-object gallery-coverage table.
- [`galleries/`](galleries/) explains how current coverage reuses the complete
  v7.4 gallery without duplicating 588 images.
- [`../docs/publication/`](../docs/publication/) distinguishes submission-ready,
  supplement-ready, and internal-QA products.

## Past releases

- `past_releases/v1/` contains the pilot evaluation tables, standalone diagnostics,
  138 parameter maps, 23 seed-redshift maps, and exploratory 3D tests.
- `past_releases/v2/` contains ranking and uncertainty tables plus final-style
  prototypes for the frozen v1 catalogue.
- `past_releases/v3/` through `past_releases/v6/` contain the frozen BLAGN science tables;
  v3-v5 also retain their figure sets.
- `past_releases/v7_2/tables/` contains the frozen first class-aware science layer.
- `past_releases/v7_3/galleries/compiled_object_grids/` contains seven lossless,
  high-resolution grids compiling every v1 per-object map by scenario.
- `past_releases/v7_4/` contains complete growth products for all 196 eligible
  objects: 196 parameter-map sheets, 196 seed-redshift maps, 196 reference
  growth tracks, six high-resolution class grids, and class-specific
  compatibility fractions. Its coverage table explicitly records the other
  22 catalogue objects as unavailable rather than silently omitting them.
  Each compiled grid uses one shared assumptions caption; captions are not
  repeated inside every object panel. The current coverage table points to
  these files because the eligible population and growth inputs are unchanged.
- `results_inventory.csv` indexes every result artifact with its release,
  collection, size, SHA-256 hash, and canonical path.

Catalogue tables are stored under `data/processed/<release>/` and identity
products under `data/crossmatch/<release>/`; see `data/README.md`.

For the curated distinction between submission-ready figures, supplement-ready
tables/galleries, and internal QA artifacts, see
[`docs/publication/README.md`](../docs/publication/README.md).

## Regeneration

After the individual v1 maps exist, regenerate the all-object grids and index:

```bash
python -m scripts.generate_all_object_grid_figures
python -m scripts.build_results_inventory
```

Regenerate and verify the complete current figure/coverage layer with:

```bash
python -m scripts.generate_v7_5_figures
python -m scripts.build_results_inventory
python -m scripts.verify_v7_5_figures
```

The grid step reads but does not rewrite individual maps. The inventory is
deterministic metadata and does not alter scientific artifacts.

## Interpretation boundary

The grids are appendix/supplement navigation products. Each panel retains the
assumptions and labels of its source map. The v7.4 compatibility fractions are
reported within object class only and are descriptive, not demographic. These
products do not make the heterogeneous catalogue complete or identify a unique
formation history.
