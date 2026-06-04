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

The notebook currently contains the v1 feasibility-scoring workflow and plotting
prototype. The catalogue standardization command above should be run first so
the notebook uses the latest processed CSV.
