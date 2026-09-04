# Manual extraction validation

Reviewed 2026-09-03. `data/manual_extraction_audit.csv` inventories all 22
row-level CSV inputs plus the source-native Scholtz TeX table. Each record pins
the checked-in bytes, expected parsed row count, source-family membership, and
the source-table locator described in the extraction notes.

Run `.venv/bin/python -m src.internal.verify_manual_extractions` to check the
audit. The verifier fails on changed bytes, row counts, duplicate measurement
identifiers, source-family drift, or a changed 41-row Scholtz parse. These gates
complement the source-archive hashes in the provenance registry and the
source-specific scientific anchors in the test suite.

The audit does not turn a published proxy, upper limit, or assumed-Eddington
mass into a canonical mass. Evidence and interpretation remain controlled by
the source notes, taxonomy, and science policy.
