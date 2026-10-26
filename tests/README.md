# Tests

From the repository root after [setup](../README.md#getting-started):

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests
```

The suite covers growth equations, catalogue membership and identities,
source-value checks, uncertainty treatment, sample selection, result regeneration,
shared figures, and poster/PDF integrity. Manuscript checks use retained files
without requiring private authoring inputs or LaTeX.

CI also rebuilds results in a separate workspace, compares them with an unchanged
baseline, and checks the Python package build/import. See the
[reproduction guide](../docs/guides/reproducibility.md) for commands and comparison
tolerances, and [validation coverage](../data/validation/README.md) for the limits
of independent source checks.
