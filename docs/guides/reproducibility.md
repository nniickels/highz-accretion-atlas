# Reproducing results

Install the [pinned environment](../../README.md#getting-started) first.
Python 3.12 on Linux and macOS is supported. `requirements/core.txt` pins
numerical and rendering dependencies; `requirements/notebook.txt` adds Jupyter
and the package build tools.

## Independent comparison

Run the following from the repository root. It creates an unchanged baseline
and a separate execution copy of the same committed revision, then removes
generated outputs from the execution copy before running notebooks 00–04.
The original virtual environment supplies Python. Uncommitted files are excluded;
review and commit intended changes before using this procedure.

```bash
analysis_python="$PWD/.venv/bin/python"
baseline_root="$(mktemp -d "${TMPDIR:-/tmp}/highz-catalogue-baseline.XXXXXX")"
reproduction_root="$(mktemp -d "${TMPDIR:-/tmp}/highz-catalogue-reproduction.XXXXXX")"
executed_notebooks="$(mktemp -d "${TMPDIR:-/tmp}/highz-catalogue-notebooks.XXXXXX")"
git archive HEAD | tar -x -C "$baseline_root"
cp -R "$baseline_root/." "$reproduction_root/"
export HIGHZ_BASELINE_ROOT="$baseline_root"
cd "$reproduction_root"
"$analysis_python" - <<'PY'
from pathlib import Path
from src.internal.verify_regenerated_artifacts import artifact_paths
root = Path.cwd()
for name in artifact_paths(root):
    (root / name).unlink()
PY
for notebook in scripts/0[0-4]_*.ipynb; do
  "$analysis_python" -m nbconvert --to notebook --execute \
    --ExecutePreprocessor.timeout=1800 \
    --output-dir="$executed_notebooks" "$notebook" || exit 1
done
"$analysis_python" -m src.internal.pbh_growth_v4 --verify
```

Return to the original repository root before running other commands that use
`.venv/bin/python`. Keep the baseline unchanged and `HIGHZ_BASELINE_ROOT` set to
its path throughout regeneration.

Notebook 03 compares regenerated products against Git HEAD before refreshing
[data manifests](../../data/README.md#file-manifests). In a separate workspace, set
`HIGHZ_BASELINE_ROOT` to an independent checkout containing the reviewed outputs.
Comparing a workspace with itself, including through a symlink, is rejected.
A directory reorganization must first be committed or use an independent
baseline with the same paths; an older HEAD with different paths cannot match.
Keep the baseline unchanged throughout regeneration. Setting the variable to
the execution workspace itself is invalid. For v4, regenerated input CSVs may
be numerically equivalent despite different serialization bytes; their baseline
must still match the manifest's pinned hashes. Code and non-CSV inputs remain
byte-exact. See [v4 verification](../reference/pbh-growth-v4.md#run-and-verify).

The comparison covers canonical v1/v2/v3 catalogues, identity products, science
results, and the CSV tables and PNG figures in `results/for_manuscript/`:

- CSV values use the shared numerical tolerance.
- PNG dimensions and alpha must match exactly. Every RGB channel of every pixel
  may differ by at most 3 out of 255, allowing measured cross-platform rendering
  roundoff. There is no averaging, resizing or alignment. Use `--exact-pixels`
  with `src.internal.verify_regenerated_artifacts` for identical renderers.
- Canonical figures have PNG exports only. Manuscript PDF dependencies are
  generated separately for `paper/`; their packaged versions are independently
  compared by decoded contents, allowing compression and object numbering to differ.
- Missing or unexpected artifacts fail verification.

CI removes generated artifacts in a disposable workspace, runs all five notebooks,
and compares the results against the original checkout. It also runs the regression
suite, source checks, publication figure verification, and a package build/import check.
Manuscript editing and compilation are separate from analysis regeneration.
The [manuscript file guide](../../results/for_manuscript/README.md#manuscript-files)
identifies both draft editions and the public source package. A fresh checkout
can verify the general draft PDF and Overleaf ZIP without LaTeX:

```bash
.venv/bin/python -m src.internal.package_overleaf --verify
```

This checks source/PDF integrity, dependencies, and section order. It does not
rebuild scientific outputs or require byte-identical PDF compilation across
platforms. The Ap&SS source has additional unbundled compilation dependencies;
its readable PDF is tracked.

## Scientific checks

Run these checks from the original repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests
.venv/bin/python -m src.internal.verify_manual_extractions
.venv/bin/python -m src.internal.verify_primary_source_values
.venv/bin/python -m src.internal.verify_source_provenance
.venv/bin/python -m src.internal.verify_versions
.venv/bin/python -m src.internal.pbh_growth_v4 --verify
```

`python -m src.internal.verify_versions` independently rebuilds catalogue,
science and compatibility values. `python -m src.internal.publication_selection`
checks publication membership and sensitivity tables. The publication figure
verifier checks PNG exports against newly rendered figures.

Source-value checks have the bounded coverage described in the
[validation guide](../../data/validation/README.md). Reproduction agreement is
not a substitute for independent source evidence.

Three identity groups remain unresolved. The ordinary redshift/identity verifier
reports them; `--require-resolved` is the strict full-catalogue gate and currently
fails. The publication samples exclude all six affected records and place four
tentative JADES detections in the exploratory sample only, yielding 223 primary
and 238 exploratory objects. See the [identity audit](../source-notes/redshift-identity-audit.md).

## Intentional updates

The four [v3 result tables](../reference/catalogue-results.md) are generated by
notebook 01 and independently rebuilt by `verify_versions`. Their settings are
in `data/scenarios/catalogue_growth_comparisons.json`. The v3 manifest also
checks the relevant code, settings, and sample-rule hashes.

Accretion/seed maps and alternative-measurement figures with unchanged inputs
are stored in their earliest version. Rebuild v1, v2, and v3 in order; the map
coverage tables link each object to its retained image. Every version's manifest
also hashes the shared images it uses. Missing-mass reasons stay in the coverage
tables; duplicate evaluation tables and repeated figure variants are not exported.

Catalogue generation also fills ratio-consistency diagnostics, annotates the
independent scientific identity audit, and copies verified JADES provenance from
the source registry. These updates retain measurements and sample membership;
unknown extraction dates remain unknown.

Inspect and explain changes against the reviewed baseline before refreshing hashes:

```bash
.venv/bin/python -m src.internal.dataset_manifests
.venv/bin/python -m src.internal.verify_source_provenance --write
```

A hash refresh records the current files; it does not demonstrate reproduction.
An intentional change needs a reviewed baseline containing that change before
the comparison can pass.

The standalone `python -m src.internal.publication_figures` command refreshes
`results/results_inventory.csv` after exporting figures. Commit that inventory
with the changed exports.
The canonical v4 export command also refreshes this inventory after writing
its outputs and manifest. CI verifies v4 again after notebooks 00–04 regenerate
its catalogue inputs against the independent baseline.
For other intentional result edits, run
`python -m src.internal.build_results_inventory` after inspecting the changes.
The regression suite checks that the recorded sizes and hashes match the
checked-in results; this bookkeeping check does not replace independent
reproduction. `publication_figures --verify` never refreshes the inventory.

To reproduce the package build used by CI after installing the notebook lock:

```bash
SOURCE_DATE_EPOCH=1788393600 .venv/bin/python -m pip wheel . --no-deps --no-build-isolation --wheel-dir=/tmp/highz-wheels
```

## CUPC posters

The portrait and landscape PPTX sources and their reviewed PDF exports
are tracked in `posters/`. Each deck contains one slide, matching its PDF.
The editable decks are authoring inputs: wording and layout are reviewed
manually, while the scientific figures are generated from
the hash-pinned inputs in `data/poster_inputs.json`. Poster editing does not
change the 00–04 notebook workflow, scientific manifests, or comparison tolerances.

With the pinned core environment installed, run from the repository root:

```bash
.venv/bin/python -m unittest tests.test_poster_rebuild tests.test_poster_exports
.venv/bin/python -m src.internal.verify_poster_exports
.venv/bin/python -m src.internal.poster_figures --output-dir /tmp/highz-poster-figures
.venv/bin/python -m src.internal.poster_layout --output /tmp/highz-landscape-rebuilt.pptx
```

Use a new output path for each rebuild. The landscape builder verifies that the
two editions contain the same text and native equations, preserves the reviewed
landscape XML (including manual geometry and reference columns), and regenerates
both scientific plots. It does not derive the final layout from the old fixed
positions. Tests independently compare regenerated plot pixels with both decks,
check catalogue counts and citation mappings, and preserve the page dimensions.

`data/poster_exports.json` records each current PPTX hash and binds its PDF to
slide 1 with a fingerprint of that slide and all linked assets.
Verification checks these hashes, one-page dimensions, text-character
coverage, and embedded fonts. Character coverage tolerates exporter differences
in text order and whitespace; it is not a semantic or visual-layout comparison.
The byte hashes reject changes even if character counts happen to stay equal.

PDFs are manually exported presentation artifacts, not byte-identical outputs
of the scientific pipeline. The current exports were visually
reviewed after the 17 October 2026 scientific update, at their full page sizes. Font versions,
export applications, metadata, and PDF encodings can differ across systems.
When promoting a layout to the print version, export the chosen slide as a one-page
PDF at its native size (portrait 36 × 48 inches, landscape 48 × 36 inches),
inspect the actual PDF for text fit, symbols, images and font embedding, then
update that pair's exported slide number, fingerprint and artifact hashes.
Do not refresh hashes to bypass a failure. No automatic PDF exporter or
printer-specific bleed profile is implied.
The verifier runs in CI; no local authoring runtime is required there.
Verification does not rewrite or silently repair the reviewed PDFs.

## Ap&SS calibration sensitivity

`publication_selection` generates and verifies
`results/for_manuscript/tables/calibration_sensitivity.csv`. Notebook 01 calls this
through `generate_science`; notebook 04 verifies it. The existing independent
artifact comparison includes the new CSV, and CI already runs publication
selection and the regression suite. No comparison tolerance changes are needed.

The calculation adds the separately reported 0.5-dex scale to
RUBIES-EGS-55604 and J0910_2028_12910, and the 0.43-dex scale to J1007_AGN.
It assumes independent zero-mean Gaussian calibration errors. The two symmetric
reported-error models use exact normal tails. J1007 uses the catalogue's
equal-side half-normal errors, convolved with the added Gaussian by 96-node
Gauss-Legendre integration over ten standard deviations. Doubling the quadrature
order and an independent random-draw calculation check this result. The scalar
`reported_sigma_dex` and `combined_sigma_dex` fields are empty for J1007 because
its reported errors are asymmetric; the two reported scales have separate fields.
Baseline masses, Monte Carlo draws, membership and reported-error counts remain
unchanged. GN-38509 and ZS7 receive no additional scatter because their reported
errors already include it. The historical general draft retains the earlier
two-object subset; the Ap&SS edition includes the added J1007 sensitivity.

Run `.venv/bin/python -m unittest tests.test_calibration_sensitivity` for the
analytic-versus-sampling check and safeguards against double counting. The
standalone calculation also runs without importing the project:

```sh
.venv/bin/python -m src.internal.calibration_sensitivity \
  --input results/for_manuscript/tables/target_robustness.csv \
  --verify results/for_manuscript/tables/calibration_sensitivity.csv
```

The Ap&SS manuscript separately cites the calibration revision and the expanded
catalogue revision. The historical two-object result is preserved at
`77908cdaadb5898e5f2e1d2d353cf99d2a3a26ac`; the current three-object table is
generated by the tracked pipeline. These citations identify analysis versions;
scientific reproduction does not depend on local submission files.

## Current and historical presentation editions

The CUPC portrait and landscape posters now use the 17 October 2026 expanded
catalogue: 355 measurements, 343 provisional object records, 37 source families,
and publication samples of 223 primary and 238 expanded objects. Their scientific
inputs resolve directly to canonical tables and are pinned in
`data/poster_inputs.json`; both plot variants, editable text, and native-size PDF
exports were refreshed together. The four onset targets are CAPERS-LRD-z9,
UNCOVER-20466, CANUCS-LRD-z8.6, and GN-z11.

The preceding poster edition and its scientific inputs are recoverable from Git
revision `fc0c5501ad2271865b1c040307cad8dd8ca5721a`. Current posters use only
the canonical input paths pinned in `data/poster_inputs.json`. Both draft
manuscripts use the expanded results:
the general draft PDF/Overleaf ZIP and the journal-formatted Ap&SS source/PDF.
Manuscript PDFs and upload ZIPs must be rebuilt separately from the science
notebooks.

The expanded catalogue and scientific products are recorded at
`a1bef516db5c76a92b6848eb12bccabdeb5804b9`. The Ap&SS manuscript cites this
scientific revision separately from the calibration sensitivity revision.
The older two-object calibration calculation remains at
`77908cdaadb5898e5f2e1d2d353cf99d2a3a26ac`.
