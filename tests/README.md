# Test suite

Run from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests
```

The suite covers:

- `test_core_models.py`: numerical equations, scoring, and canonical v1 anchors
- `test_dataset_contracts.py`: exact v1/v2/v3 products and strict nesting
- `test_source_provenance.py`: source roles, versions, hashes, and review policy
- `test_repository_layout.py`: notebook/source boundaries, compiled manuscript, and complete paper products
- `test_scientific_claims.py`: headline v3 catalogue, correction, ranking, and coverage claims
- `test_independent_validation.py`: primary-source values, independent numerical integration, manuscript ranking, and missing-error handling

- `test_reproduction_gate.py`: changed scientific values, rendered pixels, and missing artifacts are rejected

CI additionally executes source-provenance verification, in-memory v1/v2/v3
catalogue/science/compatibility reproduction, and the full notebook workflow
with independent CSV and PNG comparisons before refreshing hashes.

`test_mass_review.py` checks complete numerical-mass coverage, Killi's linear
bounds, ZS7's included calibration scatter, and Baccus revision scenarios.

`test_manuscript_methods.py` checks primary-subset claims and independently
verifies the stated efficiency sensitivity against canonical results.

`test_redshift_identity.py` tests complete redshift/coordinate coverage, source
version pinning, rejection of altered source values and omitted identity pairs,
and the publication gate for unresolved identities.
