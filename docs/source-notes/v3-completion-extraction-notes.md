# Final v3 completion extraction notes

Reviewed and extracted 2026-09-03. Each source is assigned only to v3 because
its source-level object or phenotype mix is heterogeneous. All identifications
depend essentially on JWST imaging or spectroscopy.

| Source | Raw rows | New objects | New plottable objects | Object types | Source archive SHA-256 |
| --- | ---: | ---: | ---: | --- | --- |
| Zhuang et al., NEXUS WFSS | 15 | 14 | 11 | Broad-line AGN, LRDs, quasar-like AGN | `e0fd19d3b0a079efeccea6fda92faa54876a5c293b24bdda7106f7df80978048` |
| Lin et al., COSMOS-3D | 13 | 13 | 13 | Broad-Halpha/Hbeta AGN, red compact sources, blue quasar-like sources | `3a056a22de95bf81524433d955905d15f65176e16e138fd00128826e5fa5bb52` |
| Napolitano et al., “Seven Wonders” | 2 | 2 | 0 | High-ionization-line AGN candidates | `a8eb5e6c2ea10e65d70d5a7cee5e9d5df4681f24f262296f6c19477faa024b31` |

## NEXUS WFSS

The extract contains all 15 Table 1 rows at `z>=4`. Twelve rows publish
Halpha single-epoch virial masses using the Reines et al. calibration. Table 1
does not publish object-level mass errors, so their statistical errors remain
missing; the source's typical 0.5 dex virial uncertainty is stored separately
as an unapplied method systematic. The three starred broad-line classifications
have no published mass and remain candidate, growth-ineligible rows.

NX10835 is the same object as the previously admitted Mascia identifier
`nexus-obs3_5105_10835`: the positions differ by 0.066 arcsec and the redshifts
by 0.001. The NEXUS mass-bearing measurement becomes preferred without deleting
the earlier candidate measurement. Consequently NEXUS adds 14 objects and 11
new plottable objects while upgrading one existing object.

## COSMOS-3D

All 13 Table 1 objects are at `z>=5` and have published asymmetric statistical
mass errors. Halpha and Hbeta calibrations remain distinct in `mbh_method`.
The source warns that scattering could bias virial masses high by 1--2 dex;
this directional caveat is recorded but is not converted into a symmetric
statistical error. A 10-arcsec coordinate/redshift search found no match in the
pre-completion atlas.

## Seven Wonders

GHZ7 is probable because the source places it in the AGN-only CIII]/CIV
diagnostic region and reports [NeV]3346 at S/N=3. GHZ4 remains a candidate
because its spectroscopic redshift is explicitly tentative. Neither source row
publishes a canonical black-hole mass. GHZ9 is omitted from this extract because
it is already represented by the later dedicated Napolitano analysis.

The three checked-in CSV hashes and exact row counts are pinned in
`data/manual_extraction_audit.csv`; source versions and archive hashes are in
`data/source_provenance_registry.csv`.
