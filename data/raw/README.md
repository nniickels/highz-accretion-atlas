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

`v3_jwst_heterogeneous_expansion.csv` is the audited 75-row extraction used by
the v3-only heterogeneous expansion. It excludes known aliases and overlaps;
proxy masses, assumed-Eddington estimates, and upper limits remain contextual
observables rather than canonical growth masses.
