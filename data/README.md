# Data Directory Guide

Data products are separated by provenance and release stage.

## Start with the current v7.5 catalogue

For most scientific use, begin with
[`v7_5_accreting_objects.csv`](processed/v7_5/v7_5_accreting_objects.csv).
It has one preferred row for each of 219 physical objects and retains the
measurement-level evidence history needed to audit that choice.

| Need | Canonical v7.5 file | Rows | What one row represents |
| --- | --- | ---: | --- |
| Default analysis table | [`v7_5_accreting_objects.csv`](processed/v7_5/v7_5_accreting_objects.csv) | 219 | One physical object using its preferred measurement |
| Every literature measurement | [`v7_5_accreting_measurements.csv`](processed/v7_5/v7_5_accreting_measurements.csv) | 234 | One source-specific measurement |
| Source-native observables | [`v7_5_source_observables.csv`](processed/v7_5/v7_5_source_observables.csv) | 1,106 | One reported observable attached to a measurement |
| Host-level view | [`v7_5_host_systems.csv`](processed/v7_5/v7_5_host_systems.csv) | 218 | One host system; multi-nucleus systems remain explicit |
| Class and eligibility counts | [`v7_5_catalogue_strata.csv`](processed/v7_5/v7_5_catalogue_strata.csv) | 120 | One released summary stratum |
| Preferred-row and identity decisions | [`v7_5_measurement_object_links.csv`](crossmatch/v7_5/v7_5_measurement_object_links.csv) | 234 | One measurement-to-object assignment |
| Aliases and source-local names | [`v7_5_object_aliases.csv`](crossmatch/v7_5/v7_5_object_aliases.csv) | 276 | One alias or source measurement identity |
| Object-to-host assignments | [`v7_5_object_host_links.csv`](crossmatch/v7_5/v7_5_object_host_links.csv) | 219 | One object-to-host assignment |
| Manually reviewed match candidates | [`v7_5_reviewed_match_candidates.csv`](crossmatch/v7_5/v7_5_reviewed_match_candidates.csv) | 1 | One documented cross-source review decision |
| Source papers and supporting data | [`source_provenance_registry.csv`](source_provenance_registry.csv) | 16 | One primary, reanalysis, coordinate, or context source |

The stable relational path is:

```text
source observable --measurement_id--> measurement
measurement --physical_object_id--> physical object
physical object --host_system_id--> host system
```

Use `measurement_id`, `physical_object_id`, and `host_system_id` for joins.
`object_id` is the source-local name and can recur or change across papers.
Alternate measurements are intentionally retained; do not count rows in the
measurement table as independent physical objects. The
`preferred_measurement_flag` in the measurement-object link table records the
released object-level choice.

A minimal Python read is:

```python
import pandas as pd

objects = pd.read_csv(
    "data/processed/v7_5/v7_5_accreting_objects.csv",
    low_memory=False,
)
eligible = objects.loc[objects["growth_ranking_eligible_flag"]]
```

For field definitions and controlled vocabularies, use
[`docs/v7.5-catalogue-schema.md`](../docs/v7.5-catalogue-schema.md),
[`docs/multiclass-eligibility-and-mass-comparability.md`](../docs/multiclass-eligibility-and-mass-comparability.md),
and [`sources.md`](sources.md).

## Directory layout

```text
data/
├── raw/                    source-native and manually curated input tables
├── processed/<release>/    standardized catalogue tables frozen by release
├── crossmatch/<release>/   identity links, aliases, and review decisions
├── source_family_registry.csv  released heterogeneous source-family batches
├── source_provenance_registry.csv  source status, roles, versions, DOIs, and hashes
└── mass_method_registry.csv    reviewed cross-release mass-method metadata
```

Release folder names match their filename prefixes (`v1`, `v3`, `v7_1`, and so
on). Files keep their established names so a table remains recognizable when
downloaded outside the repository.

Earlier processed and crossmatch releases are intentionally retained. A later
catalogue usually extends an earlier one, but the earlier snapshot records the
then-current membership, identity decisions, and schema required to reproduce
its science products. Do not replace an older file with a newer release or
create duplicate aliases at the directory root.

Generated science tables and figures live in `results/releases/<release>/`.
Release hashes and reproduction metadata live in `releases/`.

`source_provenance_registry.csv` is a machine-readable, non-destructive
supplement spanning all current catalogue source families and their supporting
coordinate/context sources. It does not rewrite historical catalogue rows.
Its controlled fields, current-source coverage, and exact bytes are checked by
`python -m scripts.verify_source_provenance` and
`releases/source-provenance-manifest.json`.

The current v7.5 catalogue lives in `processed/v7_5/` and
`crossmatch/v7_5/`. It contains 234 measurements, 219 physical objects, and 218
host systems. The raw Scholtz provenance audit retains both the frozen v7.4
20-row extraction, the one-row v7.5 correction, and the complete 41-row
source-native TeX table; release code proves their combined 21-row `z >= 4`
membership.
