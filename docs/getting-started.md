# Getting Started

## Requirements
- Python 3.10 or newer
- `numpy`
- `pandas`
- `matplotlib`
- Jupyter, if you want to run `scripts/v1_evaluate.ipynb`

The v1 standardization pass itself only needs Python plus `numpy` and `pandas`.

## v1 Catalogue Standardization

Run commands from the repository root:

```powershell
python -m scripts.process_data
```

Expected behavior:

- reads `data/raw/v1_raw.csv`
- validates the raw schema, numeric fields, required values, provenance fields,
  and unique `measurement_id`
- filters to `redshift >= 4`
- preserves source/method/provenance fields in the processed catalogue
- writes `data/processed/v1_processed.csv`
- prints optional missing-field counts for Mstar, Lbol, Eddington ratio, and
  lensing metadata

## Quick Checks

Inspect the regenerated file:

```powershell
python -c "import pandas as pd; df = pd.read_csv('data/processed/v1_processed.csv'); print(df.shape); print(df[['missing_mstar_flag','missing_lbol_flag','missing_edd_ratio_flag','missing_lensing_flag']].sum())"
```

Confirm the processed columns against the schema:

```powershell
python -c "import pandas as pd; print('\n'.join(pd.read_csv('data/processed/v1_processed.csv', nrows=0).columns))"
```

The processed column definitions and missing-value policy are documented in
`docs/catalogue-schema.md`.

## v1 Evaluation Notebook

After regenerating the processed catalogue, open or run:

```powershell
jupyter notebook scripts/v1_evaluate.ipynb
```

Run all cells in the notebook. The catalogue standardization command above
should be run first so the notebook uses the latest processed CSV.

The notebook writes these v1 CSV outputs:

- `results/v1_evaluation_table.csv`
- `results/v1_required_fedd_by_seed_mass.csv`
- `results/v1_required_mseed_by_growth_assumption.csv`
- `results/v1_sample_summary.csv`

It also writes these PNG figure outputs:

- `results/v1_mbh_vs_redshift_growth_tracks.png`
- `results/v1_sample_compatibility_summary.png`
- one per-object PNG map per processed object in `results/v1_parameter_maps/`

The v1 workflow intentionally writes PNG figures only.
