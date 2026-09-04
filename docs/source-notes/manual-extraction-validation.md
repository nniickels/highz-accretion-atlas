# Manual extraction validation

Reviewed 2026-09-03 and amended 2026-09-04. `data/manual_extraction_audit.csv` inventories all 25
row-level CSV inputs plus the source-native Scholtz TeX table. Each record pins
the checked-in bytes, expected parsed row count, source-family membership, and
the source-table locator described in the extraction notes.

Run `.venv/bin/python -m src.internal.verify_manual_extractions` to check the
audit. The verifier fails on changed bytes, row counts, duplicate measurement
identifiers, source-family drift, or a changed 41-row Scholtz parse. These gates
complement the source-archive hashes in the provenance registry and the
source-specific scientific anchors in the test suite.

These integrity checks cannot establish original transcription accuracy. A
fresh independent comparison on 2026-09-04 provides 2,041 field checks covering all 32 families, including complete
selected tables and representative anchors for the remaining sources; see [`../../data/validation/README.md`](../../data/validation/README.md).
It restored omitted NEXUS log-line-luminosity errors in the raw extraction and
source observables. This is a documented extraction correction, with no change
to object membership or growth masses.

The audit does not turn a published proxy, upper limit, or assumed-Eddington
mass into a canonical mass. Evidence and interpretation remain controlled by
the source notes, taxonomy, and science policy.

The completed numerical-mass audit checks all 244 measurement rows and 732
mass/error fields. It corrects Killi's logarithmic asymmetric errors against
the final published abstract. Other observables retain representative coverage.
