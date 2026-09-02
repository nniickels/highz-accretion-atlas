# Literature scope and cutoff

The canonical v1/v2/v3 datasets are frozen to the source-family review
completed on **2026-08-27**. The cutoff defines a reproducible evidence base;
it does not imply that v3 is an exhaustive census of every high-redshift
accreting black-hole report published before that date.

## Admission scope

A source enters a dataset only when the repository contains:

- a stable primary-source or archive record;
- source-native tabular measurements suitable for deterministic extraction;
- explicit evidence, mass-method, uncertainty, lensing, and missingness rules;
- identity and host-system review where cross-source overlap is possible; and
- regression anchors proving row membership and published values.

v1 contains the original JADES BLAGN source family. v2 adds the comparable
broad-line source families. v3 adds the reviewed luminous-quasar, UHZ1, and
Scholtz heterogeneous families. The authoritative included-source list is
`data/source_provenance_registry.csv`.

## Considered but not admitted by the cutoff

| Source | Status in v3 | Reason |
| --- | --- | --- |
| Juodzbalis et al. (2026), *A direct black-hole mass measurement in a little red dot at high redshift*, DOI `10.1038/s41586-026-10579-4` | pending future dataset | The distinct dynamical-mass measurement requires its own source adapter, mass-comparability policy, identity review, and regression anchors. It was not silently merged into the JADES BLAGN family. |
| Prospective sources listed in the README references | background only | They do not contribute catalogue rows unless separately admitted under the rules above. |

Future literature additions create a new dataset version rather than mutating
v3. Publication-status corrections and provenance metadata may be updated
without changing dataset membership or source-native values.
