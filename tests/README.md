# Test Suite Guide

Run the complete regression suite from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests
```

## Test groups

- `test_v1_v2_pipeline.py`: core models, standardization, scoring, and uncertainty
- `test_v3_*` through `test_v6_*`: frozen BLAGN catalogue/science releases
- `test_v7_admission.py`, `test_v7_batch.py`, and `test_v7_ren_admission.py`:
  generalized admission, batching, identity, and source-family rules
- `test_v7_catalogue.py` through `test_v7_4_growth_products.py`: successive v7 layers
- `test_v7_5_catalogue.py`, `test_v7_5_science.py`, `test_v7_5_figures.py`, and
  `test_v7_5_publication.py`: current integrated release
- `test_source_provenance.py`: source roles, versions, hashes, and review policy
- `test_maintenance_release.py`: manifest scope and strict reproduction behavior

CI additionally runs every release verifier with `--require-clean`; passing the
unit suite alone is not the complete release gate.

