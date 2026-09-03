# Data guide

Start with the final v3 object catalogue at
`processed/v3/v3_accreting_objects.csv` (133 physical objects). Use
`v3_accreting_measurements.csv` for all 142 literature measurements. Host,
source-observable, strata, and identity tables use the same v3 prefix.

v1 is the original complete 23-object JADES analysis dataset. v2 is the
expanded comparable BLAGN dataset (119 measurements / 112 objects). v3 adds
JWST-identified heterogeneous comparison and candidate sources (142 / 133).

Raw files retain descriptive source names and publication versions.
`assembly/` contains the frozen BLAGN foundation and reviewed identity inputs
needed by the deterministic catalogue builder; it is not a fourth dataset.
Dataset
versions describe grouped membership only. Never join catalogues by display
name: use `measurement_id`, `physical_object_id`, and `host_system_id`.

See `raw/README.md`, `assembly/README.md`, `processed/README.md`,
`crossmatch/README.md`, and
`../docs/guides/versioning.md`.
