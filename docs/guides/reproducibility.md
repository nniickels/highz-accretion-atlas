# Reproducing results

Install the pinned environment and run notebooks 00–04 as described in the
[root README](../../README.md#getting-started). `requirements/core.txt` pins the
numerical and rendering dependencies; `requirements/notebook.txt` includes
those pins, Jupyter and the build backend. Python 3.12 on Linux and macOS is supported.

## Independent comparison

Notebook 03 compares regenerated products against Git HEAD before refreshing
[data manifests](../../data/manifests/README.md). In a separate workspace, set
`HIGHZ_BASELINE_ROOT` to an independent checkout containing the reviewed outputs.
Comparing a workspace with itself, including through a symlink, is rejected.
A directory reorganization must first be committed or use an independent
baseline with the same paths; an older HEAD with different paths cannot match.

The comparison covers canonical v1/v2/v3 catalogues, identity products, science
results, and the CSV tables and PNG/PDF figures in `results/publication/`:

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
Manuscript editing and compilation take place separately in Overleaf.

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

To reproduce the package build used by CI after installing the notebook lock:

```bash
SOURCE_DATE_EPOCH=1788393600 .venv/bin/python -m pip wheel . --no-deps --no-build-isolation --wheel-dir=/tmp/highz-wheels
```
