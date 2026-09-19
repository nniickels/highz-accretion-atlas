# highz-accretion-atlas
A standardized, assumption-tracked catalogue of JWST-identified high-redshift
($z \ge 4$) accreting massive-black-hole systems and candidates, and their
possible formation and growth scenarios.

**Manuscript:** read [Early Black-Hole Growth Constraints from JWST](paper/highz_accretion_atlas_v3.pdf).



## Workflow

Dataset versions describe nested scientific datasets, not software releases or
chronological development checkpoints. Every version uses the same latest
applicable corrections, identity rules, cosmology, growth model, uncertainty
propagation, comparison policy, and visual grammar.

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

Historical source-admission builders and the shared ranking/uncertainty core
remain under `src/internal/compatibility/`; their names do not define public
dataset versions or write legacy output trees.

## Getting Started

The project requires Python 3.12. Create a repository-local virtual environment
and install the pinned project requirements (including the explicit build backend).
The notebook lock covers the full dependency closure on Linux and macOS:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --requirement requirements-notebook-lock.txt --requirement requirements-build-lock.txt
.venv/bin/python -m pip check
```

Run the complete regression and verification suite:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests
.venv/bin/python -m src.internal.verify_manual_extractions
.venv/bin/python -m src.internal.verify_primary_source_values
.venv/bin/python -m src.internal.verify_source_provenance
.venv/bin/python -m src.internal.verify_versions
```

Full dataset generation commands are listed in the workflow above. The source
review cutoff and explicit admission boundary are documented in
`docs/reference/literature-scope.md`; versioning details are in
`docs/guides/versioning.md`.

## Repository map

Folder-level guides keep the data, results, documentation, releases, and code
easy to navigate:

- [`data/`](data/README.md): raw sources, processed catalogues, and identity products
- [`results/`](results/README.md): science tables, figures, galleries, and inventory
- [`docs/`](docs/README.md): contracts, methods, guides, and source notes
- [`releases/`](releases/README.md): exact dataset manifests and hashes
- [`src/`](src/README.md), [`scripts/`](scripts/README.md), and [`tests/`](tests/README.md): implementation, commands, and validation

## References

Catalogue data sources are documented authoritatively in `data/sources.md`.
The following is background and prospective reading, not a list of sources
currently represented by catalogue rows:

1. Dayal, P. 2024, [A&A](https://www.aanda.org/articles/aa/full_html/2024/10/aa51481-24/aa51481-24.html), 690, A182
2. Ji, X., Maiolino, R., Übler, H., et al. 2025, [MNRAS, 544, 3900](https://doi.org/10.1093/mnras/staf1867)
3. Maiolino, R., Übler, H., D’Eugenio, F., et al. 2025, [arXiv:2505.22567](https://arxiv.org/abs/2505.22567) 
4. Dayal, P. & Maiolino, R. 2025, [arXiv:2506.08116](https://doi.org/10.48550/arXiv.2506.08116)
5. Prole, L. R., Regan, J. A., Mehta, D., et al. 2025, [arXiv:2506.11233](https://arxiv.org/abs/2506.11233)
6. Adamo, A., Atek, Hakim., Bagley, M., et al. 2025, [arXiv:2405.21054](https://arxiv.org/abs/2405.21054)
7. Dayal, P. & Ferrara, A. 2018, [arXiv:1809.09136](https://arxiv.org/abs/1809.09136)
8. Stark, D., Topping, M., Endsley, R., et al. 2025, [arXiv:2501.17078](https://arxiv.org/abs/2501.17078)

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


The manuscript additionally excludes all six records linked to the three open
identity groups and retains four tentative JADES detections only in the
exploratory sample, giving 220 primary and 234 exploratory numerical objects.
The catalogue retains every source measurement and its provisional identity.
Notebook 01 reproduces the manuscript selection and sensitivity tables;
notebook 04 verifies them with `src.internal.publication_selection`.
This conservative analysis check does not replace the strict identity-resolution
gate. See [manuscript scope and reproduction](paper/README.md).
