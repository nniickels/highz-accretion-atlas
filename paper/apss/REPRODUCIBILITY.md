# Ap&SS reproducibility record

Updated 15 October 2026.

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
Baseline Monte Carlo probabilities are retained; the calibration table labels
its analytic reported-error probabilities separately.

## Cited repository version

The manuscript links both the project repository and commit
`77908cdaadb5898e5f2e1d2d353cf99d2a3a26ac`. That commit contains the
catalogue, baseline and earlier-onset analyses, current scientific figure
exports, and the additional calibration calculation. It also contains the
pinned dependency versions and reproduction commands. The scientific
calibration files match that revision exactly.

The calibration code is `src/internal/calibration_sensitivity.py`; its input
and result are `results/for_manuscript/tables/target_robustness.csv` and
`results/for_manuscript/tables/calibration_sensitivity.csv`. These paths are
valid at the cited commit. The redundant supplementary folder and ZIP have
been removed. The manuscript retains the methods and numerical results.

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
  calibration code, input and result are checked against the cited repository
  version; publication selection reproduces the result table.
- The manuscript compiled without undefined-reference or overfull-box warnings.

The three previously unresolved identity groups remain excluded. These checks
do not independently validate every catalogue field or establish the physical
validity of a virial mass estimator. This run did not reinstall dependencies or
execute all five notebooks from scratch. Baseline figures were unchanged; their
full publication rerender check passed in the preceding audit, and the v4 figure
check was rerun after this revision.

## Rebuild and check

From this directory, `python3 build_package.py` compiles the manuscript and
builds the source ZIP. After reviewing intentional changes, use
`python3 build_package.py --record-reviewed-hashes`, then
`python3 verify_package.py`. The integrity checker compares reviewed hashes,
pinned figures, cited repository files, and source archive membership/content.
It does not silently update a hash when a check fails.

From the repository root:

```sh
.venv/bin/python -m src.internal.publication_selection
.venv/bin/python -m unittest tests.test_calibration_sensitivity
.venv/bin/python -m src.internal.calibration_sensitivity \
  --input results/for_manuscript/tables/target_robustness.csv \
  --verify results/for_manuscript/tables/calibration_sensitivity.csv
```

The generic Overleaf packager targets the original manuscript, not this Ap&SS
copy. Manuscript wording remains locally maintained; numerical regeneration
does not rewrite it. The source ZIP excludes the cover letter. The calibration code and data are
accessed through the cited repository commit; no supplementary upload is needed.

## Pagination and AI disclosure update

The methods now include AI-assisted code development and documentation. The
appendices precede the references; declarations, figures with legends, and
tables follow. Figure/table numbering follows first narrative citation. Figure
captions, table captions, scientific assets, and numerical inputs are unchanged.
The package checker verifies the section order, figure/table membership and
citation order in addition to hashes and archive contents. The revised source
ZIP was rebuilt and compiled in an independent temporary directory. Layout
changes do not alter the calibration analysis or baseline calculation.

The package checks figures at `results/for_manuscript/` against the cited
commit. The earlier historical-path mapping is no longer needed.
