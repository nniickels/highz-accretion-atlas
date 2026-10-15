# Publication analysis inputs

These files select the manuscript samples from the catalogue and define the
external comparisons. They do not change catalogue membership.

| File | Purpose |
| --- | --- |
| `identity_exclusions.json` | Excludes all six records in the three unresolved identity groups. |
| `evidence_selection.json` | Places four tentative JADES detections in the expanded sample only. |
| `review_inputs.json` | Records source caveats and external comparison measurements. Proposed observations are author suggestions. |

The samples contain 220 primary and 234 expanded objects. Existing output fields
call the expanded sample `exploratory`; it contains every primary object.
Excluding uncertain identities does not resolve them.

## Generate and verify

From the repository root, after [setup](../../README.md#getting-started):

```bash
.venv/bin/python -m src.internal.publication_selection --write
.venv/bin/python -m src.internal.publication_selection
```

The first command writes the [publication tables](../../results/for_manuscript/README.md);
the second verifies them. Notebooks 01 and 04 perform these steps. Source
locations and assumptions remain in the inputs and output tables. The Dayal and
A2744-QSO1 comparisons do not add catalogue measurements.

## Calibration uncertainty

The separate calibration test uses the adopted measurement IDs and uncertainty
scales already recorded for RUBIES-EGS-55604 and J0910_2028_12910. It adds their
separately reported 0.5-dex scales to symmetric mass errors under the assumptions
in the [reproduction guide](../../docs/guides/reproducibility.md#apss-calibration-sensitivity).
The implementation rejects different measurement IDs, asymmetric errors, or
changed scales until those assumptions are reviewed.
