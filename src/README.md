# Source code

The public modules define catalogue access, growth models, and analysis methods.
Notebook drivers and file-generation tools are in `internal/`.

## Public modules

| Module | Purpose |
| --- | --- |
| `datasets.py` | Catalogue membership, table generation, and version metadata. |
| `science.py` | Growth rankings, uncertainties, duty cycles, and follow-up tables. |
| `models.py` | Cosmology and black-hole growth equations. |
| `pbh.py` | Minimum seed masses and growth tests for the v4 analysis. |
| `scoring.py` | Growth compatibility and ranking scores. |
| `identity.py` | Stable identifiers and candidate source matches. |
| `object_taxonomy.py` | Object classes, observed properties, evidence labels, and analysis eligibility. |
| `mass_systematics.py` | Mass-estimation methods and their systematic uncertainties. |
| `source_provenance.py` | Source-version and file-integrity checks. |
| `standardize_data.py` | Conversion of source tables to the shared schema. |

A duty cycle is the fraction of time spent accreting. Growth compatibility means
that a specified history can reach the adopted mass under its stated assumptions;
it does not identify the seed's origin. The catalogue browsing score is separate
from the required-accretion-rate ranking; see the
[score guide](../docs/guides/catalogue-navigation-score.md).

## Workflow tools

- `internal/compatibility/` contains source-admission builders and the shared
  ranking and uncertainty code in `v7_science_core.py`. The historical `v7_*`
  filenames do not define public catalogue versions.
- `internal/verify_redshift_identity.py` checks reported redshifts, available
  coordinates, and close source matches. `--require-resolved` also requires the
  open identity groups to be resolved; the manuscript samples exclude them.
- `internal/pbh_growth_v4.py` generates and verifies v4 outputs and updates the
  shared results inventory when writing to the standard results folder.
- `internal/package_overleaf.py` packages the local manuscript source.
  Its `--verify` mode checks the public draft PDF and source ZIP without LaTeX
  or local manuscript files.
- `internal/poster_figures.py`, `poster_layout.py`, and
  `verify_poster_exports.py` rebuild poster figures, preserve reviewed layouts,
  and check PowerPoint/PDF pairs.

Use the [notebooks](../scripts/README.md) for the complete analysis and the
[reproduction guide](../docs/guides/reproducibility.md) for command-line checks.
