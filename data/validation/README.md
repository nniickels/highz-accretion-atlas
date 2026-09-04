# Independent primary-source checks

`primary_source_checks.json` records 865 cell-level comparisons against four
independently retrieved primary-source tables: COSMOS-3D, NEXUS, JADES, and
Seven Wonders. The checks cover 53 source rows and five repository artifacts,
including canonical integration checks for JADES and the final v3 catalogue.

Run `.venv/bin/python -m src.internal.verify_primary_source_values` from the
repository root. The fixture records retrieval dates, source URLs, retrieved
content hashes, and the exact expected values. Its scope is explicit and does
not certify source families absent from the fixture.

To refresh the fixture, download the four linked HTML versions as `cosmos.html`,
`nexus.html`, `jades.html`, and `seven.html` into a local directory, then run
`.venv/bin/python -m src.internal.refresh_primary_source_checks /path/to/html`.
Review changes before accepting the fixture. The refresh reads primary-source
tables, not the production catalogues; verification then compares the two.
