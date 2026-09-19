# highz-accretion-atlas
A standardized, assumption-tracked catalogue of JWST-identified high-redshift
($z \ge 4$) accreting massive-black-hole systems and candidates, and their
possible formation and growth scenarios.

**Manuscript:** in preparation. A download link will be added here when it is ready.

## Repository map

- [`data/`](data/README.md): raw sources, processed catalogues, and identity products
- [`results/`](results/README.md): science tables, figures, galleries, and inventory
- [`docs/`](docs/README.md): methods, guides, and source notes
- [`src/`](src/README.md), [`scripts/`](scripts/README.md), and [`tests/`](tests/README.md): implementation, commands, and validation

## Workflow

I first build and implement the standardizing and growth-comparison scripts on a smaller dataset. Call this milestone of the project v1. v2 scales up the dataset but remains homogenous in terms of object class. v3 scales up again but with different object classes. 

| Version | Dataset | Measurements | Objects | Hosts |
| --- | --- | ---: | ---: | ---: |
| v1 | Original Juodzbalis et al. JADES BLAGN catalogue | 23 | 23 | 23 |
| v2 | v1 plus comparable JWST BLAGN sources with canonical masses | 218 | 211 | 210 |
| v3 | v2 plus heterogeneous JWST-identified candidates | 350 | 338 | 337 |

For each version, canonical catalogues are under
`data/processed/<version>/`, identity products are under
`data/crossmatch/<version>/`, and science tables, figures, and per-object
galleries are under `results/<version>/`. Source-specific raw files retain
descriptive publication names because they are immutable extractions.

## Getting Started

The project requires Python 3.12. Create a repository-local virtual environment
and install the pinned environment, including Jupyter and the build backend.
The lock covers Linux and macOS:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --requirement requirements/notebook.txt
.venv/bin/python -m pip check
```

Use a complete source checkout: the Python wheel does not bundle the data or results.
For a core-only environment without Jupyter, install `requirements/core.txt`.

Run the numbered notebooks in `scripts/` from top to bottom. They call tested
Python modules under `src/internal/`; scientific implementation does not live
only in notebook state. To execute the complete workflow non-interactively:

```bash
mkdir -p /tmp/highz-atlas-notebooks
for notebook in scripts/0[0-4]_*.ipynb; do
  .venv/bin/python -m nbconvert --to notebook --execute \
    --ExecutePreprocessor.timeout=1800 \
    --output-dir=/tmp/highz-atlas-notebooks "$notebook" || exit 1
done
```

Run the complete regression and verification suite:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests
.venv/bin/python -m src.internal.verify_manual_extractions
.venv/bin/python -m src.internal.verify_primary_source_values
.venv/bin/python -m src.internal.verify_source_provenance
.venv/bin/python -m src.internal.verify_versions
```

The source review cutoff and explicit admission boundary are documented in
`docs/reference/literature-scope.md`; versioning details are in
`docs/guides/versioning.md`.

## Sources and interpretation

Catalogue citations and source limitations are documented in [data/sources.md](data/sources.md).
Publication sample policies are in [data/publication/](data/publication/README.md),
with reproducible tables and figures in [results/manuscript/](results/manuscript/README.md).
The manuscript is edited separately in Overleaf; reproducing the atlas does not
require manuscript sources or a LaTeX installation.

Reproduction compares regenerated CSV values and PNG pixels with an independent
baseline before refreshing hashes; see [reproduction and intentional updates](docs/guides/reproducibility.md).
Independent source fixtures cover all 32 families with 2,041 field checks;
all 244 numerical masses and both error bounds are independently checked.
The separate redshift/identity fixture checks all central redshifts and available
coordinates but reports three unresolved identity groups. Other observable fields
retain representative coverage. See the
[validation scope and extension requirements](data/validation/README.md) and
[scientific limits](docs/reference/science-policy.md); passing CI does not imply
a complete source audit or permit population-demographic claims.
