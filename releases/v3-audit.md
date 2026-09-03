# v3 release audit

| Manuscript claim | Machine evidence | Status |
| --- | --- | --- |
| 258 measurements / 249 objects / 248 hosts | v3 dataset manifest and verifier | verified |
| Scholtz table has 41 rows and 21 at `z >= 4` | focused claim regression, full-table parser, catalogue-builder cardinality assertions, and exact dataset reproduction | verified |
| JADES-NS-GS00099671 has no admitted numeric BH mass | focused claim regression, correction validator, canonical measurement row, and exact dataset reproduction | verified |
| 160 eligible measurements / 153 eligible objects | v3 dataset manifest and exact science reproduction | verified |
| 96 catalogue-only objects | v3 gallery coverage verifier | verified |
| 152/145 primary measurement/object rows | focused claim regression, canonical catalogue tables, and reproduction gate | verified |
| 7 alternate-measurement comparisons | focused claim regression, canonical science table, and reproduction gate | verified |
| Follow-up matrix contains 249 objects: 153 ranked and 96 explicitly unranked | canonical follow-up table and verifier | verified |
| Source-caveat summary contains one row for each of 25 admitted source families | canonical caveat table and verifier | verified |
| UNCOVER-20466 leads both point and uncertainty navigation views | focused claim regression and canonical object ranking tables | verified |
| 498 per-object panels cover all 249 objects: 249 $f_{Edd}$-mass and 249 seed-redshift-mass panels | focused claim regression, v3 dataset manifest, and visual-coverage verifier | verified |
| Full-assumption v3 growth-track figure contains the historical v1 grid of 72 curves | focused assumption-grid regression and figure-resolution verifier | verified |
| Every combined growth-track figure uses the common observed-redshift range 12 to 3 without changing figure dimensions or margins | focused axis-range regression and generated figures | verified |
| Overview growth-track object colors encode broad-line AGN in purple; the full-assumption companion uses blue numerical points with blue/gray no-mass groups | focused palette regression and generated figures | verified |

Interpretive claims are deliberately bounded: ranks are navigation/descriptive,
the pooled catalogue is not demographic, and the growth model does not prove a
unique seed or accretion history.

## Release-specific evidence decisions

The Scholtz et al. paper reports 42 objects, while its source-native sample
table contains 41 rows. The checked-in full table contains exactly 21 rows at
`z >= 4`; all 21 are included, and no black-hole mass is inferred for
JADES-NS-GS00099671.

Exactly one preferred measurement controls object-level evidence status while
all measurement-level statuses remain visible. This leaves the secure JADES
8083 measurement primary and retains its candidate alternate. UHZ1 remains
disputed because its preferred full-data reanalysis is disputed.

## Manuscript citation audit

The manuscript cites all 25 admitted source families:

- Juodžbalis, Taylor, Matthee, Lin, Harikane, Davis, Ren, Greene, Kocevski,
  Skyfire, Larson, Killi, and Übler broad-line samples
- Bogdán and Zou for the UHZ1 evidence history
- Scholtz for the JADES narrow/high-ionization candidates
- Maiolino for GN-z11
- Chisholm, Tang, Mazzolari, Zhang, and Chavez Ortiz for the expanded
  high-ionization and narrow-line families
- Leung/MEOW and Lyu/SMILES for MIRI-selected candidates
- Napolitano for GHZ9 and Mascia for compact blue broad-line emitters

It also cites Hutchison for THRILS coordinates, Goulding for UHZ1 context, and
Dayal for the growth model. The manuscript's 29 citation keys and 29
bibliography entries match exactly.
The versioned JADES DR3 GOODS-S prism catalogue supplies Scholtz-row coordinates
and is identified in the manuscript and extraction notes.
