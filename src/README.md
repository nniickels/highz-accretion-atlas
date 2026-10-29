# Source code

`datasets.py` builds the catalogue versions. `models.py` and `pbh.py` implement
the growth equations; `science.py` and `scoring.py` produce analysis tables and
scores. Other modules handle object identities, classifications, mass
systematics, source records, and unit conversions.

Read the released CSVs directly; the [data guide](../data/README.md#example-select-the-manuscript-sample)
shows how to select the manuscript sample. `catalogue_quality.py` standardizes
boolean flags, updates measurement-choice explanations, and adds source and
identity checks.

Notebook drivers and generation/verification commands are in `internal/`.

Use the [notebooks](../scripts/README.md) for the complete workflow and the
[reproduction guide](../docs/guides/reproducibility.md) for verification commands.
The [model guide](../docs/reference/model-menu.md),
[data field guide](../data/README.md#columns-units-and-missing-values), and
[result guide](../docs/reference/catalogue-results.md) explain the scientific inputs
and outputs.
