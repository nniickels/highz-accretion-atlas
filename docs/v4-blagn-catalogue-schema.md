# v4 BLAGN catalogue and identity schema

v4 adds Matthee EIGER/FRESCO and Lin ASPIRE to the frozen v3 catalogue. It
contains 96 literature measurements representing 94 physical objects at
z >= 4. No v1--v3 file is overwritten.

## Release products

| Product | Rows | Purpose |
| --- | ---: | --- |
| `data/raw/matthee23_eiger_fresco_blagn_tables1_3.csv` | 20 | Source-native Tables 1--3 extraction |
| `data/raw/lin24_aspire_blagn_tables1_3.csv` | 16 | Source-native Tables 1--3 extraction |
| `data/processed/v4_blagn_measurements.csv` | 96 | Lossless literature-measurement analysis view |
| `data/processed/v4_blagn_objects.csv` | 94 | One default measurement per physical object |
| `data/crossmatch/v4_measurement_object_links.csv` | 96 | Measurement-to-object links and default rules |
| `data/crossmatch/v4_object_aliases.csv` | 96 | Source aliases and coordinates by physical object |
| `data/crossmatch/v4_reviewed_match_candidates.csv` | 1 | Reviewed new coordinate/redshift match |
| `data/crossmatch/v4_reviewed_identity_overrides.csv` | 1 | Explicit accepted/rejected identity decisions |

## Identity and default measurements

`measurement_id` identifies one published measurement; `physical_object_id`
identifies the astrophysical source. `data/crossmatch/v4_measurement_object_links.csv`
stores the one-to-many mapping and the default-measurement rule. Existing v3
preferences are retained for longitudinal reproducibility. Therefore the new
Matthee measurement of GS-204851 is not made the default, even though it is
fully preserved and independently rankable. Aliases and reviewed candidate
metrics are separate files.

The two multiply measured physical objects are:

- `HZA-CEERS-2782`: Taylor CEERS-2782 and RUBIES-EGS-50052; the RUBIES
  measurement remains the v3 default.
- `HZA-GS-204851`: JADES GS-204851 and Matthee GOODS-S-13971; the prior JADES
  measurement remains the v4 default for longitudinal reproducibility.

Every other object has one measurement in v4. Default selection is a
reproducible view rule, not a claim that the alternative measurement is
scientifically invalid. Both alternatives are exercised by the separate
`results/v4_blagn_alternate_measurement_sensitivity.csv` product without
changing either release default.

The candidate search uses a 0.5 arcsec coordinate threshold and
`delta-z <= 0.01`, checks each new source against both the prior release and
other new sources, rejects ambiguous multi-candidate choices, and requires an
explicit accepted/rejected registry row before linking. Registry rows label
their origin as `threshold_candidate` or `manual_assertion`. A manual assertion
may support a published alias outside the thresholds only when both measurement
IDs are known and its review basis, reference, and date are nonblank. It is
deterministic candidate generation followed by review, not a probabilistic
cross-match model.

New singleton IDs are checked against all inherited and already allocated IDs.
If two unrelated papers normalize to the same readable object token, the later
allocation receives a source namespace; a second collision is a hard error.
Every pre-v4 physical-object ID remains unchanged.

## Canonical and source-native fields

The standardized core retains coordinates, redshift, MBH and asymmetric formal
errors, method tags, source provenance, and missingness flags. Source-native
extensions preserve Halpha luminosities, line widths, broad/total ratios,
equivalent widths, relevant photometry and continuum slopes, LRD phenotype,
absorption-fit flags, and row caveats. Matthee's linearly published Lbol is
converted to log cgs with exact logarithmic error propagation in processing;
the native values remain in the raw and processed tables. This is a unit
transformation, not an inferred measurement.

Important field groups are:

- identity: `measurement_id`, `physical_object_id`, `object_id`, survey, field,
  coordinates, aliases, and preferred-measurement metadata;
- black-hole mass: `log_mbh_msun_std`, asymmetric formal errors, `mbh_method`,
  and separately stored calibration systematics;
- line observables: broad/total Halpha luminosity, broad-to-total ratio, broad
  FWHM, equivalent width, and reported uncertainties where available;
- phenotype/evidence: `object_class`, `lrd_flag`, `lrd_definition`, detection
  evidence, absorption-fit flag, caveat tags, and notes;
- provenance: source key/table, paper version, URL/DOI, archive URL/checksum,
  extraction date, and selection criteria.

## Missingness and mass calibration

Host stellar mass and a source-reported Eddington ratio remain missing for the
two new sources. A comparison Eddington ratio may be calculated from published
MBH and Lbol, but it remains in `edd_ratio_from_mbh_lbol`; it never populates
`edd_ratio_std` or masquerades as a reported value.

The reviewed source/method mapping is in `data/mass_method_registry.csv`. It
records the exact JADES Halpha calibration (Reines & Volonteri 2015; 0.3 dex
calibration uncertainty) and Hbeta calibration (Vestergaard & Peterson 2006;
no numeric systematic stated in the JADES source), without changing the frozen
generic JADES method tags. The Reines et al. (2013) Halpha single-epoch tag for
Taylor, Matthee, and ASPIRE is
`single-epoch-virial-halpha-reines2013`. The 0.5 dex calibration/intrinsic
uncertainty is stored in `log_mbh_systematic_dex` and is not folded into formal
errors.

## LRD and evidence semantics

`lrd_flag` is independent of `object_class=broad-line-agn`:

- Taylor uses the object-level marker published in Table 1.
- Lin Table 1 explicitly calls all 16 ASPIRE objects LRDs.
- Matthee is treated as an LRD sample at paper level; Tables 1--3 do not contain
  an object-by-object marker. Its rows therefore use
  `lrd_definition=paper_sample_label_little_red_dot`, and the flat-continuum
  exception remains in the row caveats.

The object view takes the logical union of phenotype evidence across retained
measurements and records both supporting measurement IDs and source keys. It
also retains `preferred_measurement_lrd_flag`. Source-stratified summaries use
that preferred-measurement attribution while separately reporting the
any-measurement union, preventing an LRD label supplied by one paper from being
silently credited to another source.

For the two new sources, `quality_flag=robust` and
`detection_evidence=individual_robust` describe the published broad-line
detection. They do not erase absorption-model, contamination, dust, or virial
mass caveats. v4 rankings therefore record `detection_confidence_*` separately
from `mass_measurement_reliability_*`; absorption or contamination can lower
the latter without disputing a robust broad-line detection.

## Validation anchors

The processing layer requires 20 Matthee and 16 ASPIRE rows, all at `z >= 4`,
with 2 and 3 absorption-fit rows respectively. The combined release must have
96 unique measurements, 94 physical objects, exactly one preferred measurement
per physical object, and exactly the two multiply measured objects listed
above.
