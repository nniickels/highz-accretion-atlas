# High-z Accretion Atlas: Catalogue Expansion Guide

Status: working research guide; first same-class additions completed through v4
Literature review date: 2026-08-17; implementation audit: 2026-08-22
Repository scope at audit: v4 JADES + Taylor + Matthee + Lin broad-line AGN catalogue

## Purpose

This guide records the scientific scope, source priorities, taxonomy, and data-model
requirements for expanding the atlas beyond v1. It is a decision guide rather than
an ingestion manifest: sample sizes and interpretations must be checked against the
latest paper version when a source is actually added.

The recommended public description is:

> A source-tracked, uncertainty-aware catalogue of high-redshift accreting
> massive-black-hole systems and candidates, with growth calculations restricted
> to objects that have sufficiently credible black-hole mass constraints.

The shorter phrase "accreting objects" is too broad unless the massive-black-hole
context is explicit. It can otherwise include protostars, white dwarfs, neutron
stars, and stellar-mass X-ray binaries.

## Current Baseline and Expansion Principle

The v1 processed catalogue contains 23 measurements at `z >= 4`, all from the
Juodzbalis/JADES Type 1 broad-line AGN sample. The black-hole masses are
single-epoch virial estimates based on broad Halpha or Hbeta emission.

The lowest-risk expansion path is therefore:

1. Add more spectroscopically confirmed broad-Balmer-line AGN first.
2. Establish physical-object cross-matching and measurement versioning before
   ingesting heavily overlapping archival compilations.
3. Add evidence-selected classes such as narrow-line, X-ray, and photometric LRD
   candidates only after the taxonomy and class-specific eligibility rules exist.
4. Keep luminous quasars as a separate comparison stratum rather than pooling
   them uncritically with faint JWST BLAGN.

This sequence preserves comparability with v1 while gradually widening the
selection function.

## Recommended Source Order

### Tier 1: same-class foundation and next measurement layer

These sources define the lowest-risk same-class expansion because they contain
broad Balmer lines and object-level quantities close to the v1 schema. Taylor,
Matthee, and Lin are complete; Harikane is the next overlapping measurement
layer.

| Priority | Source | Current reported sample | Recommended atlas role | Main cautions |
| --- | --- | --- | --- | --- |
| 1 | [Taylor et al., CEERS/RUBIES](https://arxiv.org/abs/2409.06772) | 62 Halpha BLAGN at `3.5 < z < 6.8`; 21 have an LRD phenotype | Completed in v3; the `z >= 4` subset retains the row-level LRD marker | Current paper supersedes the 50-object number in the older source memo; approximately 0.5 dex virial-mass systematics are not represented by the small statistical errors; overlaps earlier CEERS work |
| 2 | [Matthee et al., EIGER/FRESCO](https://arxiv.org/abs/2306.05448) | 20 broad-Halpha sources at `z ~ 4.2-5.5` | Completed in v4; independent, line-selected NIRCam WFSS sample | Blind slitless broad-Halpha selection differs from targeted NIRSpec samples; compact/red properties were characterized after selection; the LRD designation is paper-level rather than a row marker; nominal masses and Lbol are not dust-corrected |
| 2 | [Lin et al., ASPIRE](https://arxiv.org/abs/2407.17570) | 16 broad-Halpha sources at `z ~ 4-5` in 25 fields | Completed in v4; independent-field check with tabulated `MBH` and `Lbol` | Compact/red preselection; no tabulated source-reported Eddington ratio or host mass in the extracted tables; nominal masses and Lbol are not dust-corrected; approximately 0.5 dex virial systematic |
| 3 | [Harikane et al.](https://arxiv.org/abs/2303.11946) | 10 Type 1 AGN at `z = 4.015-6.936` | Next same-class measurement layer, with host information | Known overlap with later CEERS/JWST compilations; preserve as measurements, not automatically ten new physical objects |

The completed Taylor, Matthee, and ASPIRE sequence establishes the current v4
same-class foundation. Harikane and earlier discovery papers should now be
attached as measurements of matched objects before another large compilation
is ingested.

### Tier 2: selection-bias and lower-confidence extensions

| Source | Current reported sample | Recommended atlas role | Main cautions |
| --- | --- | --- | --- |
| [Davis et al., THRILS](https://arxiv.org/abs/2602.23310) | Six newly identified BLAGN, within a seven-object broad-line set at `3.5 < z < 7` | Tests recovery of weak or host-dominated broad components in very deep spectra | Small sample; apply the `z >= 4` cut; confirm which objects are genuinely new after cross-match |
| [Ren et al., ALPINE-CRISTAL-JWST](https://academic.oup.com/mnras/article/544/1/211/8301219) | Seven AGN candidates in 18 massive galaxies at `z = 4.4-5.7` | Host-selected counterpoint with low inferred masses and host properties | Only one is highly robust; possible outflow/intermediate-width contamination; retain evidence tiers and a roughly 0.4 dex mass-systematic floor |

These sources should not be assigned the same evidence quality merely because a
virial mass is tabulated. Detection confidence and mass uncertainty are separate
attributes.

### Tier 3: large overlapping compilations and remeasurements

| Source | Current reported sample | Recommended atlas role | Prerequisite |
| --- | --- | --- | --- |
| [Baccus and Xu](https://arxiv.org/abs/2512.03281) | 252 BLAGN at `z = 0.8-7.2`, including 171 reported as new | Large archival completeness audit and bulk expansion after applying `z >= 4` | Stable `physical_object_id`, aliases, coordinate matching, survey provenance, and duplicate-measurement handling |
| [Jones et al.](https://arxiv.org/abs/2510.07376) | Uniform analysis of 70 CEERS/JADES/RUBIES BLAGN; 43 percent identified as LRDs | Host-mass and `MBH/Mstar` measurement layer; useful uniform reanalysis | Must be treated as measurements of overlapping physical objects, not as 70 automatically new objects |

The correct design is one row per paper measurement linked to one physical-object
record. Do not choose one paper and silently overwrite another. Differences among
line fits, virial calibrations, lens models, host decomposition, and SED fitting
are part of the scientific result.

### High-redshift, high-leverage individual benchmarks

These are valuable sensitivity tests and spotlight objects, but they do not expand
the catalogue statistically in the same way as a survey sample.

| Object/source | Why include it | Required treatment |
| --- | --- | --- |
| [CAPERS-LRD-z9](https://arxiv.org/abs/2505.04609), `z = 9.288` | Broad Hbeta at very high redshift; canonical `log10(MBH/Msun) ~ 7.58` | Retain the much broader method-dependent range, roughly `6.65-8.50`; do not present the canonical value as a precision mass |
| [UNCOVER z=8.50 BLAGN](https://arxiv.org/abs/2308.11610) | Broad Hbeta, high inferred mass, lensing, and a stringent host constraint | Carry lensing assumptions and uncertainties explicitly |
| [Abell 2744-QSO1 direct-mass analysis](https://arxiv.org/abs/2508.21748) | Rare direct/dynamical check on virial estimates at `z = 7.04` | Add as another measurement of an existing physical object; do not create a duplicate object |
| [GN-z11 AGN analysis](https://www.nature.com/articles/s41586-024-07052-5) | Extreme-redshift accretion benchmark at `z = 10.6` | Use cautious evidence and mass-method flags; it is not as straightforward as broad Halpha BLAGN |
| [GHZ2 AGN-contribution model](https://arxiv.org/abs/2511.03035) | Possible accretion contribution at `z = 12.34` | Candidate/evidence catalogue only unless an independent mass posterior is available; the reported mass depends on an assumed Eddington ratio and has order-dex systematics |

### Luminous quasar anchors

Use [XQR-30](https://arxiv.org/abs/2306.16474) as the preferred homogeneous
high-luminosity comparison set. It contains 42 `z > 6` quasars with high-quality
VLT/X-shooter spectroscopy and object-level luminosity, Mg II/C IV mass, and
Eddington-ratio measurements.

Keep this as a distinct analysis stratum because luminous colour-selected quasars
have a different selection function, luminosity range, emission-line calibration,
and completeness model from faint JWST Balmer-line AGN. Older individual quasars
and smaller samples remain useful historical benchmarks but need not be ingested
before XQR-30.

## Sources That Need Reclassification or Special Caution

### UHZ1 is disputed, not a confirmed high-priority addition

The full-exposure 2026 Chandra reanalysis reports only a `2.3-2.9 sigma` excess and
finds that the earlier stronger detection is sensitive to astrometric choices.
The MIRI constraints also do not require a luminous obscured AGN. UHZ1 may remain
in the evidence catalogue with `disputed` status, but it should not enter the main
growth ranking as a confirmed black hole without stronger evidence.

Source: [Napolitano et al. UHZ1 reanalysis](https://arxiv.org/abs/2603.24893).

The original mass interpretation was obtained under an approximately
Eddington-limited assumption. A mass inferred by assuming an Eddington ratio is
not an independent test of whether Eddington-limited growth was required.

Source: [original UHZ1 interpretation](https://arxiv.org/abs/2308.02654).

### Small discovery papers are often measurements, not new catalogue objects

Kocevski CEERS sources, CEERS 1019, GS-3073, Furtak's Abell 2744-QSO1, and similar
discovery papers remain important. Their later appearance in survey catalogues
must not be counted as another physical object. Preserve their measurements and
interpretive history through measurement versioning.

## Recommended Object Taxonomy

A single flat `object_class` is insufficient. The atlas should represent several
orthogonal axes.

### 1. Physical evidence status

Suggested values:

- `secure_accreting_mbh`
- `probable_accreting_mbh`
- `candidate_accreting_mbh`
- `disputed_accreting_mbh`

Evidence status should describe confidence that a massive accreting black hole is
present. It should not be conflated with the uncertainty on its mass.

### 2. Spectroscopic or obscuration type

Suggested values:

- `type1_broad_line`
- `type2_narrow_line`
- `intermediate_or_ambiguous`
- `unknown`

Type 1 versus Type 2 describes observational visibility and obscuration, not a
different physical engine.

### 3. Selection and evidence channels

Allow multiple values per object or measurement:

- broad Halpha
- broad Hbeta
- broad Mg II
- broad C IV
- X-ray
- high-ionization or coronal lines
- radio
- variability
- photometric/SED selection
- dynamical or spectroastrometric signature

This enables later analyses to compare objects selected in genuinely different
ways.

### 4. Phenotype and luminosity tags

Suggested independent tags:

- `lrd`
- `quasar_luminosity`
- `faint_agn`
- `host_dominated`
- `compact_red_source`

An LRD is a compact red or V-shaped-SED phenotype, not a physical engine. A
spectroscopically confirmed object can simultaneously be an LRD and a Type 1
BLAGN. A photometric-only LRD is not automatically an AGN: dusty star formation,
dense gas, unusual stellar populations, and foreground contaminants can reproduce
parts of the selection.

A quasar is a high-luminosity AGN, not a separate kind of compact object.

### 5. Modifiers

Suggested flags:

- lensed/unlensed/unknown
- dual or offset candidate
- host blended
- variable
- outflow contamination possible

Lensing is never the primary object class. Its magnification and uncertainty affect
inferred luminosity, host mass, and virial mass in different ways.

### 6. Black-hole mass method

At minimum distinguish:

- single-epoch Halpha virial
- single-epoch Hbeta virial
- single-epoch Mg II virial
- single-epoch C IV virial
- dynamical or spectroastrometric
- reverberation mapping
- X-ray luminosity plus assumed Eddington ratio
- SED/model-inferred mass
- no mass estimate

Also track whether the mass is independent of an assumed Eddington ratio. An
X-ray or SED mass computed from `Lbol` by assuming `lambda_Edd` must not be used as
independent evidence for a growth requirement involving that same assumption.

### 7. Interpretation tags are not observed classes

Labels such as `light_seed_descendant`, `heavy_seed_candidate`, `DCBH`, `PBH`, or
`overmassive_black_hole` are model interpretations. Store them as hypotheses with
sources, never as the primary observed class.

## Why These Classes Share an Accretion Framework

AGN, quasars, Type 1 AGN, Type 2 AGN, X-ray AGN, and confirmed AGN-hosting LRDs
can share the same physical engine: gravitational binding energy released as gas
accretes onto a massive black hole. Accretion increases black-hole mass after the
radiated fraction is removed, so the atlas growth equation can be applied across
selection classes when credible `MBH` and redshift posteriors exist.

This does not imply that all labels identify one homogeneous population or one
evolutionary sequence:

- A black hole may be dormant; "black hole" alone does not imply current accretion.
- An LRD may lack a black hole; "LRD" alone does not imply AGN activity.
- Broad lines, narrow lines, X-rays, and red SEDs require class-specific emission,
  obscuration, and radiative-transfer models. The growth equation does not explain
  those observables by itself.
- Present `Lbol/Ledd` is an instantaneous or short-timescale quantity. The
  atlas's required `f_Edd` is a lifetime-averaged growth requirement. They are not
  interchangeable.
- Black-hole mergers also add mass. Accretion is not the only growth channel.

The common growth calculation is therefore selection-agnostic mathematically but
not measurement-agnostic scientifically.

## Growth-Eligibility Rules

Maintain an evidence catalogue broader than the growth-ranking sample.

An individual measurement should normally be `growth_eligible = true` only when:

1. A sufficiently reliable redshift posterior exists.
2. A black-hole mass posterior or defensible uncertainty interval exists.
3. The mass method and its dependencies are explicit.
4. Lensing corrections and uncertainties are documented when applicable.
5. The evidence status is adequate for the analysis being reported.

Examples normally excluded from the primary growth ranking:

- photometric-only LRDs with no spectroscopic AGN evidence;
- high-ionization-line candidates with no credible `MBH` estimate;
- marginal X-ray sources whose detection is disputed;
- masses obtained only by assuming the Eddington ratio that the analysis intends
  to test;
- point estimates with no usable uncertainty model.

Such objects can still be scientifically valuable and should remain visible in a
candidate or evidence table.

## Data-Model Prerequisites

Complete these before large multi-paper ingestion:

1. Add stable `physical_object_id` values distinct from `measurement_id`.
2. Create an alias and manual cross-match table using coordinates, field, redshift,
   lens image identifiers, and published aliases.
3. Preserve one measurement row per paper or analysis rather than selecting one
   value silently.
4. Separate evidence confidence, mass quality, and phenotype.
5. Expand the current evidence vocabulary beyond the v1 robust/tentative broad-line
   categories.
6. Add `growth_eligible` and a reason for exclusion.
7. Record source-level selection functions and targeting/preselection rules.
8. Record direct observables separately from derived quantities and assumed priors.
9. Apply method-specific uncertainty floors. Broad-line virial masses commonly
   require roughly `0.4-0.5 dex` systematic allowances even when formal fit errors
   are much smaller.
10. Propagate lensing uncertainty rather than storing only a nominal
    magnification.
11. Produce both measurement-level and physical-object-level rankings.
12. Stratify demographic and ranking comparisons by selection channel and mass
    method before considering pooled results.

## Suggested Execution Sequence

1. Freeze the v2 ranking and uncertainty definitions evaluated on the v1 catalogue.
2. Design and validate physical-object matching and measurement versioning.
   **Completed for the JADES + Taylor release (2026-08-17).**
3. Ingest the `z >= 4` Taylor CEERS/RUBIES subset.
   **Completed in v3 (2026-08-17): 37 measurements / 36 physical objects; v3
   science products contain 60 measurements / 59 physical objects.**
4. Ingest Matthee EIGER/FRESCO and Lin ASPIRE as complementary survey selections.
   **Completed in v4 (2026-08-22): 36 measurements; one Matthee/JADES crossmatch;
   96 measurements / 94 physical objects in the combined release.**
5. Attach Harikane and earlier discovery-paper measurements to matched physical
   objects.
6. Add THRILS and evidence-graded ALPINE-CRISTAL candidates.
7. Add high-redshift spotlight objects with explicit method-dependent bounds.
8. Add Jones et al. as a host-mass/remeasurement layer.
9. Audit and ingest the `z >= 4` Baccus and Xu catalogue only after duplicate
   resolution is working.
10. Add XQR-30 as a separately plotted luminous-quasar anchor.
11. Add narrow-line, X-ray, and photometric candidate populations under
    class-specific evidence and growth-eligibility rules.

## Source-Memo Corrections to Remember

The older `docs/catalogue-expansion-candidates-legacy.md` remains useful as a historical
working list, but future tasks should account for these changes:

- Matthee EIGER/FRESCO and Lin ASPIRE are completed in v4 from their
  authoritative arXiv source archives.
- The generalized identity layer is active. GOODS-S-13971 and GS-204851 are
  one physical object; all source measurements remain available.

- Taylor et al. now reports 62 objects rather than the older 50-object count.
- THRILS, ALPINE-CRISTAL-JWST, Baccus and Xu, Jones et al., CAPERS-LRD-z9,
  and XQR-30 should be evaluated explicitly.
- UHZ1 should be marked disputed and excluded from a confirmed-object growth
  ranking unless stronger evidence appears.
- The direct-mass analysis of Abell 2744-QSO1 is a calibration/measurement-version
  anchor, not a new physical object.
- GHZ2 remains model-dependent and candidate-only for present purposes.

## Literature Currency Rule

Before ingesting any source:

1. Check the latest arXiv version and peer-reviewed publication, if available.
2. Verify the current sample size and table contents.
3. Search for retractions, errata, follow-up analyses, and disputed detections.
4. Check whether the same physical objects appear in newer survey compilations.
5. Record the literature-check date in the source registry or ingestion notes.

This is especially important for active JWST literature, where object counts,
redshifts, line decompositions, and AGN interpretations can change between
preprint versions.
