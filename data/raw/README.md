# Raw Source Data

This directory contains source-native tables and deliberate manual extractions.
Files retain descriptive source names and are treated as immutable inputs.

Do not normalize values in place. Corrections and interpretation choices belong
in the canonical processing layer, with the original source value preserved.
Accuracy corrections propagate to every affected dataset version. Comparable
JWST broad-line AGN additions enter v2 and flow into v3; new object/evidence
types enter v3 only. Source
versions, roles, DOIs, archive hashes, and extraction limitations are documented
in [`../sources.md`](../sources.md) and
[`../source_provenance_registry.csv`](../source_provenance_registry.csv).

`baccus26_nirspec_blagn_table1_zge4_new.csv` and
`fei26_glimpse_blagn_tables1_2_new.csv` are audited v2 canonical-mass additions.
The former excludes new cluster-field rows without source-published lensing
corrections; the latter preserves the source's explicit GLIMPSE magnification
corrections.

`v3_jwst_heterogeneous_expansion.csv` is the audited 78-row extraction used by
the v3-only heterogeneous expansion. It excludes known aliases and overlaps;
proxy masses, assumed-Eddington estimates, and upper limits remain contextual
observables rather than canonical growth masses.
