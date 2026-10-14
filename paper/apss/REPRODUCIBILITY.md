# Ap&SS reproducibility record

Updated 14 October 2026.

## Baseline and added calculation

The catalogue, sample selections, baseline numerical tables, random seeds,
growth equations and eight figures are unchanged. The revised prose explains
the contribution, source checks, table use, retained preprint measurements and
AI assistance.

The added result is `calibration_sensitivity.csv`: four rows for two objects
at offsets 0 and -0.5 dex. The calculation treats their separately reported
0.5-dex scales as independent Gaussian standard deviations. Their reported
errors are symmetric, so variances add and probabilities follow exactly from
the normal CDF. It adds nothing to objects whose quoted errors already include
calibration scatter. It is not a common uncertainty model for the full sample.

J0910_2028_12910 has probability 0.745268 without a mass shift and 0.366880
with a -0.5-dex shift. RUBIES-EGS-55604 has 0.998746 and 0.979411, respectively.
Baseline Monte Carlo probabilities are retained; the supplementary table labels
its analytic reported-error probabilities separately.

## Versions and supplied files

- Catalogue and baseline numerical tables: `1629c963cc43205bf61467e63a418e14e948efe8`.
- Baseline implementation, current figures and earlier-onset analysis:
  `9584a7d05b597740434e3413514a12eb4811f6b6`.
- Additional calibration calculation: supplied in `apss_supplementary.zip`,
  with code, reference input, result, dependency pins and execution instructions.
  The old commits do not contain this addition.

All eight submitted figure PDFs match the pinned canonical exports byte-for-byte.
The three original LaTeX table fragments are unchanged. The fourth,
`tables/calibration_rows.tex`, displays the new CSV probabilities. The original
12 earlier-onset seed entries still match their rounded canonical values.

The new calculation is part of `build_publication_outputs`, so notebook 01
regenerates it and notebook 04 verifies it through the existing pipeline. The
independent artifact comparison includes its CSV. The results inventory gained
one row for this new artifact; no baseline data/provenance manifests or comparison
tolerances were changed. A future notebook regeneration must use an independent
baseline containing this intentional addition, as documented in the main guide.

## Verification performed

- All 133 regression tests passed, including a comparison of the analytic
  calibration probability with independently drawn Gaussian errors and checks
  that already-included scatter is not added again.
- `verify_versions` passed for v1–v3, including numerical reproduction,
  dataset manifests and the updated result inventory.
- `publication_selection` reproduced all prior publication tables plus the
  new calibration table: 220 primary and 234 expanded objects.
- `pbh_growth_v4 --verify` passed, including its input hashes, regenerated
  numerical tables and figure comparisons.
- `verify_primary_source_values` passed 2,041 independent source-value checks.
- The final source ZIP compiled in a separate temporary directory. The
  supplementary ZIP's calculation reproduced its supplied table independently
  of the project import path.
- The manuscript compiled without undefined-reference or overfull-box warnings.

The three previously unresolved identity groups remain excluded. These checks
do not independently validate every catalogue field or establish the physical
validity of a virial mass estimator. This run did not reinstall dependencies or
execute all five notebooks from scratch. Baseline figures were unchanged; their
full publication rerender check passed in the preceding audit, and the v4 figure
check was rerun after this revision.

## Rebuild and check

From this directory, `python3 build_package.py` compiles the manuscript and
builds both ZIPs. After reviewing intentional changes, use
`python3 build_package.py --record-reviewed-hashes`, then
`python3 verify_package.py`. The integrity checker compares reviewed hashes,
pinned figures, supplementary source copies, and archive membership/content.
It does not silently update a hash when a check fails.

From the repository root:

```sh
.venv/bin/python -m src.internal.publication_selection
.venv/bin/python -m unittest tests.test_calibration_sensitivity
.venv/bin/python -m src.internal.calibration_sensitivity \
  --input results/manuscript/tables/target_robustness.csv \
  --verify results/manuscript/tables/calibration_sensitivity.csv
```

The generic Overleaf packager targets the original manuscript, not this Ap&SS
copy. Manuscript wording remains locally maintained; numerical regeneration
does not rewrite it. The source ZIP excludes the cover letter and supplementary
analysis files; upload the supplementary ZIP separately.

## Pagination and AI disclosure update

The methods now include AI-assisted code development and documentation. The
appendices precede the references; declarations, figures with legends, and
tables follow. Figure/table numbering follows first narrative citation. Figure
captions, table captions, scientific assets, and numerical inputs are unchanged.
The package checker verifies the section order, figure/table membership and
citation order in addition to hashes and archive contents. The revised source
ZIP was rebuilt and compiled in an independent temporary directory. Layout
changes do not alter the supplementary analysis or baseline calculation.
