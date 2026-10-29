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
Each numerical mass has an independent record with its central value,
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

## Extraction integrity

`data/manual_extraction_audit.csv` inventories 39 extraction inputs with hashes,
parsed row counts, source membership, and table locations. Run
`.venv/bin/python -m src.internal.verify_manual_extractions` to check these
records. It rejects changed bytes, row counts, duplicate measurement IDs, source
membership drift, and changes to the Scholtz table parse. File integrity checks
complement the independent value checks above; they do not establish that a
transcription agrees with its publication.

## Source references and retained data

All families use the shared provenance registry, publication/table locators, and
independently recorded expected values. The repository does not bundle reference-only copies of
paper pages, HTML, TeX, publisher metadata, or review excerpts. Machine-readable
inputs used by extraction or calculations are in `data/raw/`. Retrieve the
recorded source version to inspect the original evidence. Historical review-extract
identifiers and hashes document what was inspected; they do not identify bundled
files or provide an offline source archive.

`data/raw/baccus_published_table1.txt` is a machine-readable input to the publication
revision sensitivity calculation. Its bytes
are pinned by the provenance manifest. The frozen catalogue continues to use the
original preprint measurements.

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
