# Class-aware science policy

The current science layer consumes only the canonical v3 measurement and
physical-object tables. It produces separate point and 10,000-draw uncertainty
rankings for both views, a class/method summary, a complete exclusion audit,
alternate-measurement sensitivity, a class-aware observational follow-up
matrix, a source-family caveat summary, a source-level selection/completeness
summary, and an executable science-policy table.

Supported interpretation scopes are:

- within object class;
- within mass-comparability group;
- within object class and mass-comparability group (primary); and
- a global navigation order with no cross-class scientific claim.

Pooled demographic inference is forbidden. The machine-readable selection
registry leaves inverse weights unset unless a valid inclusion-probability model
exists; none currently does. Statistical mass errors are sampled
without combining them with method systematics. The 209-row exclusion audit is
the union of 106 ineligible measurement rows and 103 ineligible object rows; all
remain in the catalogue.

`results/v3/tables/v3_followup_priority.csv` contains all 340 objects. Its 237
growth-eligible rows receive both within-class and navigation-only ranks; the
103 objects without a method-comparable canonical mass remain explicitly
unranked. `v3_source_caveat_summary.csv` contains one row for each of the 32
admitted source families.

Reproduce with:

```bash
mkdir -p /tmp/highz-atlas-notebooks
.venv/bin/jupyter nbconvert --to notebook --execute --output-dir=/tmp/highz-atlas-notebooks scripts/01_generate_science.ipynb
.venv/bin/jupyter nbconvert --to notebook --execute --output-dir=/tmp/highz-atlas-notebooks scripts/04_verify.ipynb
```
