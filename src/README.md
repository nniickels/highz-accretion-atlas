# Source code

Public modules provide catalogue access (`datasets.py`), growth equations
(`models.py`, `pbh.py`), and analysis (`science.py`, `scoring.py`). Supporting
modules handle identities, classifications, mass systematics, source provenance,
and standardization.

Notebook drivers and generation/verification commands are in `internal/`.
Historical `v7_*` filenames under `internal/compatibility/` support reconstruction;
they do not identify additional catalogue versions.

Use the [notebooks](../scripts/README.md) for the complete workflow and the
[reproduction guide](../docs/guides/reproducibility.md) for verification commands.
The [model guide](../docs/reference/model-menu.md),
[data field guide](../data/README.md#columns-units-and-missing-values), and
[result guide](../docs/reference/catalogue-results.md) explain the scientific inputs
and outputs.
