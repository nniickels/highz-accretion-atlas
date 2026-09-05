# Source package

Public scientific code is organized by responsibility, not by former software
release number.

## Canonical interfaces

- `datasets.py`: v1/v2/v3 membership, materialization, and canonical metadata
- `science.py`: shared rankings, uncertainty, duty-cycle, follow-up, and caveat products
- `models.py`: cosmology and black-hole growth equations
- `scoring.py`: compatibility and ranking scores
- `identity.py`: stable identities and match candidates
- `object_taxonomy.py`: evidence, class, phenotype, and eligibility vocabulary
- `mass_systematics.py`: source-method systematic registry
- `source_provenance.py`: provenance validation
- `standardize_data.py`: source-table standardization

## Internal workflow

`internal/` contains deterministic catalogue, science, figure, atlas, manifest,
inventory, extraction, and verification helpers called by the notebooks in
`scripts/`.

`internal/compatibility/` retains source-admission builders that reconstruct the
complete catalogue from `data/assembly/`, and `v7_science_core.py`, the shared
ranking and uncertainty implementation called by `science.py`. Its historical
`v7_*` names are implementation history, not public dataset versions or supported
user entry points. Public workflow commands remain the numbered notebooks.

`internal/verify_redshift_identity.py` checks complete admitted redshift/coordinate
coverage and all close identity pairs. Its report distinguishes source-value
agreement from unresolved astrophysical identities; `--require-resolved` is the
publication identity gate.
