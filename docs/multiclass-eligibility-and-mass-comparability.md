# Multi-Class Eligibility and Mass-Comparability Contract

Status: required design gate for the first heterogeneous catalogue release
(planned v7). v5 remains a broad-line-AGN release; v6 is reserved for the final
same-class BLAGN consolidation, with THRILS as the preferred candidate pending
an authoritative object-level table audit.

## Purpose

The atlas may eventually contain several kinds of evidence for an accreting
massive black hole. Those records are not interchangeable. This contract keeps
object identity, evidence strength, phenotype, mass inference, and growth-rank
eligibility as separate questions. It prevents a photometric LRD label, an
X-ray excess, or a model-dependent mass proxy from being treated as equivalent
to a secure broad-line virial measurement.

## Independent axes

Every measurement must record these axes independently:

1. `physical_object_id` and unique `measurement_id`.
2. `object_class`: the measurement's accretion-evidence class.
3. `evidence_status`: `secure`, `probable`, `candidate`, or `disputed`, with a
   concise `evidence_status_basis`.
4. `spectroscopic_type`, where established; absence is not Type 2 evidence.
5. `selection_channels`: the channel through which the source entered its
   source sample.
6. `phenotype_tags`: observational descriptors such as `lrd`, `compact`, or
   `red`; phenotype is not an accretion class.
7. `lensing_status` and the lens model/magnification provenance when relevant.
8. `mbh_method`, statistical uncertainty, separately stated systematic, and a
   `mass_comparability_group`.
9. `growth_ranking_eligible_flag` and `primary_growth_ranking_flag`, each with
   a machine-checkable reason.

## Allowed evidence classes

The first multi-class release may use controlled classes such as:

- `broad_line_agn`;
- `narrow_line_agn_candidate`;
- `xray_agn_candidate`;
- `high_ionization_line_candidate`;
- `photometric_agn_candidate`;
- `luminous_quasar_comparison`.

Lensing is a property, not a class. `lrd` is a phenotype, not a class. A source
may have multiple evidence measurements linked to one physical object, but no
single row should collapse several papers or methods into a synthetic value.

## Mass-comparability groups

At minimum, use controlled groups that distinguish:

- `virial_balmer_single_epoch`;
- `virial_uv_single_epoch`;
- `reverberation_or_dynamical_direct`;
- `xray_or_bolometric_proxy`;
- `sed_or_scaling_proxy`;
- `assumed_eddington_ratio_mass`;
- `no_numeric_mass`.

Calibration tags remain more specific than these groups. Statistical posterior
errors and method/calibration systematics must remain separate. Limits and
assumption-derived values stay explicitly censored or model-dependent; they
must not be converted into apparently measured canonical masses.

## Growth-rank gates

A row may enter a complete exploratory growth diagnostic only when it has:

- a defensible numeric black-hole mass measurement or posterior;
- observed redshift and enough provenance to reproduce the growth interval;
- an identified mass method and uncertainty semantics;
- resolved lensing treatment when the inferred mass depends on magnification;
- no unresolved physical-object identity ambiguity.

The primary growth rank is stricter. It requires `secure` or `probable`
accreting-massive-BH evidence and a mass method suitable for the stated
comparison. Candidate and disputed objects remain in evidence/caveat tables
and, when numerically eligible, in explicitly exploratory diagnostics; they do
not receive a primary rank.

No object is penalized because a paper did not publish host mass, bolometric
luminosity, or Eddington ratio. Those diagnostics remain unavailable.

## Comparison policy

- Publish measurement- and physical-object-level views.
- Count a linked physical object once in object-level summaries.
- Keep class-, selection-, source-, and mass-method strata visible.
- Do not infer demographics from pooled unlike selection functions.
- Do not compare rank positions across incompatible mass groups without an
  explicitly labelled sensitivity analysis.
- Maintain a global exploratory diagnostic only as a navigation tool; paper
  claims should use class-specific or comparability-qualified primary ranks.

## Ingestion and validation gate

Before a heterogeneous source is accepted, tests must verify:

- unique measurement IDs and stable physical-object links;
- controlled class/evidence/phenotype/lensing/mass-group values;
- nonempty basis fields for candidate or disputed classifications;
- correct handling of limits, missing values, and method systematics;
- exact eligibility outcomes and exclusion reasons;
- source- and class-stratified counts at both catalogue views;
- unchanged frozen v1--v6 artifacts.

ALPINE-CRISTAL and other heterogeneous candidate sets belong after this gate,
in v7 or later. THRILS remains the preferred candidate for the next v6
same-class BLAGN source, conditional on an authoritative object-level table.
