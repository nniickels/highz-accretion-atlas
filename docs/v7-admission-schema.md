# v7 heterogeneous-source admission schema

Status: implemented design and validation gate; no heterogeneous source has
yet been ingested and no v7 release products exist.

The executable contract is `src/v7_admission.py`. It validates proposed
measurement tables before they can enter a v7 catalogue. The validator is
source independent and is tested only with synthetic fixtures at this stage.
It does not read, append to, or regenerate any frozen v1--v6 artifact.

## Identity levels

v7 distinguishes three levels:

1. `measurement_id`: one published measurement row; always unique.
2. `physical_object_id`: one accreting source or candidate nucleus; several
   literature measurements may link here.
3. `host_system_id`: the enclosing galaxy or interacting system; more than one
   candidate nucleus may share it.

Each physical object must map to exactly one host system. A host quantity
repeated for multiple nuclei must use
`host_property_scope=shared_host_system_total`, repeat the same published value,
and must not be counted as independent nuclear host measurements. A missing
host quantity uses `host_property_scope=not_published`.

## Canonical v7 vocabulary

v7 stores underscore-delimited object classes and short evidence labels. In
particular, it uses `broad_line_agn` and `secure`, `probable`, `candidate`, or
`disputed`. Frozen v5/v6 tables retain `broad-line-agn` and labels such as
`probable_accreting_mbh`. `normalize_v7_vocabulary` provides the explicit copy
adapter, including `compact_source`/`red_agn` phenotype spellings; it never
mutates an inherited table. Historical selection tokens remain controlled but
retain their source-specific detail.

Phenotypes remain independent from class and evidence. Controlled phenotype
tags initially include `lrd`, `compact`, `red`, `merger`, `clumpy`, and
`dual_nucleus`. `lrd` is therefore rejected as an `object_class`.

## Mass and ranking fields

Every proposed row records the exact `mbh_method`, asymmetric statistical
errors and their semantics, a separate calibration systematic and kind, and a
coarser `mass_comparability_group`. A method-dependent mass may set
`conditional_mass_flag=true`, but then requires a machine-readable
`conditional_mass_reason`. The initial controlled reasons distinguish a
BLR-dependent virial interpretation, an assumed-Eddington mass, an SED/scaling
model, and unresolved lensing; new reasons require an explicit schema change.

Exploratory eligibility is calculated from the presence of a numeric mass,
redshift, method, uncertainty semantics, resolved lensing treatment, and
resolved identity. The stored flag and reason must exactly match that result.
Primary eligibility additionally requires secure/probable evidence, an
unconditional mass interpretation, and a mass method explicitly marked
appropriate for the primary comparison. Candidate and disputed evidence never
enters the primary rank.

Missing host mass, bolometric luminosity, or Eddington ratio does not affect
growth-rank eligibility. Calibration systematics cannot be marked as already
combined with the statistical errors at admission.

## Lensing and censored observables

`lensing_status` is independent from object class. A lensed row requires a
numeric magnification and provenance. An unresolved lensing correction makes a
numeric mass ineligible until resolved.

Line measurements and other source observables use a separate long-form table
validated by `validate_v7_observables`. Each value is explicitly a `detection`,
`upper_limit`, or `lower_limit`. Limits retain numeric bounds and units but
cannot masquerade as detections with symmetric errors.

## Source admission sequence

For each proposed source:

1. Obtain the authoritative complete source table or stop.
2. Preserve all published rows in a source-specific raw file.
3. Resolve measurement, physical-object, and host-system identities.
4. Map every proposed processed row to this schema and validate it.
5. Validate any long-form observable table and censored values.
6. Test exact evidence, mass-comparability, lensing, and ranking outcomes.
7. Verify every frozen v1--v6 manifest before any v7 release is written.

Passing this gate permits source-specific ingestion work; it does not itself
admit a source or authorize pooled demographic interpretation.
