# Publication analysis inputs

These inputs define the publication analysis separately from canonical catalogue membership:

- `identity_exclusions.json`: excludes every record in the three unresolved identity groups.
- `evidence_selection.json`: retains four tentative JADES detections in the exploratory sample only.
- `review_inputs.json`: source-linked target caveats and external comparison measurements.
  Proposed observations are author suggestions, not source-reported observing plans.

The resulting samples contain 220 primary and 234 exploratory objects. These
policies neither alter the canonical catalogue nor resolve the open identities.

Run `python -m src.internal.publication_selection --write` to regenerate the
[analysis tables](../../results/publication/README.md); omit `--write` to verify them.
The external Dayal and A2744-QSO1 comparisons do not admit new catalogue measurements.
Source locators and assumptions remain in the JSON inputs and output tables.
