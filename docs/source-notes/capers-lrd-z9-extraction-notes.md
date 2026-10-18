# CAPERS-LRD-z9: published-value extraction and admission assessment

Source reviewed and retrieved 17 October 2026; literature cutoff 3 September
2026. This note documents source measurements, conventions, and the adopted
catalogue admission. The dated identity screen uses the pre-expansion catalogue.

## Source version and publisher correspondence

Adopt [Taylor et al., arXiv:2505.04609v4](https://arxiv.org/html/2505.04609v4),
dated 24 June 2025. The arXiv history identifies v4 as the accepted ApJL revision,
adding referee changes and the flexible-dust appendix; there is no later arXiv
revision in the retrieved record. All measurement fields here use v4 alone.

Publisher-deposited [Crossref metadata](https://api.crossref.org/works/10.3847/2041-8213/ade789)
verifies DOI `10.3847/2041-8213/ade789`, Taylor as first author, the corresponding
title and target redshift, and *The Astrophysical Journal Letters* **989**, L7,
published 6 August 2025. The publisher-deposited abstract also agrees on the
canonical mass and systematic bounds. The publisher article endpoint was denied
to the browsing service; this is bibliographic/abstract correspondence, not a
claim of a line-by-line comparison with the publisher's full tables. The pinned
accepted v4 is the numerical authority, so that access limit does not require
mixing versions or prevent this extraction.

Retrieved TeX archive: `https://arxiv.org/src/2505.04609v4`, SHA-256
`b176066077fcf145f797d86124a8b97fa65dbf3dce709d25783fec57ad92a885`.
Retain its original `main.tex` without modification, SHA-256
`d46df6b4eed520596435c53115a74abcc0eee697b1381983ca07f3259bc6b6ea`.
The archive's figure binaries and style files are unnecessary to the numerical
admission and are not retained. The source manifest records the separately
retrieved HTML hash and the hashes of every retained supporting payload.

## Complete screen and identity assessment

All three tables and the sole appendix were reviewed. Table 1 has **25 property
rows for one object**; Table 2 has **11 model-parameter rows for that same
object**; Appendix A/Table 3 has **12 alternative-model parameter rows for the
same object**. No table contains an additional target, companion, or source
catalogue. All 48 data rows are preserved, with row numbers and source locators,
in `capers_lrd_z9_v4_table_cells.csv`; model-grid parameters are context, not
additional objects or black-hole measurements.

`capers_lrd_z9_v4_screen.csv` gives 19 screen entries: the original target and
18 literature/control entries or series. Figure 6's eleven comparison series
are recorded individually by their source legend, including the legacy quasar
compilation, Akins, Furtak, Lin, Naidu, Kokorev, Tripodi, Larson, Goulding, GHZ9,
and GN-z11. They are literature points, not new measurements made here. The
named spectral/break comparisons MoM-BH*-1, Abell2744-QSO1, UNCOVER-45924
(also A2744-45924), RUBIES-UDS-154183, and RUBIES-BLAGN-1 likewise supply no
new mass measurement in this source. RUBIES-UDS-154183 is additionally below
scope at z=3.55. The 232 z<0.95 DESI controls and their 20-object red stack are
outside scope; a stack does not create a physical catalogue object. Figure 5's
external host-mass comparisons are also not new CAPERS targets. Reference lists
and background survey descriptions are not interpreted as source object tables.

The original source target is **CAPERS-LRD-z9**, explicitly aliased in II.1 to
**CAPERS-COSMOS-119334**. Three MSA configurations and 18 exposures are repeated
observations of this one object. Table 1 gives RA=150.1362532 deg,
Dec=2.3080298 deg; the paper does not explicitly name a coordinate frame/equinox.
Preserve this missing frame statement rather than inventing ICRS provenance.

Both v2 and v3 measurement and object tables and their alias tables were searched
for the target IDs, and every measurement with coordinates was compared by a
great-circle distance independently of redshift. Neither version has an alias
match or a neighbour within 2 arcsec. The nearest measurement in both is ZS7,
185.34772 arcsec away at z=7.15. The v3 object named
`capers-cos07_6368_35805` is 296.79050 arcsec away at z=6.528 and is distinct;
a survey/program-name match is not an identity match. v2 has no missing-coordinate
rows; v3 has 27, individually retained in the identity fixture. They are GHZ2,
MoM-BH*-1, and 25 named CEERS/Mazzolari targets with different redshifts and no
CAPERS target alias. Their missing positions limit a positional census, but none
supplies evidence of this target's identity. Existing unresolved identity groups
remain unaffected.

**Adopted identity outcome:** one new object, one new host, one new preferred
measurement, zero matches to existing catalogue objects. The canonical IDs are
`CAPERSLRDz9_taylor25`, `HZA-CAPERS-LRD-Z9`, and `HZS-CAPERS-LRD-Z9` for the
measurement, physical object, and host, respectively. `capers_lrd_z9_identity_checks.json`
records the exact inspected input hashes, nearest rows, and missing-coordinate
records. It is a dated source assessment, not a requirement to keep future
catalogue hashes unchanged after admission.

## Published mass, errors, and independent alternatives

Table 1 and IV.2 give the preferred source estimate
**log10(MBH/Msun)=7.58 +/- 0.15**, using broad Hbeta and Greene & Ho (2005)
equation 10 (reprinted as equation 1):

`MBH/Msun = (2.4 +/- 0.3) * 10^6 * (L_Hbeta/10^42 erg/s)^(0.59 +/- 0.06) * (FWHM_Hbeta/1000 km/s)^2`.

The 0.15 dex error propagates line-flux, line-width, and empirical calibration
coefficient uncertainties. It is **not purely statistical**, does not include
the full high-redshift applicability systematic, and is not an extra 0.15-dex
term to add to those same coefficient errors again. It is already logarithmic;
no linear-to-log error conversion is needed. The source adopts this canonical,
uncorrected-for-dust estimate for its later comparisons.

The source separately discusses additional high-redshift systematics as large
as **0.5–0.7 dex**. Preserve that range and its meaning. Do not substitute its
midpoint as a measured Gaussian error, add it automatically to the quoted
0.15 dex, or silently assign one scalar `log_mbh_systematic_dex`. A dedicated
sensitivity calculation can adopt explicit assumptions later.

| Estimate in IV.2 | Reported value (log10 Msun) | Meaning and catalogue treatment |
| --- | --- | --- |
| Canonical, no attenuation correction | 7.58 +/- 0.15 | Preferred Balmer virial mass for numerical comparison. |
| Balmer-decrement dust correction | 8.10 +/- 0.40 | Correlated alternative using SMC attenuation, Case B, and AV,BLR=1.9 +1.3/-1.2. Sensitivity/context only. |
| Spectrophotometric dust correction | 7.70 +/- 0.14 | Correlated alternative using AV approximately 0.53. Sensitivity/context only. |
| Upper systematic bound | <8.50 | One-sigma upper endpoint of the 8.10 +/- 0.40 dust alternative; not an independent censored likelihood. |
| Assumed-Eddington lower bound | >6.65 | Hbeta luminosity converted with unattenuated Case-B Halpha/Hbeta=2.86, Stern & Laor (2012) bolometric correction, and assumed fEdd=1. Context only. |

These are **five estimate/limit records for one object**, not five independent
measurements. The 6.65–8.50 envelope combines different assumptions and is not a
posterior or the error interval of 7.58. In particular, the 6.65 lower bound
cannot independently demonstrate a requirement for super-Eddington growth:
it assumes an Eddington luminosity relation and is not an independently measured
virial mass. No bound or envelope is sampled by this extraction.

## Lines, dust, dense gas, and missingness

Adopt the Table 1/III.2 intrinsic broad Hbeta FWHM **3521 +/- 502 km/s**, and
observed broad Hbeta flux **140 +/- 14.6** in units of **10^-20 erg/s/cm^2**.
The forward fit includes wavelength-dependent line-spread convolution, with the
nominal spectral resolving power increased by a factor 1.7 for a point source.
Do not correct the intrinsic FWHM for the instrument again. Hbeta is detected
at approximately S/N=10; the [O III] doublet at combined S/N approximately 4.2
anchors the adopted **spectroscopic z=9.288 +/- 0.003**. Hgamma is blended with
[O III]4363, with its widths fixed from the Hbeta fit; broad Hgamma S/N is
approximately 4.8. Broad Hgamma flux is 45.9 +/- 9.5 in the same units.

The Table 1 limits on narrow Hgamma (<7.1), narrow Hbeta (<62.7), and absorption
Hbeta flux (>-69.1) are **2-sigma limits**, per the table footnote. Preserve
negative absorption-flux signs and inequality directions. Absorption and narrow
Hbeta are individually statistically insignificant and degenerate; their
inclusion models covariance, not secure absorption evidence.

Two internal source discrepancies are retained explicitly:

- Absorption Hbeta FWHM is **282 +/- 159 km/s in Table 1**, but **413 +/- 255**
  in III.2. This auxiliary field is not used in the mass or eligibility decision.
- VI's first summary bullet gives broad Hbeta FWHM **3525 +/- 589 km/s**,
  while Table 1 and III.2 agree on **3521 +/- 502**. Adopt the detailed table
  and fitting passage, without averaging or replacing the published mass.

The broad-line Hbeta/Hgamma decrement is reported as 3.5 +1.7/-0.9; do not
replace it with the ratio of rounded central flux cells, since posterior ratios
and central-value ratios need not agree. Case B (intrinsic ratio 2.14) plus
an SMC law implies AV,BLR=1.9 +1.3/-1.2, but Case B may fail in dense,
collisionally excited gas. The source notes the dust estimates differ at about
1.3 sigma. The canonical mass receives neither correction.

The fiducial gas-enshrouded AGN model has log(nH/cm^-3)=9.9 +/- 0.2,
log(NH/cm^-2)>25.9 (one-sigma lower bound limited by the model grid), and
SMC AV=0.53 +0.09/-0.08. Cloudy is not designed for all processes in this
Compton-thick regime, so these fits are model context, not independent dynamical
masses. Appendix A changes the attenuation law: delta=-4.66 +0.31/-0.24,
AV=0.32 +0.05/-0.04, log(nH)=10.3 +/-0.3, and log(NH)=25.0 +0.3/-0.5.
It improves the MIRI residual but requires an implausibly steep attenuation law;
it does not create another object or adopted black-hole mass.

The host stellar-mass value is **log(Mstar/Msun)<9.0**, with possible further
AGN contamination of the UV. Store as an upper limit, leaving canonical
stellar mass and its errors missing. Do not interpret it as a detection at 9.0.
No canonical numeric Lbol, measured instantaneous Eddington ratio, or lensing
magnification is supplied by Table 1. Leave these missing; the lower-mass-limit
calculation's assumed fEdd=1 is not an observed Eddington ratio. No source
magnification correction is described for this ordinary PRIMER-COSMOS field.
The catalogue uses `lensing_status=not_reported`, blank mu, and
`lensing_mass_correction_status=not_required`, with this field-context rationale;
do not fabricate mu=1 or apply a demagnification.

## Canonical mapping and eligibility

The source is a single-target broad-Balmer virial study, satisfying the comparable
Balmer-family contract. Membership is **v2 and therefore v3**, with v1 unchanged.
This preserves the source calibration;
it does not recalibrate every family to a common recipe.

| Canonical field(s) | Adopted mapping |
| --- | --- |
| source_key / source_table | `taylor25_capers_lrd_z9` / Table 1 and IV.2 |
| object_id / published_aliases | CAPERS-LRD-z9 / CAPERS-COSMOS-119334 |
| ra_deg / dec_deg / redshift / redshift_err | Published Table 1 values; frame explicitly unreported; redshift_kind=`spec` |
| log_mbh_msun_std / log_mbh_err_minus / log_mbh_err_plus | 7.58 / 0.15 / 0.15 |
| mbh_method / mass_comparability_group | `single-epoch-virial-hbeta-greeneho2005` / `virial_balmer_single_epoch` |
| mbh_formal_uncertainty_kind | Reported line measurements plus empirical calibration-coefficient errors; not purely statistical |
| dust_correction_applied_flag | False |
| log_mbh_systematic_dex / mbh_systematic_applied_flag | Missing scalar / False; native 0.5–0.7 dex range retained separately |
| broad_line_species / fwhm_instrument_corrected_flag | Hbeta / True (intrinsic fitted width) |
| object_class / spectroscopic_type | `broad_line_agn` / `type1_broad_line` |
| evidence_status / basis | `secure`; broad Hbeta plus narrower forbidden lines and a measured systemic redshift |
| selection_channels / phenotype_tags | `photometric_sed;broad_hbeta` / `lrd;compact;red` |
| identity_resolution_status / preferred_measurement_flag | `resolved` / True |
| conditional_mass_flag | False for canonical source virial estimate; ordinary virial applicability caveats remain explicit |
| growth_ranking_eligible_flag | True for canonical mass only; method, redshift, identity and field lensing treatment supported |
| primary_mass_comparison_flag / primary_growth_ranking_flag | True under existing secure Balmer-method policy |
| manuscript membership | Primary and expanded under the publication-selection rules |

Source caveat tags: `prism_resolution`, `virial_calibration_high_redshift`,
`gas_enshrouded_lrd`, `dust_alternative_masses_correlated`,
`assumed_eddington_bound_context_only`, `source_auxiliary_width_discrepancy`,
`source_summary_width_discrepancy`, `host_mass_upper_limit`,
`coordinate_frame_unreported`. Any controlled tag naming should follow the final
registry. The alternate mass rows should enter source-local observables or a
sensitivity input, not increase preferred measurement/object cardinalities.

Source-family registry facts: JWST NIRCam LRD selection followed by
CAPERS/NIRSpec-PRISM confirmation; source-native Hbeta virial mass; one new
object; dataset minimum v2; DOI and exact v4 as above. The mass-method
registry entry preserves Greene & Ho equation 10 and the already included
coefficient uncertainties, with the separate high-z applicability range.
Selection was targeted follow-up of a high-value high-z LRD candidate; there
is no usable source inclusion probability or completeness weight. This source
supports object-level comparisons, not population fractions or seed-origin
probabilities.

Current growth rankings and v4 target selection are recorded in `results/`.
Treating a mass estimate as eligible does not validate its high-z virial assumptions.

## Retained files and independent checks

Raw files:

- `data/raw/capers_lrd_z9_v4_properties.csv`: one source-native target row.
- `data/raw/capers_lrd_z9_v4_mass_alternatives.csv`: five correlated estimate/limit records.
- `data/raw/capers_lrd_z9_v4_table_cells.csv`: every data row of all three tables.
- `data/raw/capers_lrd_z9_v4_screen.csv`: complete original/literature/control screen.

Supporting files under `data/validation/source_inputs/`:

- `capers_lrd_z9_v4_main.tex`: original archive member.
- `capers_lrd_z9_v4_extract.html`: source DOM extract of observations, analysis,
  results, discussion, summary and appendix; table/footnote/math content retained.
- `capers_lrd_z9_published_crossref.json`: publisher-deposited correspondence.
- `capers_lrd_z9_v4_figure6_legend.txt`: comparison-series legend transcribed
  from the archive figure with pypdf; no point digitization.

Independent fixtures and read-only check:

- `data/validation/capers_lrd_z9_source_manifest.json`: exact versions, retrieval
  date, archive/member hashes, supporting-payload hashes and row counts.
- `data/validation/capers_lrd_z9_expected_values.json`: independent TeX readings
  of mass/error, position/redshift, broad-line and dust values and all five
  mass semantics, plus source discrepancies.
- `data/validation/capers_lrd_z9_identity_checks.json`: both-version identity screen.
- `data/validation/capers_lrd_z9_validate.py`: source-only validation, run as
  `.venv/bin/python data/validation/capers_lrd_z9_validate.py`.

The check passes: retained payload hashes; 17 independently read numeric property
anchors; five mass values/error/limit definitions; 48 table-row cardinalities;
TeX anchors including both internal discrepancies; DOI correspondence; and the
recorded identity outcome. This source-only checker complements the independent
canonical mass/error and redshift/identity verifiers. The HTML scraper is a
transcription aid; expected mass values were independently read from TeX.

The explicitly unreported coordinate frame, auxiliary width conflicts, and
high-z virial/dust/gas model limitations remain source caveats. Shared registries,
processed products, manifests, and publication outputs include the adopted source.

## Reviewed canonical admission

Admitted 17 October 2026 at the unchanged 3 September 2026 cutoff.
Final measurement `CAPERSLRDz9_taylor25`, physical object `HZA-CAPERS-LRD-Z9`, host `HZS-CAPERS-LRD-Z9`.
Membership: **v2 and v3; primary and expanded numerical samples**. Adopted semantics: 7.58 +/- 0.15 dex; no dust correction or scalar added systematic.
Each family contributes one new physical object and one preferred measurement;
model alternatives do not add measurements or objects. The source-level screen
and exclusions above remain the scientific provenance for that decision.
The three older unresolved catalogue identity groups remain excluded from
manuscript inference. Canonical values are built by
`src/internal/october2026_additions.py`, with independent source-native fixtures
registered in the complete mass/error and redshift/coordinate checks.
