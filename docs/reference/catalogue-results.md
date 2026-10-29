# Catalogue result tables

These four tables in `results/v3/tables/` use the existing v3 measurements,
growth models, and publication sample rules.

| Table | Contents |
| --- | --- |
| [v3_object_results.csv](../../results/v3/tables/v3_object_results.csv) | One row per object: mass, errors, method, sample flags, reference growth requirements, and source notes. |
| [v3_growth_assumption_comparison.csv](../../results/v3/tables/v3_growth_assumption_comparison.csv) | Required rates for each usable mass under ten sets of assumptions. |
| [v3_field_availability.csv](../../results/v3/tables/v3_field_availability.csv) | Available and missing fields, counted by source and object class. |
| [v3_minimum_seed_mass.csv](../../results/v3/tables/v3_minimum_seed_mass.csv) | Minimum seeds across starting times, efficiencies, rate limits, and mass shifts. |

The object summary includes all 343 records. Growth comparisons use the 241
usable masses. Publication flags identify the 223 primary and 238 expanded
objects; excluded identities remain flagged in the tables.
The summary also records scientific identity status and its open issue group,
separately from assembly decisions.

## Assumptions

[catalogue_growth_comparisons.json](../../data/scenarios/catalogue_growth_comparisons.json)
records the settings. The reference is a 100-solar-mass seed, starting redshift
30, efficiency 0.1, and no merger boost.

The comparison changes one assumption at a time: seed masses of 10³, 10⁴,
or 10⁵ solar masses; starting redshift 20; non-spinning efficiency 0.05719;
or mass shifts of ±0.3 and ±0.5 dex. It uses the catalogue’s matter-plus-Lambda
cosmology. `required_fedd` is clipped at zero to match existing results;
`central_status` marks seeds that exceed the final mass as unsuccessful.

Minimum seeds use starting redshifts 30, 100, and 3400; efficiencies 0.1 and
0.05719; rate limits 0.3, 1, and 2; and mass shifts 0 and ±0.5 dex.
This table includes radiation in cosmic ages and assumes no mergers.

By default, both growth tables reuse the catalogue’s 10,000 mass-error draws
with random seed 20260808.
The draws are stable per object and shared across assumptions. Missing errors
give point results only; intervals and sampled fractions remain blank.
Separate calibration scatter is not added. v4 retains its original random
streams, so its central minimum seeds agree while sampled percentiles may differ.

Availability counts distinguish measurements from adopted object records.
Each fraction uses all rows in its group as the denominator. Source groups
use that row’s source; object groups therefore describe preferred measurements.
Mass-error coverage requires a mass and at least one reported error. Host-mass
upper limits are counted separately from measured masses. Coordinates require
both right ascension and declination.

## Generate and verify

Notebook 01 generates these tables with the other science results. After
[setup](../../README.md#getting-started), the equivalent commands are:

```bash
.venv/bin/python -m src.internal.generate_science v3
.venv/bin/python -m src.internal.verify_versions
```

The verifier rebuilds the tables from catalogue inputs and settings. The v3
manifest records their hashes and the relevant code, settings, and sample-rule
hashes.
