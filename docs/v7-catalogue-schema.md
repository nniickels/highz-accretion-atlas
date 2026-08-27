# Frozen v7.0 catalogue-only heterogeneous atlas layer

v7 non-destructively copies the frozen v6 catalogue through the controlled
vocabulary adapter in `src/v7_admission.py` and appends the admitted Ren et al.
ALPINE--CRISTAL--JWST source layer. It does not overwrite v1--v6 products and
does not yet generate v7 growth rankings, uncertainty products, or figures.

The combined table retains historical `*_std` uncertainty columns for
compatibility while exposing the canonical v7 names without that suffix. The
two representations must be numerically identical, including missingness.
Every new row also passes the shared standardization layer, carries its
introduction `project_version`, and has a positive `cosmic_time_gyr`. The batch
gate in `src/v7_batch.py` enforces these invariants before concatenation.

## Cardinalities

- 119 literature measurements
- 112 physical accreting-BH objects or candidate nuclei
- 111 host systems
- 119 exploratory growth-eligible measurements / 112 objects
- 112 primary-eligible measurements / 105 objects

The Ren layer contributes seven candidate nuclei in six host systems.
`DC_848185_a` and `DC_848185_b` are separate physical-object IDs sharing
`HZS-DC-848185`; they are not duplicate measurements of one black hole. The
existing duplicate-measurement links and v6 default choices remain unchanged.

## Products

- `data/processed/v7_accreting_measurements.csv`: one row per literature
  measurement; the executable admission contract applies here.
- `data/processed/v7_accreting_objects.csv`: one row per physical object, using
  the frozen v6 preferred-measurement rules and the only Ren measurement for
  each nucleus. Evidence is conservatively aggregated across linked rows.
- `data/processed/v7_host_systems.csv`: identity and shared-host metadata only;
  it is not a black-hole ranking table.
- `data/processed/v7_source_observables.csv`: all 70 source-native Ren Table 2
  entries, including twelve explicit upper limits.
- `data/processed/v7_catalogue_strata.csv`: counts by entity level, source,
  survey, field, evidence, class, and LRD phenotype. These are catalogue counts,
  not pooled demographic inference.
- `data/crossmatch/v7_measurement_object_links.csv` and
  `data/crossmatch/v7_object_host_links.csv`: the two explicit identity edges.
- `data/crossmatch/v7_object_aliases.csv`: source aliases and coordinates.
- `data/crossmatch/v7_reviewed_match_candidates.csv`: empty because the Ren
  coordinate/redshift audit found no candidate v6 match.

## v6 inheritance decisions

Frozen rows retain published values and stable `HZA-*` IDs. v7 changes only the
copied representation:

- historical classes and evidence labels are translated to canonical v7 terms;
- JADES fields are restored from the published `GN-*`/`GS-*` identifiers, and
  an unavailable legacy extraction date is explicitly marked, not invented;
- the source-reviewed 0.3 dex JADES Halpha calibration systematic is exposed
  separately from statistical errors; no Hbeta systematic is inferred;
- inherited objects receive deterministic `HZS-*` host IDs with an explicit
  provisional one-to-one assignment status;
- missing lensing measurements remain `not_reported`; no magnification or
  lensing uncertainty is inferred in this catalogue-only phase.

## Ren eligibility and host semantics

All seven Ren masses are retained as Reines et al. (2013) Halpha single-epoch
virial estimates with formal asymmetric errors and a separate 0.4 dex
calibration systematic. Six masses are conditional on the broad component being
BLR emission and are excluded from primary comparisons. `DC_536534` is probable
evidence and primary eligible. The integrated stellar mass for `DC_848185` has
`host_property_scope=shared_host_system_total`; it must not be assigned as an
independent host mass to each candidate nucleus.

## Reproduction

```bash
python -m scripts.process_v7_catalogue
python -m scripts.verify_v7_catalogue --reproduce
```

`releases/v7-catalogue-manifest.json` covers only catalogue, identity,
observable, and count products. A later class-aware science workflow must use a
separate release scope and must not silently pool unlike selection functions or
conditional masses.

Larger additions are organized by evidence family under
`docs/v7-source-family-batches.md`; the next selected batch is the distinct
XQR-30 luminous-quasar comparison stratum. That extension is now released in
separate v7.1-prefixed artifacts; this frozen v7.0 layer and manifest remain
byte-identical.
