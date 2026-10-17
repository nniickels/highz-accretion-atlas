# Independent source checks

These files record expected values read independently from the publications.
They check transcription and unit conversion without using generated catalogue
values as their own reference.

## Mass checks

| File | Coverage |
| --- | --- |
| `primary_source_checks.json` | 865 checks across 53 COSMOS-3D, NEXUS, JADES, and Seven Wonders rows. |
| `primary_family_anchors.json` | 470 checks for the other 33 source families, including all 49 admitted Baccus rows. |
| `complete_mass_checks.json` | 744 central-mass and error fields for all 248 admitted numerical mass measurements. |

Together these files cover all 37 source families and provide 2,079 comparisons.
Some comparisons overlap; this is not a count of distinct catalogue cells.
The mass checks include missing errors for the twelve NEXUS measurements.
Each numerical mass must have one independent record with its central value,
lower error, upper error, source version, and table or text location.

From the repository root, after [setup](../../README.md#getting-started):

```bash
.venv/bin/python -m src.internal.verify_primary_source_values
.venv/bin/python -m src.internal.verify_redshift_identity
```

The first command rejects incomplete mass/error coverage, changed values, and
source-version mismatches. The second checks central redshifts, available
coordinates, and source matches, and reports the open identity groups.
Adding `--require-resolved` to the second command fails until those groups are
resolved. The manuscript samples exclude all affected records.

## Supporting extracts

`source_inputs/killi-published-crossref.json` preserves the publisher-deposited
abstract used for Killi's redshift and mass bounds. Its older preprint is
registered separately for coordinates. `source_inputs/baccus_published_table1.txt`
contains the revised publisher table used in the Baccus sensitivity test; the
catalogue retains its pinned preprint measurements.

Harikane's linear mass bounds are converted to base-10 logarithms to eight decimal
places. Other TeX tables report logarithmic masses and errors directly. Source
versions, conversion notes, and previously reviewed table/PDF references are
recorded with the expected values. The provenance manifest pins these files and
the supporting extracts by hash.

## Extend the checks

Retrieve the recorded source version, verify its archive hash, and inspect the
specified table or passage. Record reported values and conversions, then check
both the extraction and the processed table. Keep limits, conditional estimates,
and missing values distinct from measurements. Never copy expected values from
the processing pipeline.

To update the four-source HTML checks, save the linked records as `cosmos.html`,
`nexus.html`, `jades.html`, and `seven.html`, then run
`.venv/bin/python -m src.internal.refresh_primary_source_checks /path/to/html`.
Review the changes against those sources before updating the provenance hashes.

## Limits

The separate [redshift and identity audit](../../docs/source-notes/redshift-identity-audit.md)
checks all 355 central redshifts, 328 available coordinate pairs, and 31
redshift-type labels: 1,042 field comparisons. Twenty-seven rows lack coordinates,
and three identity groups remain unresolved. Redshift uncertainties and spectral
reliability are not fully checked.

Luminosities, Eddington ratios, host masses, magnifications, line measurements,
limits, and evidence classifications have partial independent coverage. Checks
of selected rows from a source do not validate its entire sample. Review any
additional field before using it for a new scientific claim.

These checks do not establish mass-estimator validity, correlations between
errors, survey completeness, or unbiased sample selection. Numerical agreement
also does not resolve whether two records describe the same physical object.
