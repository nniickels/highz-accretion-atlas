# v3 manuscript claim audit

| Manuscript claim | Machine evidence | Status |
| --- | --- | --- |
| 234 measurements / 219 objects / 218 hosts | v3 dataset manifest and verifier | verified |
| Scholtz table has 41 rows and 21 at `z >= 4` | focused claim regression, full-table parser, catalogue-builder cardinality assertions, and exact dataset reproduction | verified |
| JADES-NS-GS00099671 has no admitted numeric BH mass | focused claim regression, correction validator, canonical measurement row, and exact dataset reproduction | verified |
| 209 eligible measurements / 196 eligible objects | v3 dataset manifest and exact science reproduction | verified |
| 23 catalogue-only objects | v3 gallery coverage verifier | verified |
| 182/171 primary measurement/object rows | focused claim regression, canonical catalogue tables, and reproduction gate | verified |
| 13 alternate-measurement comparisons | focused claim regression, canonical science table, and reproduction gate | verified |
| Follow-up matrix contains 219 objects: 196 ranked and 23 explicitly unranked | canonical follow-up table and verifier | verified |
| Source-caveat summary contains one row for each of 11 admitted source families | canonical caveat table and verifier | verified |
| J1148+5251 is first in point and uncertainty navigation views | focused claim regression and canonical object ranking tables | verified |
| Top eight uncertainty entries have stored probability 1 for required `f_Edd > 1` | focused claim regression and canonical uncertainty table | verified |
| 438 per-object panels cover all 219 objects: 219 $f_{Edd}$-mass and 219 seed-redshift-mass panels | focused claim regression, v3 dataset manifest, and visual-coverage verifier | verified |
| Full-assumption v3 growth-track figure contains the historical v1 grid of 72 curves | focused assumption-grid regression and figure-resolution verifier | verified |
| Every combined growth-track figure uses the common observed-redshift range 10 to 3 without changing figure dimensions or margins | focused axis-range regression and generated figures | verified |
| Overview growth-track object colors encode broad-line AGN in purple and luminous quasars in red; full-assumption companions retain their pre-contrast palette | focused palette regression and generated figures | verified |
| Uncertainty-filtered full-assumption view excludes exactly four luminous quasars above the declared 0.7 dex mass-error threshold | focused selection regression, `v3_growth_track_uncertainty_filter.csv`, and figure-resolution verifier | verified |

Interpretive claims are deliberately bounded: ranks are navigation/descriptive,
the pooled catalogue is not demographic, and the growth model does not prove a
unique seed or accretion history.
