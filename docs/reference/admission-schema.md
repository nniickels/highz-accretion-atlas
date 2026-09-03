# Heterogeneous-source admission schema

Every source admitted to v2 or v3 must provide stable measurement, physical
object, and host-system identities; source/version provenance; independent
evidence, class, phenotype, lensing, and mass-method fields; and explicit
eligibility reasons.

Admission validation requires:

1. unique measurement IDs and exactly one preferred measurement per object;
2. controlled evidence, class, lensing, and mass-comparability values;
3. nonempty bases for candidate, disputed, conditional, or excluded rows;
4. separate statistical and method-systematic uncertainty fields;
5. reviewed identity decisions for candidate cross-source matches;
6. source-local observables with measurement-level provenance;
7. exact measurement/object/host cardinalities and nested v1 < v2 < v3 membership;
8. source-caveat and exclusion coverage in generated results.

Assembly inputs are described in [`../../data/assembly/README.md`](../../data/assembly/README.md).

## Canonical object aggregation

The measurement schema is shared across v1, v2, and v3. The object table adds:

- `all_measurement_evidence_statuses`
- `all_measurement_evidence_status_bases`
- `object_evidence_aggregation_policy`

Exactly one preferred measurement per physical object controls the object-level
`evidence_status` and `evidence_status_basis`. The history columns retain every
distinct measurement-level value. Eligibility is recomputed from the preferred
status and the numeric, method, identity, and lensing contracts above.

Current row counts are release properties recorded in the dataset manifests,
rather than part of this stable schema.
