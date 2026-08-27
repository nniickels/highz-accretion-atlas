# Contributing

Use Python 3.12 and install `requirements-lock.txt` into `.venv`. Keep source
extractions immutable and source-specific; introduce corrections in a new
release rather than rewriting a frozen artifact.

Before submitting a change:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests
.venv/bin/python -m scripts.verify_v7_5_catalogue --reproduce
.venv/bin/python -m scripts.verify_v7_5_science --reproduce
.venv/bin/python -m scripts.verify_v7_5_figures
```

New data must include source/version provenance, a deterministic admission
adapter, identity review where needed, regression anchors, and a release
manifest. Do not pool heterogeneous source families for demographic inference
without an explicit selection/completeness model.
