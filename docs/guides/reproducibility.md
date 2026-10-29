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

Notebook 03 compares regenerated products with the independent baseline before
refreshing [data manifests](../../data/README.md#file-manifests). A baseline must
contain the same intended paths and inputs; comparison with the execution folder
itself, including through a symlink, is rejected.

For v4, CSV serialization may differ across platforms. The independent baseline
must match the pinned input hashes; regenerated CSV values are then compared
numerically. Code and non-CSV inputs remain byte-exact.

The comparison covers canonical v1/v2/v3 catalogues, identity products, science
results, and the CSV tables and PNG figures in `results/v3/selected_samples/`:

- CSV values use the shared numerical tolerance.
- PNG dimensions and alpha must match exactly. Every RGB channel of every pixel
  may differ by at most 3 out of 255, allowing measured cross-platform rendering
  roundoff. There is no averaging, resizing or alignment. Use `--exact-pixels`
  with `src.internal.verify_regenerated_artifacts` for identical renderers.
- Canonical figures have PNG exports only. Retained PDF verification fixtures
  are compared by decoded contents, allowing compression and object numbering to differ.
- Missing or unexpected artifacts fail verification.

CI removes generated artifacts in a disposable workspace, runs all five notebooks,
and compares the results against the original checkout. It also runs the regression
suite, source checks, publication figure verification, and a package build/import check.

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

The [identity verifier](../source-notes/redshift-identity-audit.md#executable-checks)
reports three unresolved groups. Its optional `--require-resolved` check currently
fails; the publication samples exclude the affected records.

## Intentional updates

Generation commands are listed with the [v3 result tables](../reference/catalogue-results.md),
[publication results](../../results/v3/selected_samples/README.md#generate-and-verify),
and [v4 outputs](../../results/v4/README.md#generate-and-verify).
Rebuild v1, v2, and v3 in order because later versions can reference earlier plots.

Inspect and explain changes against the reviewed baseline before refreshing hashes:

```bash
.venv/bin/python -m src.internal.dataset_manifests
.venv/bin/python -m src.internal.verify_source_provenance --write
```

A hash refresh records the current files; it does not demonstrate reproduction.
An intentional change needs a reviewed baseline containing that change before
the comparison can pass.

Canonical publication-figure and v4 exports refresh `results/results_inventory.csv`.
For other intentional result changes, run:

```bash
.venv/bin/python -m src.internal.build_results_inventory
```

The inventory records file sizes and hashes. Verification does not refresh it;
matching hashes does not replace independent reproduction.

Catalogue metadata edits can change the input hashes recorded by v4 and
`data/poster_inputs.json`. Check the affected scientific values before updating
those hashes, then rerun the v4 and poster checks below. Existing poster exports
can be retained when the plotted values are unchanged.

To reproduce the package build used by CI after installing the notebook lock:

```bash
SOURCE_DATE_EPOCH=1788393600 .venv/bin/python -m pip wheel . --no-deps --no-build-isolation --wheel-dir=/tmp/highz-wheels
```

## Posters and retained manuscript files

Current portrait and landscape PPTX/PDF pairs are in `posters/`. Scientific
inputs are pinned in `data/poster_inputs.json`; export hashes and slide/asset
fingerprints are in `data/poster_exports.json`.

```bash
.venv/bin/python -m src.internal.verify_poster_exports
.venv/bin/python -m src.internal.poster_figures --output-dir /tmp/highz-poster-figures
.venv/bin/python -m src.internal.package_overleaf --verify
```

Poster checks cover file integrity, page size, text-character coverage, fonts,
and regenerated scientific plots. They do not replace visual inspection of
layout. PDF exports are made separately from the analysis notebooks.
The manuscript command checks the general draft PDF/source-ZIP integrity and
section order without LaTeX or local authoring sources. It does not compile or
verify the Ap&SS manuscript.

The Ap&SS submission uses different highlighted targets in its growth tracks
and efficiency boundaries. Regenerate these two figure variants with
`.venv/bin/python -m src.internal.apss_figures`, or compare them with the local
submission PDFs using `.venv/bin/python -m src.internal.apss_figures --verify`.
The remaining figures use the canonical publication outputs. The Ap&SS source,
compiled PDF, and source-inventory rows (`paper/apss/tables/source_rows.tex`)
are tracked. The remaining figure, table, and class dependencies are local
submission files; include them when transferring or compiling the source.
Both drafts' source-inventory caveats must agree; the general draft's rows are
included in `paper/early_giants_overleaf.zip`.
