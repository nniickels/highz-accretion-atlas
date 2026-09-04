# Literature scope and cutoff

The current v1/v2/v3 source-family membership reflects the literature review
completed on **2026-09-03**. The cutoff records the review date for the current
catalogue state; it does not imply that v3 is an exhaustive census of every
high-redshift accreting black-hole report published before that date.

## Admission scope

A source enters a dataset only when the repository contains:

- a stable primary-source or archive record;
- source-native tabular measurements suitable for deterministic extraction;
- explicit evidence, mass-method, uncertainty, lensing, and missingness rules;
- identity and host-system review where cross-source overlap is possible; and
- regression anchors proving row membership and published values.

v1 contains the original JADES BLAGN source family. v2 adds comparable JWST
broad-line source families with canonical masses. v3 adds JWST-identified
heterogeneous X-ray, narrow-line, high-ionization, infrared, photometric, and
broad-line-candidate source datasets. Ground-selected legacy quasar samples are
outside the catalogue boundary. The authoritative included-source list is
`data/source_provenance_registry.csv`.

## Considered but not admitted by the cutoff

| Source | Status in v3 | Reason |
| --- | --- | --- |
| Juodzbalis et al. (2026), *A direct black-hole mass measurement in a little red dot at high redshift*, DOI `10.1038/s41586-026-10579-4` | verified next-version measurement | The source is A2744-QSO1, already represented in v2/v3. Its pinned v2 archive reports a preferred direct MOKA3D mass of log(MBH/Msun)=7.7+/-0.3 plus an inclination-free lower-limit result. It requires a direct-mass adapter and adds zero objects. |
| Jin et al., J0226 JWST BLAGN sample | screened, no new membership | All four physical objects are represented by admitted Baccus rows, so adding the dataset would not contribute a new candidate. |
| Baccus GLIMPSE, MACS0416, and MACS1149 cluster-field rows without published magnifications | source-local exclusions | Thirteen otherwise-new Baccus objects lack source-published lensing corrections. Three GLIMPSE objects enter independently through Fei with explicit corrections; the remaining ten are not admitted as comparable mass points. |
| Prospective sources listed in the README references | background only | They do not contribute catalogue rows unless separately admitted under the rules above. |

The v1/v2/v3 membership is frozen at this cutoff. New source families or new
measurements require a new dataset version; their scientific scope and nesting
must be declared when that version is defined. The v2/v3 source assignments
above describe the existing frozen datasets, not permission to expand them.
Accuracy fixes, publication-status corrections, and provenance updates apply to
every affected existing version. Any correction to an extracted value must be
documented against the primary source and accompanied by regenerated products
and explicitly reviewed manifests.

The implemented final admission record and counts are maintained in
[`catalogue-completion-plan.md`](catalogue-completion-plan.md).
