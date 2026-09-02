# Getting started

Use Python 3.12 with `requirements-notebook-lock.txt`, then execute the ordered
notebooks:

```bash
mkdir -p /tmp/highz-atlas-notebooks
.venv/bin/jupyter nbconvert --to notebook --execute --output-dir=/tmp/highz-atlas-notebooks scripts/00_process_catalogues.ipynb
.venv/bin/jupyter nbconvert --to notebook --execute --output-dir=/tmp/highz-atlas-notebooks scripts/01_generate_science.ipynb
.venv/bin/jupyter nbconvert --to notebook --execute --output-dir=/tmp/highz-atlas-notebooks scripts/02_generate_figures.ipynb
.venv/bin/jupyter nbconvert --to notebook --execute --output-dir=/tmp/highz-atlas-notebooks scripts/03_generate_atlas.ipynb
.venv/bin/jupyter nbconvert --to notebook --execute --output-dir=/tmp/highz-atlas-notebooks scripts/04_verify.ipynb
```

The notebooks call tested Python implementation under `src/internal/`. See
[`versioning.md`](versioning.md) and
[`../current/literature-scope.md`](../current/literature-scope.md).

The package metadata describes the Python workflow code used inside this source
repository, including the internal compatibility builders required for exact
catalogue reconstruction. Canonical data and results are repository artifacts,
not Python package data, so execute the workflow from a complete source checkout
rather than treating the built wheel as a standalone atlas distribution.
