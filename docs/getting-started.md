# Getting Started

## Requirements

The reproducible v4.0.1 environment is Python 3.12 with exact package versions
in `requirements-lock.txt`. Install it with:

```powershell
python -m pip install --requirement requirements-lock.txt
```

The lock includes Jupyter for the legacy interactive v1 evaluation notebook.
Runtime package metadata is also recorded in `pyproject.toml`.

The v1 standardization pass itself only needs Python plus `numpy` and `pandas`.

The project release chronology and filename rules are documented in
`docs/release-versioning.md`.

Before trusting checked-in v4 products, verify their release hashes and rebuild
all catalogue and science CSVs in memory (no artifact is written):

```powershell
python -m scripts.verify_v4_release --reproduce
```

CI additionally runs this command with `--require-clean`, after the complete
regression suite, to prove that verification leaves a clean checkout unchanged.

## Current v5 BLAGN Release

The current release extends frozen v4 with the ten-row Harikane NIRSpec
broad-Halpha sample:

```powershell
python -m scripts.process_v5_blagn
python -m scripts.generate_v5_blagn_science --n-samples 10000 --seed 20260808
```

This writes 106 measurements, 99 physical objects, 106 links and aliases, six
reviewed candidates, and 13 v5 science tables. Five Harikane measurements link
to existing objects and five create new objects. See
`docs/v5-blagn-catalogue-schema.md`,
`docs/harikane23-nirspec-extraction-notes.md`, and
`docs/v5-blagn-science-workflow.md`.

## Frozen v4 BLAGN Release

The shortest reproduction path for frozen v4 uses the checked-in v3
measurement catalogue as its input:

```powershell
python -m scripts.process_v4_blagn
python -m scripts.generate_v4_blagn_science --n-samples 10000 --seed 20260808
python -m scripts.generate_v4_final_figures
```

To rebuild the catalogue chain from source-specific raw tables instead, run:

```powershell
python -m scripts.process_data
python -m scripts.process_v3_blagn
python -m scripts.process_v4_blagn
python -m scripts.generate_v4_blagn_science --n-samples 10000 --seed 20260808
python -m scripts.generate_v4_final_figures
```

The v4 processing command writes 96 measurement rows, 94 physical-object rows,
96 measurement/object links, 96 aliases, and one reviewed cross-paper match
candidate plus its explicit review decision. The science command writes 13 `results/v4_blagn_*.csv` products at
measurement and physical-object level. Expected source additions are 20 Matthee
EIGER/FRESCO rows and 16 Lin ASPIRE rows. The newly reviewed identity is
`GOODS-S-13971 = GS-204851`; the existing
`CEERS-2782 = RUBIES-EGS-50052` identity is inherited from v3.

See `docs/v4-blagn-catalogue-schema.md` for catalogue/identity details and
`docs/v4-blagn-science-workflow.md` for the output and scenario inventory.
No command overwrites a v1--v3 artifact.

The figure command writes five v4-specific final figures to
`results/v4_main_text_figures/`. Generate the frozen-v3 comparison figures
separately when needed:

```powershell
python -m scripts.generate_v3_final_figures
```

## v3 Expanded BLAGN Release

Build the separate v3 catalogue without changing v1 or v2:

```powershell
python -m scripts.process_v3_blagn
```

This validates all 63 Taylor Table 1 measurements, applies `z >= 4` only in the
processing layer, combines the resulting 37 measurements with the 23-row v1
catalogue, and writes:

- `data/processed/v3_blagn_measurements.csv` (60 measurement rows)
- `data/processed/v3_blagn_objects.csv` (59 physical-object rows)

The object view links CEERS-2782 and RUBIES-EGS-50052 but retains both in the
measurement view. The command does not run rankings or regenerate figures.
Schema and source details are in `docs/v3-blagn-catalogue-schema.md` and
`docs/taylor24-ceers-rubies-extraction-notes.md`.

Generate the v3 evaluation, point rankings, uncertainty rankings, and
stratified summaries with:

```powershell
python -m scripts.generate_v3_blagn_science --n-samples 10000 --seed 20260808
```

This writes only `results/v3_blagn_*.csv` products. It produces separate
measurement- and physical-object-level rankings, keeps statistical MBH sampling
separate from the global `+/-0.3 dex` and Taylor-only `+/-0.5 dex` sensitivity
scenarios, and does not regenerate figures. See
`docs/v3-blagn-science-workflow.md` for the full inventory and ranking
interpretation.

## End-to-End v1 + v2 Reproduction

Run commands from the repository root. The evaluation notebook is the one
interactive step; run all cells before generating ranking products.

```powershell
python -m scripts.process_data
jupyter notebook scripts/v1_evaluate.ipynb
python scripts/generate_v2_rankings.py
python scripts/generate_v2_uncertainty_rankings.py --n-samples 10000 --seed 20260808
python scripts/generate_v2_final_figures.py
$env:PYTHONDONTWRITEBYTECODE='1'; python -m unittest discover -s tests
```

Current v1 catalogue regression anchors are 23 processed measurements, redshift range
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

## v2 Ranking Table (v1 Catalogue)

After regenerating the processed catalogue and v1 evaluation CSVs, run:

```powershell
python scripts/generate_v2_rankings.py
```

This writes:

- `results/v2_object_ranking_table.csv`

The script prints a verification summary with the row count, `measurement_id`
uniqueness check, top-ranked physical-pressure objects, and sanity checks for
known v1 high-leverage objects.

Ranking columns are point-estimate triage metrics. They separate physical
growth pressure from measurement robustness/caveats and use required-parameter
metrics rather than compatibility scores for the main physical-pressure rank.

## v2 Uncertainty-Aware Rankings (v1 Catalogue)

After generating the v2 point-estimate ranking from the v1 catalogue,
run:

```powershell
python scripts/generate_v2_uncertainty_rankings.py
```

Optional controls:

```powershell
python scripts/generate_v2_uncertainty_rankings.py --n-samples 10000 --seed 20260808
```

This samples the reported asymmetric black-hole mass errors and evaluates
baseline, `MBH -0.3 dex`, and `MBH +0.3 dex` systematic scenarios. It writes:

- `results/v2_uncertainty_required_fedd_summary.csv`
- `results/v2_uncertainty_required_mseed_summary.csv`
- `results/v2_uncertainty_aware_ranking_table.csv`

The uncertainty propagation design and current v2 ranking summary are
documented in `docs/v2-uncertainty-propagation.md`.

Scenario suffixes keep statistical MBH sampling separate from systematic
mass-shift cases. Preferred probability columns use names such as
`prob_required_fedd_seed1e2_gt_1_baseline` and
`prob_required_mseed_fedd0p3_gt_1e6_baseline`.

## v2 Main-Text Figure Prototypes (v1 Catalogue)

After generating the v2 ranking table, run:

```powershell
python scripts/generate_v2_final_figures.py
```

This writes final-style prototype figures to:

- `results/v2_main_text_figures/`

Expected prototype filenames:

- `v2_main_text_mbh_redshift_growth_overview.png`
- `v2_main_text_ranked_required_fedd.png`
- `v2_main_text_ranked_required_seed_mass.png`
- `v2_main_text_pressure_vs_confidence.png`
- `v2_main_text_uncertainty_forest.png`
- `v2_main_text_spotlight_seed_redshift_maps.png`

The exploratory figures and full map galleries in `results/` are not deleted or
replaced. The figure inventory is documented in `docs/v2-figure-inventory.md`.
Prototype filenames begin with `v2_main_text_` to distinguish them from
exploratory v1 outputs.

## Verification Checks

Run the v1--v5 verification suite from the repository root:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; python -m unittest discover -s tests
```

These checks cover growth-model sanity behavior, catalogue standardization,
scoring semantics, the v2 ranking-table contract, current v1 numeric regression
anchors, Taylor/Matthee/ASPIRE source contracts, v3/v4 identity handling, and
expanded science-output invariants. The numeric anchors lock down the present 23-row v1
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
