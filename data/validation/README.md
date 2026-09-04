# Independent primary-source checks

The two fixtures provide 1,309 field comparisons with independent primary-source
values, covering all 32 admitted source families. This is representative family
coverage, not an exhaustive audit of every catalogue field.

`primary_source_checks.json` supplies 865 checks across 53 rows from COSMOS-3D,
NEXUS, JADES, and Seven Wonders. `primary_family_anchors.json` adds 444 checks
for the other 28 families, including 343 checks across all 49 Baccus rows.
Some context-only families have only redshift or position anchors; their full
scientific interpretation is not certified by passing these checks.

Run `.venv/bin/python -m src.internal.verify_primary_source_values` from the
repository root. The verifier checks expected values, anchor archive versions,
and complete family coverage. Both fixtures are pinned in the provenance manifest.

For the four-table fixture, download the linked HTML records as `cosmos.html`,
`nexus.html`, `jades.html`, and `seven.html`, then run
`.venv/bin/python -m src.internal.refresh_primary_source_checks /path/to/html`.
For family anchors, retrieve the recorded source URL, verify the archive hash,
extract the named TeX member (or PDF text with pypdf), and inspect the recorded
locator and evidence. Publisher machine-readable tables have their own URL and
member hash; the archive hash separately pins the paper. Review any fixture
changes against primary material, never derive expected numbers from catalogue
outputs. Baccus anchors pin arXiv v1, the actual frozen measurement version.
Killi's coordinates are checked against the archived preprint; that preprint
predates the final numerical revision, so this anchor does not validate its
published redshift or formal mass-error values.
