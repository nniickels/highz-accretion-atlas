# Independent primary-source checks

The verifier performs 2,041 comparisons across three fixtures. The complete
mass audit covers **all 244 admitted numerical mass measurements and all 732
central-mass/error fields**, including missing errors for the twelve NEXUS
measurements. The fixtures overlap, so 2,041 is a comparison count, not a count
of unique cells. Coverage of other observables remains representative.

- `primary_source_checks.json`: 865 checks across 53 rows from independently
  retrieved COSMOS-3D, NEXUS, JADES, and Seven Wonders tables.
- `primary_family_anchors.json`: 444 additional comparisons for the other 28
  families, including all 49 admitted Baccus rows. Together these cover all 32
  admitted families.
- `complete_mass_checks.json`: 732 mass/error checks, requiring exactly one
  independent record for every numerical mass measurement. TeX table cells,
  source versions, conversion notes, and locators accompany the expectations.

Run `.venv/bin/python -m src.internal.verify_primary_source_values`. The gate
rejects missing measurement coverage, incomplete error triplets, source-version
mismatches, and changed values. All fixtures and the two supplementary source
inputs are pinned in the provenance manifest.

For the four-table fixture, download the linked HTML records as `cosmos.html`,
`nexus.html`, `jades.html`, and `seven.html`, then run
`.venv/bin/python -m src.internal.refresh_primary_source_checks /path/to/html`.
For the other fixtures, retrieve the recorded source archive, verify its hash,
and inspect the named table member/locator. Expected values must be independently
reviewed against that source, never copied from generated catalogue outputs.
Harikane's linear mass bounds are transformed with log10 to eight decimals.
The remaining TeX tables quote log masses and errors directly. Previously
reviewed table/PDF anchors are reused with explicit fixture references.

Killi's final publisher-deposited abstract is saved verbatim in
`source_inputs/killi-published-crossref.json`; it verifies z=4.5319 and
M=8(+0.5,-0.4)e8 Msun. The corrected log errors preserve these asymmetric
bounds. Its older preprint is registered separately for coordinates.
`source_inputs/baccus_published_table1.txt` is the revised publisher table used
by the supplementary Baccus sensitivity analysis. The frozen catalogue still
uses the explicitly pinned v1 measurement table.

This audit validates transcription and conversion of numerical mass/error
fields. It does not establish estimator validity, reconstruct posterior
covariance, or make the heterogeneous sample complete or unbiased.

## Remaining coverage and completion criteria

The mass/error audit is complete for the admitted numerical measurements. The
remaining non-mass audit is **partial**, not a completed task or an intrinsic
impossibility. Redshifts, coordinates/identities, luminosities and their errors,
Eddington ratios, host masses, magnifications, line measurements, censoring, and
evidence classifications do not yet have exhaustive independent cell coverage.
Some are checked in the four-table fixture or family anchors; a family anchor
does not certify all fields or every row in that family. Hash agreement and
regeneration establish consistency with stored inputs, not source correctness.

To extend coverage, retrieve each pinned source version, review its table or
text locator independently, record source-native values and conversions, and
check both the raw extraction and its canonical destination. Keep limits,
conditional estimates and missing values distinct from detections. Add fixtures
with row identifiers and source hashes, plus tests rejecting missing expected
coverage. Do not generate expected values from the pipeline being tested.

Exhaustive non-mass validation remains recommended before relying on those
fields for a new scientific claim. The current manuscript's growth diagnostics
are driven by mass and redshift, so extending redshift/identity checks is the
first priority, followed by fields used in follow-up and host comparisons.
Until then, describe the atlas as reproducible with complete numerical-mass
checks and representative checks of other fields; do not claim all catalogue
values or scientific interpretations have been independently validated.
