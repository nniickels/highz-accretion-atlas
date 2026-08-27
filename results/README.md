# Results Directory Guide

Generated results are organized first by project release and then by artifact
type. Historical releases are retained as frozen snapshots: later products are
usually more complete or polished, but earlier releases can contain distinct
diagnostics and are part of the reproducibility record.

## Layout

```text
results/
├── README.md
├── results_inventory.csv
└── releases/
    └── <release>/
        ├── tables/       generated CSV science products
        ├── figures/      standalone and paper-facing figures
        │   └── main_text/
        └── galleries/
            ├── per_object/         complete object-level collections
            └── compiled_by_class/  zoomable class-specific grids
```

Only folders needed by a release are present. Release names use underscores for
minor versions in paths (`v7_2`, `v7_3`) because artifact filenames follow the
same convention.

## Current and historical products

- `releases/v1/` contains the pilot evaluation tables, standalone diagnostics,
  138 parameter maps, 23 seed-redshift maps, and exploratory 3D tests.
- `releases/v2/` contains ranking and uncertainty tables plus final-style
  prototypes for the frozen v1 catalogue.
- `releases/v3/` through `releases/v6/` contain the frozen BLAGN science tables;
  v3-v5 also retain their figure sets.
- `releases/v7_2/tables/` contains the current class-aware science layer.
- `releases/v7_3/galleries/compiled_object_grids/` contains seven lossless,
  high-resolution grids compiling every v1 per-object map by scenario.
- `releases/v7_4/` contains complete growth products for all 196 eligible
  objects: 196 parameter-map sheets, 196 seed-redshift maps, 196 reference
  growth tracks, six high-resolution class grids, and class-specific
  compatibility fractions. Its coverage table explicitly records the other
  22 catalogue objects as unavailable rather than silently omitting them.
  Each compiled grid uses one shared assumptions caption; captions are not
  repeated inside every object panel.
- `results_inventory.csv` indexes every result artifact with its release,
  collection, size, SHA-256 hash, and canonical path.

Catalogue tables are stored under `data/processed/<release>/` and identity
products under `data/crossmatch/<release>/`; see `data/README.md`.

## Regeneration

After the individual v1 maps exist, regenerate the all-object grids and index:

```bash
python -m scripts.generate_all_object_grid_figures
python -m scripts.build_results_inventory
```

Regenerate and verify the complete current growth collection with:

```bash
python -m scripts.generate_v7_4_growth_products
python -m scripts.build_results_inventory
python -m scripts.build_v7_4_growth_manifest
python -m scripts.verify_v7_4_growth_products
```

The grid step reads but does not rewrite individual maps. The inventory is
deterministic metadata and does not alter scientific artifacts.

## Interpretation boundary

The grids are appendix/supplement navigation products. Each panel retains the
assumptions and labels of its source map. The v7.4 compatibility fractions are
reported within object class only and are descriptive, not demographic. These
products do not make the heterogeneous catalogue complete or identify a unique
formation history.
