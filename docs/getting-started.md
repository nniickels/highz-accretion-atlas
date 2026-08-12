# Getting Started

## Requirements
- Python 3.10 or newer
- `numpy`
- `pandas`
- `matplotlib`
- Jupyter, if you want to run `scripts/v1_evaluate.ipynb`

The v1 standardization pass itself only needs Python plus `numpy` and `pandas`.

## End-to-End v1 Reproduction

Run commands from the repository root. The evaluation notebook is the one
interactive step; run all cells before generating ranking products.

```powershell
python -m scripts.process_data
jupyter notebook scripts/v1_evaluate.ipynb
python scripts/generate_v1_rankings.py
python scripts/generate_v1_uncertainty_rankings.py --n-samples 10000 --seed 20260808
python scripts/generate_v1_final_figures.py
$env:PYTHONDONTWRITEBYTECODE='1'; python -m unittest discover -s tests
```

Current v1 regression anchors are 23 processed measurements, redshift range
about 4.133 to 8.913, and quality flags of 18 robust plus 5 tentative. These
anchors describe the present v1 extraction; update them only with an
intentional catalogue or assumption change.

Important baseline assumptions for the ranking and uncertainty products are
`z_seed=30`, `epsilon=0.1`, `merger_boost=1`, and the flat Planck-style
cosmology implemented in `src.models`.

## v1 Catalogue Standardization

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

The v1 notebook writes static PNG figure outputs only.

These notebook figures are exploratory/reference outputs. They are useful for
appendix material and diagnostics, but they are not overwritten by the
final-style prototype figure script below.

## v1 Ranking Table

After regenerating the processed catalogue and v1 evaluation CSVs, run:

```powershell
python scripts/generate_v1_rankings.py
```

This writes:

- `results/v1_object_ranking_table.csv`

The script prints a verification summary with the row count, `measurement_id`
uniqueness check, top-ranked physical-pressure objects, and sanity checks for
known v1 high-leverage objects.

Ranking columns are point-estimate triage metrics. They separate physical
growth pressure from measurement robustness/caveats and use required-parameter
metrics rather than compatibility scores for the main physical-pressure rank.

## v1 Uncertainty-Aware Rankings

After generating the v1 point-estimate and uncertainty-aware ranking products,
run:

```powershell
python scripts/generate_v1_uncertainty_rankings.py
```

Optional controls:

```powershell
python scripts/generate_v1_uncertainty_rankings.py --n-samples 10000 --seed 20260808
```

This samples the reported asymmetric black-hole mass errors and evaluates
baseline, `MBH -0.3 dex`, and `MBH +0.3 dex` systematic scenarios. It writes:

- `results/v1_uncertainty_required_fedd_summary.csv`
- `results/v1_uncertainty_required_mseed_summary.csv`
- `results/v1_uncertainty_aware_ranking_table.csv`

The uncertainty propagation design and current v1 ranking summary are
documented in `docs/v1-uncertainty-propagation.md`.

Scenario suffixes keep statistical MBH sampling separate from systematic
mass-shift cases. Preferred probability columns use names such as
`prob_required_fedd_seed1e2_gt_1_baseline` and
`prob_required_mseed_fedd0p3_gt_1e6_baseline`.

## v1 Main-Text Figure Prototypes

After generating the v1 ranking table, run:

```powershell
python scripts/generate_v1_final_figures.py
```

This writes final-style prototype figures to:

- `results/v1_main_text_figures/`

Expected prototype filenames:

- `v1_main_text_mbh_redshift_growth_overview.png`
- `v1_main_text_ranked_required_fedd.png`
- `v1_main_text_ranked_required_seed_mass.png`
- `v1_main_text_pressure_vs_confidence.png`
- `v1_main_text_uncertainty_forest.png`
- `v1_main_text_spotlight_seed_redshift_maps.png`

The exploratory figures and full map galleries in `results/` are not deleted or
replaced. The figure inventory is documented in `docs/v1-figure-inventory.md`.
Prototype filenames begin with `v1_main_text_` to distinguish them from
exploratory v1 outputs.

## Verification Checks

Run the lightweight v1 verification suite from the repository root:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; python -m unittest discover -s tests
```

These checks cover growth-model sanity behavior, catalogue standardization
validation, scoring semantics, the v1 ranking-table contract, and current v1
numeric regression anchors. The numeric anchors lock down the present 23-row v1
catalogue and baseline science-output ranks so future changes do not silently
alter the interpretation; they are regression checks, not universal physical
constants. If the catalogue membership, source extraction, or baseline
assumptions intentionally change, review and update the anchors in the same
change. The tests use Python's built-in `unittest` runner and do not require
extra test dependencies. The environment variable avoids rewriting tracked
bytecode cache files during the test run.

## Optional Seed-Redshift Diagnostic Figures

To generate the additional seed-timing plots:

```powershell
python scripts/generate_seed_redshift_figures.py
```

This writes:

- per-object `M_seed` versus `z_seed` required-`f_Edd` maps in
  `results/v1_seed_redshift_maps/`
- one exploratory 3D required-`f_Edd` surface in
  `results/v1_seed_redshift_3d_tests/`

These figures use the same processed v1 catalogue and restrict the seed
redshift scan to `z_seed <= 30`.
