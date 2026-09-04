# Independent primary-source checks

`primary_source_checks.json` records 865 cell-level comparisons against four
independently retrieved primary-source tables: COSMOS-3D, NEXUS, JADES, and
Seven Wonders. The checks cover 53 source rows and five repository artifacts,
including canonical integration checks for JADES and the final v3 catalogue.

Run `.venv/bin/python -m src.internal.verify_primary_source_values` from the
repository root. The fixture records retrieval dates, source URLs, retrieved
content hashes, and the exact expected values. Its scope is explicit and does
not certify source families absent from the fixture.
