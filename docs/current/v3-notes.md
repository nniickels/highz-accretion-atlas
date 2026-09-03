# v3 notes

v3 is the complete heterogeneous dataset; v1 and v2 are its maintained nested
subsets. For the canonical processed-data paths and complete visual atlas, see
[`v3-atlas.md`](v3-atlas.md).

## Provenance correction

The Scholtz et al. paper reports 42 objects, while its source-native sample
table contains 41 rows. The checked-in full TeX table contains exactly 21 rows
at `z >= 4`; all 21 are included in v3. No black-hole mass is inferred for the
omitted-in-earlier-work JADES-NS-GS00099671 row.

## Evidence policy

Exactly one preferred measurement now controls object-level evidence status.
All distinct measurement-level statuses and bases remain on the object row.
This makes the preferred secure JADES 8083 measurement primary again while
leaving its candidate alternate measurement fully visible. UHZ1 remains
disputed because its preferred full-data reanalysis is disputed.

## Dataset scale

- 142 measurements, 133 physical objects, 132 host systems
- 183 source-local observables
- 119/112 growth-eligible measurement/object rows
- 182/171 primary measurement/object rows
- 48 explicit measurement/object science exclusions
- six manuscript figures and five additional all-object/robustness figures
- complete current $f_{Edd}$-mass and seed-redshift-mass panels for all 133 objects
- three full all-object supplement atlases
- 133-row follow-up matrix with 112 ranked and 21 explicitly unranked objects
- 9-row source-family caveat summary

The v3 verification commands check these counts, schemas, figures, and
manuscript references directly.
