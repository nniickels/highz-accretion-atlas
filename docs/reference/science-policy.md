# Class-aware science policy

The shared science layer consumes the canonical measurement and physical-object
tables for each of v1, v2, and v3. The counts below describe v3. It produces separate point and 10,000-draw uncertainty
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
exists; none currently does. Source-reported mass errors are sampled
without adding separate method systematics. ZS7's published 0.4-dex error
already includes calibration scatter and is retained once. Other reported
errors are not assumed to have purely statistical components. The 209-row exclusion audit is
the union of 106 ineligible measurement rows and 103 ineligible object rows; all
remain in the catalogue.

The required-Eddington-ratio order differs from the composite navigation score.
The latter combines two normalized growth diagnostics and a redshift term (see
`_pressure_score` in `src/internal/compatibility/v7_science_core.py` and the
manuscript formula). The manuscript top-five table sorts by
`required_fedd_seed1e2`: GS-20057765 is third; COSMOS3D-13852 is fourth but third
in composite navigation order.

Twelve NEXUS masses have no reported mass errors. Their repeated point
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

## Scientific limits and what would change them

The frozen atlas supports descriptive, within-class comparisons and conditional
growth calculations. These limits do not prevent manuscript development, but
must accompany interpretation of the results:

| Limit | Current interpretation | Requirement for an extension |
| --- | --- | --- |
| Fixed growth assumptions | Reported-error probabilities hold at the stated seed mass/redshift, efficiency, merger factor and cosmology; they are not model-marginalized probabilities or probabilities of a seed origin. | Define justified parameter distributions and correlations, then propagate them jointly. Existing scenario maps illustrate sensitivity; they do not marginalize it. |
| Approximate mass-error distributions | Equal-side half-normal draws reproduce quoted scales approximately, not full source posteriors. Method envelopes remain separate; twelve objects lack reported errors. | Obtain posterior information or justify and test alternative error models, including shared calibration effects. Never turn absent errors into certainty. |
| Heterogeneous selection | Counts and navigation ranks describe the admitted sample; population fractions, number densities and seed-channel frequencies are unsupported. | Validate source-specific inclusion probabilities and parent populations, account for survey overlap, and only then enable the demographic gate. Missing selection information cannot be repaired by assigning arbitrary weights. |
| Partial non-mass source audit | Reproduction is verified, but not every source field or identity has been independently re-read. | Extend the fixtures under the criteria in `data/validation/README.md`, prioritizing redshifts and identities. |
| Frozen measurement membership | Known new measurements, including the A2744-QSO1 direct-mass result, are not silently substituted into v1/v2/v3. | Follow the next-version admission work in `literature-scope.md`; distinguish new measurements from corrections to existing extracted values. |

The growth law also compresses time-dependent feedback and accretion into
average parameters. The ideal-spin endpoints and photon-trapping coupling are
illustrative assumptions, and the age expression is a flat matter-plus-Lambda
approximation without radiation. Passing numerical integration tests validates
implementation of those equations, not their adequacy for every physical model.
