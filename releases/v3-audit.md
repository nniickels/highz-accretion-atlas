# v3 release audit

| Manuscript claim | Machine evidence | Status |
| --- | --- | --- |
| 350 measurements / 340 objects / 339 hosts | v3 dataset manifest and verifier | verified |
| Scholtz table has 41 rows and 21 at `z >= 4` | focused claim regression, full-table parser, catalogue-builder cardinality assertions, and exact dataset reproduction | verified |
| JADES-NS-GS00099671 has no admitted numeric BH mass | focused claim regression, correction validator, canonical measurement row, and exact dataset reproduction | verified |
| 244 eligible measurements / 237 eligible objects | v3 dataset manifest and exact science reproduction | verified |
| 103 catalogue-only objects | v3 gallery coverage verifier | verified |
| 234/227 primary measurement/object rows | focused claim regression, canonical catalogue tables, and reproduction gate | verified |
| 7 alternate-measurement comparisons | focused claim regression, canonical science table, and reproduction gate | verified |
| Follow-up matrix contains 340 objects: 237 ranked and 103 explicitly unranked | canonical follow-up table and verifier | verified |
| Source-caveat summary contains one row for each of 32 admitted source families | canonical caveat table and verifier | verified |
| UNCOVER-20466 leads both point and uncertainty navigation views | focused claim regression and canonical object ranking tables | verified |
| 680 per-object panels cover all 340 objects: 340 $f_{Edd}$-mass and 340 seed-redshift-mass panels | focused claim regression, v3 dataset manifest, and visual-coverage verifier | verified |
| Full-assumption v3 growth-track figure contains the historical v1 grid of 72 curves | focused assumption-grid regression and figure-resolution verifier | verified |
| Every combined growth-track figure uses the common observed-redshift range 13 to 3, including GHZ2 at z=12.34 | axis-range and catalogue-coverage regressions and generated figures | verified |
| Overview growth-track object colors encode broad-line AGN in purple; the full-assumption companion uses blue numerical points with blue/gray no-mass groups | focused palette regression and generated figures | verified |

Interpretive claims are deliberately bounded: ranks are navigation/descriptive,
the pooled catalogue is not demographic, and the growth model does not prove a
unique seed or accretion history.

The 2026-09-04 correction separates composite navigation rank from descending
required Eddington ratio in the manuscript. GS-20057765 is third in the latter;
COSMOS3D-13852 is fourth (third by composite score). Twelve NEXUS point estimates
without statistical errors have no probabilities or uncertainty ranks and are
visually distinguished. The compatibility efficiency prescription is explicit.

Independent source validation covers 1,309 field comparisons across all 32
families, plus numerical age/growth checks; see `data/validation/README.md`.
It does not certify all-source accuracy. The NEXUS extraction correction adds
published luminosity errors without changing membership or mass estimates.

## Release-specific evidence decisions

The Scholtz et al. paper reports 42 objects, while its source-native sample
table contains 41 rows. The checked-in full table contains exactly 21 rows at
`z >= 4`; all 21 are included, and no black-hole mass is inferred for
JADES-NS-GS00099671.

Exactly one preferred measurement controls object-level evidence status while
all measurement-level statuses remain visible. This leaves the secure JADES
8083 measurement primary and retains its candidate alternate. UHZ1 remains
disputed because its preferred full-data reanalysis is disputed.

The v2 expansion admits 49 new non-cluster Baccus objects and ten Fei/GLIMPSE
objects with explicit lensing corrections. Thirteen otherwise-new Baccus
cluster-field objects are excluded because that source does not publish the
required magnifications; three of them enter through Fei with corrected values.
The heterogeneous v3 expansion adds two Treiber UNCOVER high-ionization
components and MoM-BH*-1, all without canonical numerical growth masses.
The final v3 completion adds 14 NEXUS objects, 13 COSMOS-3D objects, and GHZ4
and GHZ7. NX10835 is identity-resolved to its prior Mascia measurement, so the
30 new measurements add 29 objects and 25 plottable objects.

## Manuscript citation audit

The manuscript cites all 32 admitted source families, including Zhuang/NEXUS,
Lin/COSMOS-3D, and Napolitano/“Seven Wonders”:

- Juodžbalis, Taylor, Matthee, Lin, Harikane, Davis, Ren, Greene, Kocevski,
  Skyfire, Larson, Killi, Übler, Baccus, and Fei/GLIMPSE broad-line samples
- Bogdán and Zou for the UHZ1 evidence history
- Scholtz for the JADES narrow/high-ionization candidates
- Maiolino for GN-z11
- Chisholm, Tang, Mazzolari, Zhang, and Chavez Ortiz for the expanded
  high-ionization and narrow-line families
- Leung/MEOW and Lyu/SMILES for MIRI-selected candidates
- Napolitano for GHZ9, Mascia for compact blue broad-line emitters, Treiber for
  the additional UNCOVER high-ionization candidates, and Naidu for MoM-BH*-1

It also cites Hutchison for THRILS coordinates, Goulding for UHZ1 context, and
Dayal for the growth model. The manuscript's 36 citation keys and 36
bibliography entries match exactly.
The versioned JADES DR3 GOODS-S prism catalogue supplies Scholtz-row coordinates
and is identified in the manuscript and extraction notes.
