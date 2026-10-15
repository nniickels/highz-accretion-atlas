# Reproducing results

Install the pinned environment and run notebooks 00–04 as described in the
[root README](../../README.md#getting-started). `requirements/core.txt` pins the
numerical and rendering dependencies; `requirements/notebook.txt` includes
those pins, Jupyter and the build backend. Python 3.12 on Linux and macOS is supported.

## Independent comparison

The root README's command creates independent baseline and execution archives
of the same committed revision, retains the original environment's Python path,
and sets `HIGHZ_BASELINE_ROOT` before running notebooks 00–04 and v4 verification.
The archives omit uncommitted changes. Return to the original repository root
before running commands that use `.venv/bin/python`.

Notebook 03 compares regenerated products against Git HEAD before refreshing
[data manifests](../../data/manifests/README.md). In a separate workspace, set
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
The authoritative local source is `paper/main.tex`, with a
compiled PDF and synchronized Overleaf ZIP. The generic manuscript PDF and Overleaf ZIP are tracked alongside the Ap&SS
submission package in `paper/apss/`. The Ap&SS source, PDF, upload archives,
supplementary calculation, and rebuild/integrity records are tracked. Its cover
letter and compilation intermediates remain ignored. The original local sources
elsewhere under `paper/` remain ignored.
Overleaf receives the packaged local sources; it is not a separate authoritative
editing target. Run `python3 -m src.internal.package_overleaf` to build the
manuscript-only upload ZIP from the local sources after compiling and copying
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
tentative JADES detections in the exploratory sample only, yielding 220 primary
and 234 exploratory objects. See the [identity audit](../source-notes/redshift-identity-audit.md).

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

The final portrait and landscape PPTX sources and their reviewed PDF exports
are tracked in `posters/`. The editable decks are authoring inputs: wording and
layout are reviewed manually, while the scientific figures are generated from
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

`data/poster_exports.json` binds each PDF to the exact reviewed PPTX with SHA-256
hashes. Verification checks these hashes, one-page dimensions, text-character
coverage, and embedded fonts. Character coverage tolerates exporter differences
in text order and whitespace; it is not a semantic or visual-layout comparison.
The byte hashes reject changes even if character counts happen to stay equal.

PDFs are manually exported presentation artifacts, not byte-identical outputs
of the scientific pipeline. The current portrait was exported through macOS
Quartz (PDF 1.4), and the landscape is PDF 1.7; both were visually reviewed at
their full page sizes. Font versions, export applications, metadata, and PDF
encodings can differ across systems. After changing a PPTX, export a one-page
PDF at its native size (portrait 36 × 48 inches, landscape 48 × 36 inches),
inspect the actual PDF for text fit, symbols, images and font embedding, then
update only that reviewed pair's hashes. Do not refresh hashes to bypass a
failure. No automatic PDF exporter or printer-specific bleed profile is implied.
The verifier runs in CI; no local authoring runtime is required there.
The current Quartz portrait contains unused zero-offset cross-reference entries;
`pypdf` warns and ignores them. They have no object references, all checked text
and fonts are present, and independent Poppler rendering succeeded. Verification
does not rewrite or silently repair the reviewed PDF.

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

The tracked Ap&SS submission supplies the calculation, reference table, result,
and dependency pins in a separate supplementary ZIP. Its package manifest records
these files and the revised manuscript. The existing 9584a7d05b59 reference pins
the baseline implementation and figures; it does not contain this added test.
