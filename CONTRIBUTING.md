# Contributing

Use Python 3.12 and install `requirements-notebook-lock.txt` into `.venv`. Keep source
extractions immutable and source-specific; introduce corrections in a new
processing-layer change rather than rewriting a frozen raw artifact. Accuracy
corrections regenerate every affected dataset; new literature membership
creates a new dataset version.

Before submitting a change:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests
.venv/bin/python -m src.internal.verify_source_provenance
.venv/bin/python -m src.internal.verify_versions
```

New data must include source/version provenance, a deterministic admission
adapter, identity review where needed, regression anchors, and a dataset
manifest. New literature membership creates a new dataset version rather than
mutating v3. Do not pool heterogeneous source families for demographic inference
without an explicit selection/completeness model.

Update `data/source_provenance_registry.csv` when a source version,
publication status, DOI, dataset DOI, or supporting-source role changes. Use a
new provenance row when one catalogue family draws on multiple sources. Never
use a provenance supplement to imply an unknown historical extraction date or
silently rewrite a frozen catalogue value.
