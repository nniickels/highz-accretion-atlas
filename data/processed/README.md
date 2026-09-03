# Processed catalogues

- `v1/`: 23 original JADES BLAGN measurements and objects.
- `v2/`: 119 comparable BLAGN measurements representing 112 objects.
- `v3/`: final JWST-identified heterogeneous catalogue, 142 measurements and 133 objects.

These are dataset scopes, not software releases. Each uses the same schema and
contains measurement, object, host, observable, and strata tables. Use the
object table for one row per physical object and the measurement table when
literature-measurement multiplicity matters.

Legacy same-class ingestion tables may remain as internal regression inputs;
they are not additional public dataset versions.
