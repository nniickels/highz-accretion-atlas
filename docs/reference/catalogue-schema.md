# Catalogue schema and eligibility

The measurement schema is shared across v1, v2, and v3. The
[data field guide](../../data/README.md#columns-units-and-missing-values) explains
column names and units. Counts belong to the [version guide](../guides/versioning.md).

## Classification fields

AGN, broad-line AGN, quasars, and little red dots (LRDs) are not interchangeable.
Canonical rows separately record:

- `object_class` and `spectroscopic_type`;
- `evidence_status`: `secure`, `probable`, `candidate`, or `disputed`, with a basis;
- selection channels and phenotype tags, including `lrd`;
- lensing status and correction provenance;
- mass method, reported errors, additional method systematics, and comparability;
- identity decisions and numerical/primary growth eligibility with reasons.

Classes include broad-line AGN and narrow-line, high-ionization, photometric,
and X-ray candidates. Lensing and LRD phenotype are independent of object class.
Mass-comparability groups distinguish Balmer and UV single-epoch virial masses,
direct methods, proxies or assumed-Eddington estimates, and missing numeric masses.
Limits and conditional estimates are not promoted to measured canonical masses.

## Preferred measurements and object aggregation

Each physical object has exactly one preferred measurement. That row controls
its canonical evidence and mass status. The object table retains all linked
measurement IDs, source keys, evidence statuses and evidence bases in
`available_measurement_ids`, `available_source_keys`,
`all_measurement_evidence_statuses`, and `all_measurement_evidence_status_bases`.
`object_evidence_aggregation_policy` records how the preferred row is used.
Alternate measurements remain visible without adding independent objects.

## Growth eligibility and publication selection

`growth_ranking_eligible_flag` requires a supported numeric mass and redshift,
a reproducible method, and accepted assembly identity and lensing treatment.
`primary_growth_ranking_flag` additionally requires sufficiently credible
(`secure` or `probable`) evidence and a suitable comparison method.
`primary_mass_comparison_flag` describes method comparability; it does not by
itself establish primary growth or manuscript membership.

Candidate, disputed, conditional, and mass-free records remain in the catalogue
and caveat products. Assembly identity status does not certify independently
established astrophysical uniqueness: the [identity audit](../source-notes/redshift-identity-audit.md)
can impose stricter exclusions. Use the [publication selection](../../data/publication/README.md#sample-selection)
for manuscript analyses, rather than substituting a single catalogue flag.
Global ranks are navigation aids. Scientific comparisons must respect compatible
classes, methods, and source [selection functions](selection-completeness.md).

`scientific_identity_status` records that independent audit separately from
assembly status. It is `unresolved` for open groups and `no_open_issue_recorded`
otherwise; the latter does not certify uniqueness. `scientific_identity_issue_group`
identifies each open group and propagates to every linked measurement.

Source-reported errors can already include calibration terms. These are retained
once; additional method systematics remain separate unless a sensitivity test
explicitly applies them. Missing errors do not imply exact masses.

## Admission checks

Every admitted source requires source/version provenance, explicit missingness
and uncertainty semantics, reviewed cross-source identities and host assignments,
and source-local observables. Validation checks:

1. unique measurement IDs and exactly one preferred measurement per object;
2. controlled class, evidence, lensing, and mass-comparability values;
3. nonempty bases for candidate, disputed, conditional, and excluded records;
4. source-reported errors and separate additional-systematic fields;
5. measurement/object/host links, nested v1 < v2 < v3 membership, and cardinalities;
6. source caveats and exclusions in generated results.

[Assembly inputs](../../data/README.md#assembly-inputs) supply the shared builder.
`src.internal.verify_versions` checks these requirements. Historical admission
implementations under `src/internal/compatibility/` support reconstruction;
their filenames do not define additional public catalogue versions.
