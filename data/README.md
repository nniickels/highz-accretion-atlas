# Data

This folder holds catalogue tables, their source measurements, and the records
used to check them. Calculated growth rates and figures are in [results/](../results/README.md).

## Start here

- [v3 object table](processed/v3/v3_accreting_objects.csv): one preferred
  measurement per stored object, with 338 object records.
- [v3 measurement table](processed/v3/v3_accreting_measurements.csv): all 350
  literature measurements, including alternatives for the same object.

The catalogue records 337 host systems. Three identity groups remain unresolved,
so the object count is provisional. See the [identity audit](../docs/source-notes/redshift-identity-audit.md).

## Folder guide

| Folder | Contents |
| --- | --- |
| [processed/](#processed-catalogues) | Standardized measurement, object, host, observable, and subgroup tables. |
| [raw/](raw/README.md) | Original source tables and manual extractions. |
| [assembly/](#assembly-inputs) | Inputs used to combine source records and apply reviewed identity decisions. |
| [crossmatch/](#identity-links) | Links between measurements, objects, and hosts, with aliases and match reviews. |
| [validation/](validation/README.md) | Expected source values and extracts used for independent checks. |
| [publication/](publication/README.md) | Rules and comparison inputs for the manuscript samples. |
| [manifests/](#file-manifests) | File lists and SHA-256 checksums for data and source records. |

## Processed catalogues

`processed/v1/`, `v2/`, and `v3/` use the same table structure. Their sizes and
scope are listed in the [main README](../README.md#dataset-versions).
Choose one version for an analysis; concatenating versions counts shared
records repeatedly.

A measurement is a record from the literature. An object groups measurements
assigned to the same accreting system. A host groups systems assigned to the
same host galaxy. Distinct objects can share a host. Observable tables retain
individual reported quantities; strata tables summarize catalogue subgroups.

Use `measurement_id`, `physical_object_id`, and `host_system_id` to join tables.
Display names can differ between sources. Retained legacy tables support
regression checks and do not define additional public versions.

## Assembly inputs

`assembly/blagn_foundation_measurements.csv` holds the corrected broad-line
AGN measurements used before Ren and the v3 expansion sources are added.
Here AGN means active galactic nucleus. Files ending in
`_identity_overrides.csv` record reviewed decisions about source matches;
other assembly inputs record reconciled duplicate pairs.

These files are fixed inputs to the catalogue builder. Generated tables go to
`processed/` and `crossmatch/`. The [versioning guide](../docs/guides/versioning.md)
defines which source types enter each version.

## Identity links

`crossmatch/v1/`, `v2/`, and `v3/` contain measurement-to-object and object-to-host
links, aliases, and match reviews. Use these links to inspect how records were
grouped. Historical filenames in retained review inputs do not identify new
catalogue versions. Open identity questions are documented in the identity audit.

## File manifests

`manifests/v1-dataset-manifest.json`, `v2-dataset-manifest.json`, and
`v3-dataset-manifest.json` list the generated files and their SHA-256 checksums.
`source-provenance-manifest.json` records source and validation files.
Checksums detect file changes; they do not establish scientific correctness.

The [reproduction guide](../docs/guides/reproducibility.md) gives verification
commands and explains when a reviewed change requires new checksums.
Publication results are compared separately against an independent baseline.

## Registries and review records

| File | Purpose |
| --- | --- |
| [sources.md](sources.md) | Source bibliography, extraction methods, and limitations. |
| [source_provenance_registry.csv](source_provenance_registry.csv) | Publication versions, source locations, archive hashes, and verification dates. |
| [source_family_registry.csv](source_family_registry.csv) | How each study or related survey group enters the catalogue. |
| [mass_method_registry.csv](mass_method_registry.csv) | Mass estimators, calibration references, and method uncertainties. |
| [selection_function_registry.csv](selection_function_registry.csv) | Survey selection, completeness information, and limits on population inference. |
| [manual_extraction_audit.csv](manual_extraction_audit.csv) | Extracted-file hashes, row counts, source locations, and remaining checks. |
| [poster_inputs.json](poster_inputs.json) | Reviewed scientific inputs for poster figures and claims. |
| [poster_exports.json](poster_exports.json) | Reviewed PowerPoint/PDF pairs and their hashes. |

See [setup](../README.md#getting-started) before running the workflows.
