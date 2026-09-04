# Processed catalogues

- `v1/`: 23 original JADES BLAGN measurements and objects.
- `v2/`: 218 comparable BLAGN measurements representing 211 objects and 210 hosts.
- `v3/`: final JWST-identified heterogeneous catalogue, 320 measurements representing 311 objects and 310 hosts.

These are dataset scopes, not software releases. Each uses the same schema and
contains measurement, object, host, observable, and strata tables. Use the
object table for one row per physical object and the measurement table when
literature-measurement multiplicity matters.

Legacy same-class ingestion tables may remain as internal regression inputs;
they are not additional public dataset versions.
