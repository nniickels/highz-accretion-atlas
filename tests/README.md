# Tests

Run the regression suite from the repository root after
[installing the pinned environment](../README.md#getting-started):

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests
```

## Coverage

| Test files | Checks |
| --- | --- |
| `test_core_models.py`, `test_dataset_contracts.py`, `test_scientific_claims.py` | Growth equations, catalogue membership, version relationships, and reported catalogue results. |
| `test_source_provenance.py`, `test_independent_validation.py`, `test_mass_review.py` | Source versions, recorded source values, numerical integration, and mass-error treatment. |
| `test_redshift_identity.py` | Redshift and coordinate coverage, close source matches, and rejection of unresolved identities when required. |
| `test_manuscript_methods.py`, `test_calibration_sensitivity.py` | Publication samples, efficiency sensitivity, and the separate calibration-scatter calculation. |
| `test_repository_layout.py` | Notebook/source boundaries and expected catalogue maps and tables. |
| `test_reproduction_gate.py`, `test_reproduction.py` | Rejection of changed values, pixels, and missing files; narrowly bounded numerical roundoff. |
| `test_pbh_v4.py` | Minimum seed masses, onset times, rate caps, mass errors, and regeneration of v4 results. |
| `test_manuscript_release.py` | Draft PDF/source-ZIP integrity, archive contents, packaging, and section order without LaTeX. |
| `test_poster_rebuild.py`, `test_poster_exports.py` | Poster text, citations, catalogue counts, plot pixels, reviewed layouts, and PDF/source pairing. |

The v4 tests also require an independent baseline for equivalent CSV files with
different encodings and reject changed scientific values or code. A regression
in the minimum-seed calculation has an absolute tolerance of 1e-13 dex; unrelated
columns and larger differences remain failures. PNG dimensions and transparency
must match exactly; pixel-channel tolerances are documented in the
[reproduction guide](../docs/guides/reproducibility.md#independent-comparison).

## Continuous integration

CI runs the suite, source checks, numerical reconstruction, figure verification,
poster checks, and a Python package build/import check. It also removes generated
outputs from a separate checkout, executes notebooks 00–04, and compares results
with the unchanged baseline before updating generated-file hashes.

The original local manuscript sources, cover letter, and compilation files are
excluded from Git. Tests allow the tracked draft PDF, Overleaf ZIP, and Ap&SS
submission package. Package-integrity checks and independent source checks serve
different purposes: matching stored outputs does not validate every physical assumption.
