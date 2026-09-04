# Class-aware science policy

The current science layer consumes only the canonical v3 measurement and
physical-object tables. It produces separate point and 10,000-draw uncertainty
rankings for both views, a class/method summary, a complete exclusion audit,
alternate-measurement sensitivity, a class-aware observational follow-up
matrix, a source-family caveat summary, and an executable science-policy table.

Supported interpretation scopes are:

- within object class;
- within mass-comparability group;
- within object class and mass-comparability group (primary); and
- a global navigation order with no cross-class scientific claim.

Pooled demographic inference is forbidden. Statistical mass errors are sampled
without combining them with method systematics. The 200-row exclusion audit is
the union of 101 ineligible measurement rows and 99 ineligible object rows; all
remain in the catalogue.

`results/v3/tables/v3_followup_priority.csv` contains all 311 objects. Its 212
growth-eligible rows receive both within-class and navigation-only ranks; the
99 objects without a method-comparable canonical mass remain explicitly
unranked. `v3_source_caveat_summary.csv` contains one row for each of the 29
admitted source families.

Reproduce with:

```bash
mkdir -p /tmp/highz-atlas-notebooks
.venv/bin/jupyter nbconvert --to notebook --execute --output-dir=/tmp/highz-atlas-notebooks scripts/01_generate_science.ipynb
.venv/bin/jupyter nbconvert --to notebook --execute --output-dir=/tmp/highz-atlas-notebooks scripts/04_verify.ipynb
```
