# Manual extraction validation

Reviewed 2026-09-03, amended 2026-09-04, and extended 2026-10-17 for the
five-family admission. `data/manual_extraction_audit.csv` now inventories 39
extraction artifacts, including row-level CSV inputs and source-native tables. Each record pins
the checked-in bytes, expected parsed row count, source-family membership, and
the source-table locator described in the extraction notes.

Run `.venv/bin/python -m src.internal.verify_manual_extractions` to check the
audit. The verifier fails on changed bytes, row counts, duplicate measurement
identifiers, source-family drift, or a changed 41-row Scholtz parse. These gates
complement the source-archive hashes in the provenance registry and the
source-specific scientific anchors in the test suite.

These integrity checks cannot establish original transcription accuracy. A
September independent comparison provided 2,041 field checks across 32 families.
The October extension brings the current coverage to 2,079 comparisons across
37 families, including complete selected tables and representative anchors; see [`../../data/validation/README.md`](../../data/validation/README.md).
The September comparison restored omitted NEXUS log-line-luminosity errors in the raw extraction and
source observables. This is a documented extraction correction, with no change
to object membership or growth masses.

The audit does not turn a published proxy, upper limit, or assumed-Eddington
mass into a canonical mass. Evidence and interpretation remain controlled by
the source notes, taxonomy, and science policy.

The completed numerical-mass audit checks all 248 numerical measurement rows and 744
mass/error fields. It corrects Killi's logarithmic asymmetric errors against
the final published abstract. Other observables retain representative coverage.
