# Getting Started

## Requirements

The shared reproducible v4.0.1--v7.4 catalogue and science environment is Python 3.12 with exact
package versions in `requirements-lock.txt`. Do not use the Apple Command Line
Tools Python: it may resolve as Python 3.9 and does not contain the project
dependencies.

Create a repository-local environment on macOS or Linux with:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --requirement requirements-lock.txt
.venv/bin/python --version
```

On Windows PowerShell, use:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --requirement requirements-lock.txt
.\.venv\Scripts\python.exe --version
```

The version check must report Python 3.12. Run tests without relying on shell
activation or an ambiguous `python` command:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests
```

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m unittest discover -s tests
```

The remaining examples use `python` for readability and assume the environment
has first been activated with `source .venv/bin/activate` on macOS/Linux or
`.\.venv\Scripts\Activate.ps1` in PowerShell. Using the explicit interpreter
paths above is equally valid.

CI and all non-interactive catalogue/science workflows use only this core lock.
For the optional legacy interactive v1 notebook environment, install
`requirements-notebook-lock.txt` instead. Runtime package metadata is also
recorded in `pyproject.toml`.

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
Manifest membership and hashes are exact. Independently rebuilt tables require exact structure
and nonnumeric content, while floating-point columns use `rtol=1e-13` and
`atol=1e-14` so normal platform-level `libm` differences do not create false
failures.

## Current v7.4 Catalogue and v7.2 Science Layers

The current catalogue copies frozen v7.3 and adds all 20 tabulated Scholtz et
al. candidates at `z >= 4`:

```powershell
python -m scripts.process_v7_4_catalogue
python -m scripts.verify_v7_4_catalogue --reproduce
```

It contains 233 measurements, 218 physical objects, and 217 host systems. The
new family has no numeric black-hole masses, so frozen v7.2 science remains the
current growth analysis. The conservative object evidence aggregate reduces
the catalogue's primary-object count by one for multiply observed JADES 8083.
See `docs/v7.4-catalogue-schema.md`.

### Frozen v7.3 catalogue

The v7.3 catalogue copies frozen v7.2 and adds the two-version UHZ1 X-ray
evidence history:

```powershell
python -m scripts.process_v7_3_catalogue
python -m scripts.verify_v7_3_catalogue --reproduce
```

It contains 213 measurements, 199 physical objects, and 198 host systems. UHZ1
is represented once at object level, with the disputed full-data reanalysis
preferred; neither literature version is growth-ranked because no canonical
numeric mass is admitted. See `docs/v7.3-catalogue-schema.md`.

### Frozen v7.2 catalogue and class-aware science

The frozen v7.2 catalogue layer copies frozen v7.1 and adds all 50 Shen et al.
GNIRS quasars as a second luminous-quasar comparison family:

```powershell
python -m scripts.process_v7_2_catalogue
python -m scripts.verify_v7_2_catalogue --reproduce
```

This writes 211 measurements, 198 physical objects, 197 host systems, explicit
measurement/object and object/host links, 993 source observables, six reviewed
GNIRS/XQR identity decisions, and stratified catalogue counts. Build and verify
the class-aware science layer separately:

```powershell
python -m scripts.generate_v7_2_class_aware_science --n-samples 10000 --seed 20260808
python -m scripts.verify_v7_2_science --reproduce
```

The eight science tables keep global navigation distinct from within-class and
within-mass-method comparisons, propagate published statistical mass errors,
and retain a separate systematic envelope. No v7.2 figure set is generated. See
`docs/v7.2-catalogue-schema.md` and
`docs/shen19-gnirs50-extraction-notes.md`, and
`docs/v7.2-class-aware-science-workflow.md`.

## Current Completed v6 Science Release

The current release extends frozen v5 with the complete seven-row Davis/THRILS
Appendix Table 5 and retains six rows after the project redshift cut:

```powershell
python -m scripts.process_v6_blagn
python -m scripts.generate_v6_blagn_science --n-samples 10000 --seed 20260808
python -m scripts.verify_v6_release --reproduce
```

This writes 112 measurements, 105 physical objects, links and aliases, an empty
schema-preserving reviewed-candidate file, and 16 v6 science tables. The six
retained THRILS measurements are six new objects; the known Taylor repeat is
below `z=4` and remains in raw-source history only. See
`docs/v6-blagn-catalogue-schema.md`,
`docs/davis26-thrils-extraction-notes.md`, and
`docs/v6-blagn-science-workflow.md`.

No v6 figures are generated by this step. The independently verified v5 paper
figures remain the current deliberate rendered set.

## Frozen v5 BLAGN Release

The v5 release extends frozen v4 with the ten-row Harikane NIRSpec
broad-Halpha sample:

```powershell
python -m scripts.process_v5_blagn
python -m scripts.generate_v5_blagn_science --n-samples 10000 --seed 20260808
python -m scripts.generate_v5_final_figures
python -m scripts.verify_v5_release --reproduce
python -m scripts.verify_v5_figures
```

This writes 106 measurements, 99 physical objects, 106 links and aliases, six
reviewed candidates, and 16 v5 science tables. Five Harikane measurements link
to existing objects and five create new objects. See
`docs/v5-blagn-catalogue-schema.md`,
`docs/harikane23-nirspec-extraction-notes.md`, and
`docs/v5-blagn-science-workflow.md`. The figure command writes three current
main-text figures and one appendix sensitivity figure documented in
`docs/v5-figure-inventory.md`; it does not alter frozen v1--v4 figures.
The last command verifies exact membership and hashes for those four canonical
PNGs without regenerating them.

The verifier checks exact v5 manifest membership and hashes, then reconstructs all five
catalogue/identity plus 16 science products in memory. CI runs it with
`--require-clean` after the frozen-v4 gate, then verifies the separate canonical
figure manifest from the same clean checkout.

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
candidate plus its explicit review decision. The science command writes 13 `results/releases/v4/tables/v4_blagn_*.csv` products at
measurement and physical-object level. Expected source additions are 20 Matthee
EIGER/FRESCO rows and 16 Lin ASPIRE rows. The newly reviewed identity is
`GOODS-S-13971 = GS-204851`; the existing
`CEERS-2782 = RUBIES-EGS-50052` identity is inherited from v3.

See `docs/v4-blagn-catalogue-schema.md` for catalogue/identity details and
`docs/v4-blagn-science-workflow.md` for the output and scenario inventory.
No command overwrites a v1--v3 artifact.

The figure command writes five v4-specific final figures to
`results/releases/v4/figures/main_text/`. Generate the frozen-v3 comparison figures
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

- `data/processed/v3/v3_blagn_measurements.csv` (60 measurement rows)
- `data/processed/v3/v3_blagn_objects.csv` (59 physical-object rows)

The object view links CEERS-2782 and RUBIES-EGS-50052 but retains both in the
measurement view. The command does not run rankings or regenerate figures.
Schema and source details are in `docs/v3-blagn-catalogue-schema.md` and
`docs/taylor24-ceers-rubies-extraction-notes.md`.

Generate the v3 evaluation, point rankings, uncertainty rankings, and
stratified summaries with:

```powershell
python -m scripts.generate_v3_blagn_science --n-samples 10000 --seed 20260808
```

This writes only `results/releases/v3/tables/v3_blagn_*.csv` products. It produces separate
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
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m unittest discover -s tests
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
- writes `data/processed/v1/v1_processed.csv`
- prints optional missing-field counts for Mstar, Lbol, Eddington ratio, and
  lensing metadata

## Quick Checks

Inspect the regenerated file:

```powershell
python -c "import pandas as pd; df = pd.read_csv('data/processed/v1/v1_processed.csv'); print(df.shape); print(df[['missing_mstar_flag','missing_lbol_flag','missing_edd_ratio_flag','missing_lensing_flag']].sum())"
```

Confirm the processed columns against the schema:

```powershell
python -c "import pandas as pd; print('\n'.join(pd.read_csv('data/processed/v1/v1_processed.csv', nrows=0).columns))"
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

- `results/releases/v1/tables/v1_evaluation_table.csv`
- `results/releases/v1/tables/v1_required_fedd_by_seed_mass.csv`
- `results/releases/v1/tables/v1_required_mseed_by_growth_assumption.csv`
- `results/releases/v1/tables/v1_sample_summary.csv`

It also writes these PNG figure outputs:

- `results/releases/v1/figures/v1_mbh_vs_redshift_growth_tracks.png`
- `results/releases/v1/figures/v1_sample_compatibility_summary.png`
- one per-object PNG map per processed object in `results/releases/v1/galleries/parameter_maps/`

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

- `results/releases/v2/tables/v2_object_ranking_table.csv`

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

- `results/releases/v2/tables/v2_uncertainty_required_fedd_summary.csv`
- `results/releases/v2/tables/v2_uncertainty_required_mseed_summary.csv`
- `results/releases/v2/tables/v2_uncertainty_aware_ranking_table.csv`

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

- `results/releases/v2/figures/main_text/`

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

Run the full v1--v7.2 regression suite from the repository root:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; .\.venv\Scripts\python.exe -m unittest discover -s tests
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
  `results/releases/v1/galleries/seed_redshift_maps/`
- one exploratory 3D required-`f_Edd` surface in
  `results/releases/v1/galleries/seed_redshift_3d_tests/`

After the individual parameter and seed-redshift maps exist, compile every
object into zoomable grid figures and refresh the categorized results index:

```powershell
python -m scripts.generate_all_object_grid_figures
python -m scripts.build_results_inventory
python -m scripts.verify_v7_3_results_gallery
```

The seven lossless 6048-by-5648 PNG grids live in
`results/releases/v7_3/galleries/compiled_object_grids/`. This step reads but does not overwrite any
individual map or frozen science table.

These figures use the same processed v1 catalogue and restrict the seed
redshift scan to `z_seed <= 30`.
