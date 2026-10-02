# highz-accretion-atlas
A standardized, assumption-tracked catalogue of JWST-identified high-redshift
($z \ge 4$) accreting massive-black-hole systems and candidates, and their
possible formation and growth scenarios.

**Manuscript:** in progress. A link will be added here once the paper is finalized.

## Repository map

- [`data/`](data/README.md): raw sources, processed catalogues, and identity products
- [`results/`](results/README.md): science tables, figures, galleries, and inventory
- [`docs/`](docs/README.md): methods, guides, and source notes
- [`src/`](src/README.md), [`scripts/`](scripts/README.md), and [`tests/`](tests/README.md): implementation, commands, and validation

## Workflow

I first build and implement the standardizing and growth-comparison scripts on a smaller dataset. Call this milestone of the project v1. v2 scales up the dataset but remains homogenous in terms of object class. v3 scales up again but with different object classes. v4 adds a focused primordial-seed growth analysis using the existing v3 catalogue.

| Version | Dataset | Measurements | Objects | Hosts |
| --- | --- | ---: | ---: | ---: |
| v1 | Original Juodzbalis et al. JADES BLAGN catalogue | 23 | 23 | 23 |
| v2 | v1 plus comparable JWST BLAGN sources with canonical masses | 218 | 211 | 210 |
| v3 | v2 plus heterogeneous JWST-identified candidates | 350 | 338 | 337 |
| v4 | Unchanged v3 catalogue; PBH growth extension for four selected targets | 350 | 338 | 337 |

The v4 counts describe its unchanged input catalogue; the focused analysis uses
four targets and adds no measurements, objects, or hosts.

For v1–v3, canonical catalogues are under
`data/processed/<version>/`, identity products are under
`data/crossmatch/<version>/`, and science tables, figures, and per-object
galleries are under `results/<version>/`. Source-specific raw files retain
descriptive publication names because they are immutable extractions.

**v4 — PBH growth extension:** a separate, focused analysis of the three most
constraining publication-primary objects plus GN-z11, using the existing v3
measurements. It tests the growth component of Dayal (2024) with equality and
delayed accretion onset, mass uncertainties, and stellar/heavy-seed controls.
It does not add catalogue sources or establish PBH formation/population viability.
See [v4 methods and limitations](docs/reference/pbh-growth-v4.md) and
[v4 outputs](results/v4/README.md).

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
only in notebook state. To reproduce the committed revision non-interactively,
use separate baseline and execution copies. Review and commit intended analysis
changes before running this command; uncommitted files are not included:

```bash
analysis_python="$PWD/.venv/bin/python"
baseline_root="$(mktemp -d "${TMPDIR:-/tmp}/highz-atlas-baseline.XXXXXX")"
reproduction_root="$(mktemp -d "${TMPDIR:-/tmp}/highz-atlas-reproduction.XXXXXX")"
executed_notebooks="$(mktemp -d "${TMPDIR:-/tmp}/highz-atlas-notebooks.XXXXXX")"
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

From the original repository root, run the complete regression and verification suite:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests
.venv/bin/python -m src.internal.verify_manual_extractions
.venv/bin/python -m src.internal.verify_primary_source_values
.venv/bin/python -m src.internal.verify_source_provenance
.venv/bin/python -m src.internal.verify_versions
.venv/bin/python -m src.internal.pbh_growth_v4 --verify
```

Generate the optional v4 extension with
`.venv/bin/python -m src.internal.pbh_growth_v4 --write` or
`scripts/05_pbh_growth_v4.ipynb`. This writes only `results/v4/`; the original
00–04 workflows retain their scope and do not regenerate v4.

The source review cutoff and explicit admission boundary are documented in
`docs/reference/literature-scope.md`; versioning details are in
`docs/guides/versioning.md`.

## Sources and interpretation

Catalogue citations and source limitations are documented in [data/sources.md](data/sources.md).
Publication sample policies are in [data/publication/](data/publication/README.md),
with reproducible tables and figures in [results/manuscript/](results/manuscript/README.md).
Reproducing the atlas does not require manuscript sources or a LaTeX installation.

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
