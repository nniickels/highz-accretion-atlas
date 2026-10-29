# Publication analysis inputs

These files select the primary and expanded samples from v3 and define the
external comparisons. They do not change catalogue membership.

| File | Purpose |
| --- | --- |
| `identity_exclusions.json` | Excludes all six records in the three unresolved identity groups. |
| `evidence_selection.json` | Places four tentative JADES detections in the expanded sample only. |
| `review_inputs.json` | Records source caveats and external comparison measurements. Proposed observations are author suggestions. |

## Sample selection

The samples contain 223 primary and 238 expanded objects. Existing output fields
call the expanded sample `exploratory`; it contains every primary object.
Excluding uncertain identities does not resolve them.

The canonical method-primary sample has 230 objects. The evidence policy moves
GS-20057765, GS-20030333, GS-164055, and GN-4685 to the expanded sample only,
leaving 226 primary candidates before identity exclusions. Three mass-bearing
records in unresolved groups are then excluded, giving 223 primary objects.
The expanded sample removes those same three from 241 growth-eligible objects,
leaving 238. All six affected object records are excluded; three already lack
eligible masses. The [identity audit](../../docs/source-notes/redshift-identity-audit.md)
records their identities and the evidence needed to resolve them.

The expanded sample adds fourteen candidates and GN-z11 to the primary sample.
GN-z11 uses a UV virial estimator; the primary sample uses Balmer masses.
MACS0416-Y1 is expanded-only. These manuscript rules do not modify the original
catalogue flags or resolve physical identities.

## Identity-exclusion sensitivity

Holding the evidence policy fixed, the exclusions preserve primary/expanded
threshold counts of 11/17 at central mass, 9/13 at p16, and 8/11 for reported-error
P(f_Edd>1)>=0.95, together with scenario counts and top-five ordering. The primary
median requirement changes from 0.574202 to 0.574252. These statements use the
reference growth assumptions; they are not parameter-marginalized probabilities.

The [membership and sensitivity tables](../../results/v3/selected_samples/README.md)
record the full selection. In `identity_exclusion_sensitivity.csv`, the
`catalogue` scope means manuscript evidence selection before identity exclusions;
it is not the unfiltered method-primary sample. `publication` applies both
policies. Three catalogue identity groups remain unresolved.

## Generate and verify

From the repository root, after [setup](../../README.md#getting-started):

```bash
.venv/bin/python -m src.internal.publication_selection --write
.venv/bin/python -m src.internal.publication_selection
```

The first command writes the [publication tables](../../results/v3/selected_samples/README.md);
the second verifies them. Notebooks 01 and 04 perform these steps. Source
locations and assumptions remain in the inputs and output tables. The Dayal and
A2744-QSO1 comparisons do not add catalogue measurements.

## Calibration uncertainty

The separate three-object test and its error assumptions are described with the
[calibration results](../../results/v3/selected_samples/README.md#calibration-test).
The test does not change sample membership or catalogue masses.
