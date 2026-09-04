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

The required-Eddington-ratio order differs from the composite navigation score.
The latter combines two normalized growth diagnostics and a redshift term (see
`_pressure_score` in `src/internal/compatibility/v7_science_core.py` and the
manuscript formula). The manuscript top-five table sorts by
`required_fedd_seed1e2`: GS-20057765 is third; COSMOS3D-13852 is fourth but third
in composite navigation order.

Twelve NEXUS masses have no reported statistical errors. Their repeated point
values in the uncertainty CSVs have `mbh_uncertainty_mode` equal to
`point_estimate_no_reported_mbh_error`. Probabilities and uncertainty ranks are
unavailable; zero-width intervals are not statistical certainty. Summary plots put these objects in a
separate "No error" row; the full uncertainty atlas uses open diamonds. The
other 225 objects use equal-probability half-normal draws on each side of the
central mass, scaled by the reported error. This approximates intervals, not
source posteriors.

Baseline ranks, duty cycles, and seed-redshift maps use epsilon=0.1. Growth
tracks retain their stated constant efficiencies. Spin-separated Eddington-ratio
maps and compatibility matrices use ideal Kerr thin-disk efficiencies below
unity and `epsilon_eff = epsilon_spin*f*exp(1-f)` above unity. This illustrative
photon-trapping rule assumes `f=1+ln(mdot)`, with accretion rate normalized by
`L_Edd/(epsilon_spin*c^2)`. It is not a relativistic slim-disk or spin-evolution
solution. Comparisons must preserve the distinction between these products.

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
