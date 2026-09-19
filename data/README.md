# Data guide

This folder contains the catalogue, the source data used to build it, and the
records needed to trace and check its values. Calculated growth constraints,
rankings, and plots live separately in [results/](../results/README.md).

## Where to start

For the broadest catalogue, open
[v3_accreting_objects.csv](processed/v3/v3_accreting_objects.csv): one preferred
measurement per stored object, with 338 object records. Use
[v3_accreting_measurements.csv](processed/v3/v3_accreting_measurements.csv) to
see all 350 literature measurements, including multiple measurements of the same
object. The catalogue also identifies 337 host systems.

These counts describe the stored catalogue. Three identity groups remain
unresolved, so 338 is not a confirmed count of distinct astrophysical objects;
see the [identity audit](../docs/source-notes/redshift-identity-audit.md).

## What each subfolder contains

| Folder | Contents and purpose | When to use it |
| --- | --- | --- |
| [processed/](processed/README.md) | Standardized, analysis-ready catalogues for v1, v2, and v3. Each version has measurement, object, host-system, source-observable, and catalogue-strata tables. | Start here to read or analyze the catalogue. |
| [raw/](raw/README.md) | Source-native tables and manual extractions from the literature. Filenames identify the source; original values and publication versions are preserved rather than overwritten by processing choices. | Inspect what a paper reported or trace a standardized value back to its input. |
| [assembly/](assembly/README.md) | The frozen broad-line AGN foundation and reviewed identity inputs, including overrides and reconciled duplicate pairs, used by the catalogue builder. These are intermediate building blocks, not another dataset version. | Reconstruct the catalogue or inspect how source records were combined. |
| [crossmatch/](crossmatch/README.md) | Versioned links between measurements, objects, and hosts, plus alternative names, reviewed match candidates, and external-literature identity audits. | Join tables, find another name for an object, or inspect whether two source records refer to the same system. |
| [validation/](validation/README.md) | Independently recorded source values, source locators, and supporting extracts used to check the catalogue. Includes mass/error checks and redshift/identity checks. | Assess validation coverage or verify transcription and conversion against the literature. These checks do not establish that every field or identity is settled. |
| [publication/](publication/README.md) | Inputs for the manuscript analysis: identity exclusions, evidence-selection rules, and source-linked comparison measurements and caveats. These select samples from the catalogue without changing its membership. | Reproduce the 220-object primary and 234-object exploratory samples. Their generated tables and figures are in [results/manuscript/](../results/manuscript/README.md). |
| [manifests/](manifests/README.md) | Lists of canonical artifacts and their SHA-256 checksums, plus a manifest for provenance records and validation inputs. | Check file integrity and consistency with the recorded baseline. Matching hashes do not independently establish scientific correctness. |

## Dataset versions and table relationships

The `v1/`, `v2/`, and `v3/` folders under `processed/` and `crossmatch/` are
nested dataset scopes, not software releases:

| Version | Scope | Measurements | Object records | Host systems |
| --- | --- | ---: | ---: | ---: |
| v1 | Original JADES broad-line AGN sample | 23 | 23 | 23 |
| v2 | Expanded sample of comparable broad-line AGN | 218 | 211 | 210 |
| v3 | v2 plus heterogeneous JWST-identified systems and candidates | 350 | 338 | 337 |

Within each version, a **measurement** is a literature measurement record, an
**object** groups records assigned to the same accreting system, and a **host**
groups systems assigned to the same host. Multiple measurements can belong to
one object, and distinct objects can share a host. The source-observable table
retains individual reported quantities; the strata table summarizes catalogue
subgroups.

Join tables using `measurement_id`, `physical_object_id`, and `host_system_id`,
with the links in `crossmatch/`. Display names alone are not reliable join keys.
For a single catalogue analysis, choose one version rather than concatenate all
three, which would count shared records repeatedly. See the
[versioning guide](../docs/guides/versioning.md) for admission boundaries.

## Files alongside the subfolders

- [sources.md](sources.md): readable source bibliography, extraction methods,
  and source-specific limitations.
- [source_provenance_registry.csv](source_provenance_registry.csv): publication
  versions, URLs, DOIs, archive hashes, source roles, and verification dates.
- [source_family_registry.csv](source_family_registry.csv): how source families
  enter the assembly process, including their evidence classes and admission modules.
- [mass_method_registry.csv](mass_method_registry.csv): black-hole mass estimators,
  calibration references, and reported method systematics.
- [selection_function_registry.csv](selection_function_registry.csv): reported
  source selection and completeness information, with limits on demographic use.
- [manual_extraction_audit.csv](manual_extraction_audit.csv): extraction file hashes,
  expected row counts, source locators, checks performed, and remaining limitations.

To regenerate or verify these products, follow the
[repository workflow](../README.md#workflow) and
[reproduction guide](../docs/guides/reproducibility.md).
