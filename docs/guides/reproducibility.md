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
results, and the CSV tables and PNG/PDF figures in `results/for_manuscript/`:

- CSV values use the shared numerical tolerance.
- PNG dimensions and alpha must match exactly. Every RGB channel of every pixel
  may differ by at most 3 out of 255, allowing measured cross-platform rendering
  roundoff. There is no averaging, resizing or alignment. Use `--exact-pixels`
  with `src.internal.verify_regenerated_artifacts` for identical renderers.
- PDFs must have identical decoded contents, including drawing commands, fonts,
  image samples, geometry and properties. Compression and object numbering may differ.
- Missing or unexpected artifacts fail verification.

CI removes generated artifacts in a disposable workspace, runs all five notebooks,
and compares the results against the original checkout. It also runs the regression
suite, source checks, publication figure verification, and a package build/import check.
Manuscript editing and compilation are separate from the analysis pipeline.
Both draft editions use the current expanded catalogue. The journal-formatted
source and PDF are tracked as `paper/apss/main.tex` and `paper/apss/main.pdf`.
The general draft is tracked as `paper/early_giants_draft.pdf` and its synchronized
`paper/early_giants_overleaf.zip`; their local source is `paper/main.tex`.
Other files in `paper/apss/` are local and Git-ignored, including figure/table
copies, upload archives, rebuild scripts, integrity records, and the cover letter.
A fresh checkout can read the Ap&SS source and PDF but cannot compile that source
without restoring its local dependencies. Scientific code, canonical data,
calibration calculations, and generated scientific results remain tracked.
The original local manuscript sources elsewhere under `paper/` remain ignored.
For the general draft, Overleaf receives the packaged local sources;
it is not a separate authoritative editing target. Run
`python3 -m src.internal.package_overleaf` to build that edition's
manuscript-only upload ZIP from its local sources after compiling and copying
`paper/previews/main.pdf` to `paper/early_giants_draft.pdf`. This optional packaging
command requires the local source. CI runs the read-only `--verify` command
against the public ZIP and PDF without requiring local manuscript files or TeX.
It checks source and PDF hashes, dependency membership, and that references precede
appendices with both starting on new pages. The ZIP uses fixed entry timestamps
and contains no Ap&SS files or private working materials. These release-integrity
checks are separate from scientific artifact regeneration; the compiler-produced
draft PDF is not required to regenerate byte-for-byte across platforms.
The local `paper/README.md` documents compilation and packaging.

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
verifier checks both PNG and PDF exports against newly rendered figures.

Source-value checks have the bounded coverage described in the
[validation guide](../../data/validation/README.md). Reproduction agreement is
not a substitute for independent source evidence.

Three identity groups remain unresolved. The ordinary redshift/identity verifier
reports them; `--require-resolved` is the strict full-catalogue gate and currently
fails. The publication samples exclude all six affected records and place four
tentative JADES detections in the exploratory sample only, yielding 223 primary
and 238 exploratory objects. See the [identity audit](../source-notes/redshift-identity-audit.md).

## Intentional updates

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

`publication_selection` now also generates and verifies
`results/for_manuscript/tables/calibration_sensitivity.csv`. Notebook 01 calls this
through `generate_science`; notebook 04 verifies it. The existing independent
artifact comparison includes the new CSV, and CI already runs publication
selection and the regression suite. No comparison tolerance changes are needed.

The calculation adds the separately reported 0.5-dex scale only to
RUBIES-EGS-55604 and J0910_2028_12910. It assumes an independent zero-mean
Gaussian calibration error and uses exact normal probabilities, since both
reported errors are symmetric. It does not change baseline masses, Monte Carlo
draws, sample membership, or existing results. GN-38509 and ZS7 receive no
additional scatter because their reported errors already include it.

Run `.venv/bin/python -m unittest tests.test_calibration_sensitivity` for the
analytic-versus-sampling check and safeguards against double counting. The
standalone calculation also runs without importing the project:

```sh
.venv/bin/python -m src.internal.calibration_sensitivity \
  --input results/for_manuscript/tables/target_robustness.csv \
  --verify results/for_manuscript/tables/calibration_sensitivity.csv
```

The Ap&SS manuscript cites repository commit
`77908cdaadb5898e5f2e1d2d353cf99d2a3a26ac`, which contains the calibration
code, input and result tables, dependency versions, and reproduction commands.
The submission uses this repository reference instead of duplicate supplementary
files. When the local submission package is available, its optional integrity checker
compares the current figures and analysis files against the expanded scientific
revision below, while retaining the separate calibration citation. Scientific
reproduction uses the tracked analysis pipeline and does not require these local
presentation files.

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
scientific revision separately from the unchanged calibration calculation at
`77908cdaadb5898e5f2e1d2d353cf99d2a3a26ac`.
