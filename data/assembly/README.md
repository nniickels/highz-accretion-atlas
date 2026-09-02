# Catalogue assembly inputs

These files are frozen, machine-readable inputs required to reconstruct the
canonical v1/v2/v3 catalogues:

- `blagn_foundation_measurements.csv`: corrected broad-line foundation before
  the Ren and heterogeneous v3 source families are attached
- `*_identity_overrides.csv`: reviewed cross-source identity decisions
- `xqr30_external_identity_audit.csv`: reviewed external-repeat audit

They are implementation inputs, not public dataset versions. Canonical outputs
are written only under `data/processed/v1`, `v2`, and `v3`, with identity
products under the matching `data/crossmatch/` directories.
