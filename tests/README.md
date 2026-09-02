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

CI additionally executes source-provenance verification and exact in-memory
v1/v2/v3 catalogue and science reproduction.
