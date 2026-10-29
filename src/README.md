# Source code

Public modules provide catalogue version materialization (`datasets.py`), growth equations
(`models.py`, `pbh.py`), and analysis (`science.py`, `scoring.py`). Supporting
modules handle identities, classifications, mass systematics, source provenance,
and standardization.

Read the released CSVs directly; the [data guide](../data/README.md#example-select-the-manuscript-sample)
shows how to select the reviewed sample. `catalogue_quality.py` normalizes
boolean flags, updates adoption explanations, and attaches identity/provenance diagnostics.

Notebook drivers and generation/verification commands are in `internal/`.
Historical `v7_*` filenames under `internal/compatibility/` support reconstruction;
they do not identify additional catalogue versions.

Use the [notebooks](../scripts/README.md) for the complete workflow and the
[reproduction guide](../docs/guides/reproducibility.md) for verification commands.
The [model guide](../docs/reference/model-menu.md),
[data field guide](../data/README.md#columns-units-and-missing-values), and
[result guide](../docs/reference/catalogue-results.md) explain the scientific inputs
and outputs.
