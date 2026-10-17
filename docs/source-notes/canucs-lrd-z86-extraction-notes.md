# CANUCS-LRD-z8.6 source extraction

Reviewed/retrieved 17 October 2026 against the literature cutoff 3 September 2026.
These are source provenance and admission proposals; canonical products have not
been regenerated. The authorized expansion adds to v2 and v3, leaving v1 unchanged.
The comparison revision is `fc0c5501ad2271865b1c040307cad8dd8ca5721a`.

## Measurement version and retained sources

Adopt Tripodi et al., *Extreme properties of a compact and massive accreting black
hole host in the first 500 Myr*, Nature Communications 16, 9830 (19 November
2025), DOI [10.1038/s41467-025-65070-x](https://doi.org/10.1038/s41467-025-65070-x).
Use the published abstract, Methods, and Supplementary Tables 1–5 together.
The earlier [arXiv:2412.04983v1](https://arxiv.org/abs/2412.04983v1), dated
6 December 2024, is a comparison source only. The arXiv record lists one version;
publication metadata is not permission to relabel that preprint as the publication.

For overlap/evidence use [Morishita arXiv:2508.01372v2](https://arxiv.org/abs/2508.01372v2),
15 January 2026, accepted for ApJ, available before the cutoff. The revised
record is important: v1 section III.2 independently applied an Hbeta relation
and reported `6.2(-4.3,+8.4) x 10^7 Msun`. In v2 that calculation/equation is
removed; section III.2 cites Tripodi's `1.0(-0.4,+0.6) x 10^8 Msun` instead.
Do not admit the obsolete v1 mass as a second current measurement. V2 adds new
G140H Lyman-alpha observations and independently remeasures the PRISM spectrum;
it is neither a new object nor wholly literature-reused spectroscopy.

`data/validation/canucs_source_payloads.json` gives exact URLs, retrieval date,
and SHA-256 for each retained extract. The supplementary extract additionally
records the downloaded original PDF hash. Published supplement PDF pages 7–8
(printed 50–51) were rendered and visually inspected, including column headings,
asymmetric errors and magnification footnotes; all five tables were read. The
retained text contains complete tables 1–5 (PDF pages 7–10). Temporary HTML,
PDFs and rendered pages were kept outside the repository.

## Complete source screen

The published study has **one science target**, source 5112687. No table contains
a second newly measured accreting object. Enumerating table rows is distinct
from enumerating galaxies:

| Source material / rows screened | Outcome |
| --- | --- |
| CANUCS-LRD-z8.6 / 5112687 | Propose one new object, host and preferred Hbeta mass |
| Foreground 5112688, 0.54 arcsec away, zphot=0.49(-0.07,+0.05) | Exclude: low-redshift foreground galaxy used for lensing, not a second high-z AGN |
| Supplementary Table 1: [OIII]5008, Hbeta narrow, Hbeta broad, [OIII]4364, Hgamma narrow, Hgamma broad, Hdelta, [NeIII]3869, [OII]3727, CIV, NIV]1483/1486; each Fiducial/Test 1/Test 2 column | All 11 line rows and three model columns belong to 5112687. Hgamma broad absent in Fiducial; UV lines not separately refit in Tests 1/2. [OII] is a 3-sigma upper limit. No additional object or mass |
| Supplementary Table 2: E(B-V), nebular AV, six logarithmic line ratios; Fiducial/Test 1/Test 2 | Same object's dust/diagnostic modeling; no new object |
| Supplementary Table 3: Hbeta mass, 5100 A mass, Eddington luminosity, bolometric luminosity, Eddington ratio; three fit cases | Prefer Fiducial Hbeta; retain all fits as modeling observables, not six independent BH measurements |
| Supplementary Table 4: 12 parameter rows, with/without AGN SED fits | Same host and model priors; no extra BH masses or objects |
| Supplementary Table 5: C24-Pop III.1, C24-ALS, Sch23-EL, Sch23-SE, S23-M1e-6, S23-M1e-3, Z22-S1, Z22-S5-ref, Z22-S5-FB1, Z22-S5-FB2, B23-FABLE, B23-ref, Bh22a, Bh22b, Bh22c, Bh22d, Bh22e, Ni22, L24-HMAD, L24-MAD | All 20 rows are theoretical models, not observed catalogue members |
| Morishita v2 Table 1: G140H and PRISM line measurements | One target, same ID 5112687; new evidence only |
| Morishita environment photometric candidates in Fig. 7 / section IV.1 | Neighbouring Lyman-break galaxies without source-assigned AGN evidence or masses; not catalogue candidates merely because they may ionize the bubble. No individual object table is supplied |
| Main/supplementary figures' literature comparison samples | Context only, not newly extracted source rows. Includes GN-z11, UNCOVER-20466, ZS7, COS-66964, J1007-AGN, 04590, RXCJ2248-ID, GHZ2, GS-9209, RUBIES-UDS-QG-z7 and ground-selected QSOs such as J0100+2802. Refer to their own source families; do not readmit figure points |

## Identity review

The published identity is `5112687`, `CANUCS-LRD-z8.6`, RA `11:49:33.82`,
Dec `+22:20:59.16` = (177.39091666666667, 22.34976666666667) degrees.
An explicit coordinate frame/equinox is not stated; do not invent an ICRS claim.
The imaging reduction is tied to the HST/ACS reference frame. Retain the
sexagesimal precision. Proposed physical ID `HZA-CANUCS-LRD-Z8-6`, host ID
`HZS-CANUCS-LRD-Z8-6`, measurement ID `CANUCS5112687_tripodi25`.

Scanned all 218 v2 and 350 v3 measurement rows by great-circle separation,
without a redshift prefilter. Zero positioned measurements lie within 2 arcsec;
the nearest is J112014389_matthee23 at 61837.34 arcsec, z=4.897. No current
measurement row contains 5112687, CANUCS-LRD or Tripodi. Proposed new alias is
not an existing object alias. Both versions' object/alias tables were also
searched for these strings. The source survey's appearance in another paper
is not object admission.

The 27 v3 missing-coordinate rows are enumerated in
`data/validation/canucs_identity_screen.json`: GHZ2 (z=12.34), MoM-BH*-1
(z=7.7569), and 25 CEERS/Mazzolari rows. CEERS-1029 at z=8.61 deserves mention
because of its similar redshift, but its CEERS field and source identity differ
from this MACS1149 target. These are not positive crossmatches; absent sky
positions limit a global identity-completeness claim. Morishita explicitly
identifies its target as CANUCS 5112687, so its new z=8.6329±0.0005 does not
create another physical object. Do not replace Tripodi's z=8.6319±0.0005 with
that re-reduction's redshift in the preferred measurement.

## Canonical field mapping and uncertainties

`data/raw/tripodi25_canucs_lrd_z86.csv` retains reported values and labels.
`data/validation/canucs_adapter_check.py` is a focused deterministic conversion
and independent-anchor check, not a registration in the shared pipeline.
Map redshift to spectroscopic, species Hbeta, class `broad_line_agn`,
spectroscopic type `type1_broad_line`, phenotype `lrd;compact`, comparability
`virial_balmer_single_epoch`, method `single-epoch-virial-hbeta`.

Prefer the published headline linear mass `1.0(+0.6,-0.4) x 10^8 Msun`.
Central log mass is 8.0; endpoint conversion gives +0.204119982655925 and
-0.221848749616356 dex. Table 3 separately reports 8.0±0.2 dex, a rounded
summary, not another measurement. Do not log the error bars themselves.
Reported uncertainties follow median/16th/84th percentiles unless otherwise
stated; upper/lower limits are 3 sigma. The headline and table rounding do not
justify claiming exact equivalence of their posterior endpoints.

The exact Fiducial Hbeta FWHM is 4190(+570,-540) km/s in Table 1; the main
text rounds to 4200(+600,-500). Use the exact table values. Fiducial Hbeta broad
flux is 29.8±4.7 in 10^-19 erg/s/cm^2. No instrumental deconvolution flag is
asserted from this table alone. Hbeta broad S/N is reported as 6. Narrow [OIII]
lacks a broad counterpart, and NIV]/CIV support the AGN interpretation.

The paper cites Greene & Ho (2005), using line luminosity and Hbeta width,
and separately 5100 A continuum and the same broad width. Its printed equation
and coefficients are retained verbatim in the source extract, including their
normalizations; do not silently repair/recompute the published mass from them.
Alternative relations (reference 138) raise masses by 0.15–0.2 dex and are a
method sensitivity, not additional independent masses. General single-epoch
uncertainty is stated as 0.3–0.5 dex. Inclusion of that calibration scatter in
Table 3's ±0.2 is not explicitly established; retain reported uncertainty and
mark statistical/calibration decomposition unspecified. Do not add the scatter
range to canonical errors or choose an arbitrary scalar systematic.

Table 3 gives log Lbol=45.0±0.8 (erg/s), from 3000 A continuum and the cited
bolometric correction; Eddington ratio 0.1 has factor-two uncertainty. Preserve
that multiplicative convention rather than fabricate a Gaussian error. These
are derived from the same observables and are not independent mass constraints.
The preferred published host mass is 4.5(+1.1,-2.9) x 10^9 Msun; those errors
include SED/dust-model variation. Table 4's AGN-fit log Mstar=9.65±0.08 is the
single-model fit, not a replacement for the adopted host envelope.

## Lensing and dust, field by field

| Field | Published correction state / integration rule |
| --- | --- |
| Redshift, coordinates, line FWHM | No flux-magnification division |
| Table 1 line fluxes, including broad Hbeta and limits | Explicitly observed/magnified, not lens-corrected. Retain as reported. If deriving an intrinsic flux, divide this field once by 1.07 and label it derived |
| Table 3 Hbeta/5100 masses, LEdd and Lbol | Explicitly corrected for μ=1.07. Never divide the published mass again, whether by μ or a luminosity exponent |
| Table 2 dust-corrected line ratios | Source reports magnification correction; common μ cancels in ratios. Already corrected for nebular reddening |
| Table 4 stellar masses / adopted main-text host mass | Corrected in publication. Preserve reported values |
| Physical size upper limit <70 pc | Forward lens modeling uses conservative cluster μ=1.056; keep this method-specific limit rather than rescale it by 1.07 |

Adopted μ=1.07(-0.01,+0.08) combines lens-model alternatives, not a symmetric
measurement. Keep both errors; avoid averaging into an artificial Gaussian.
Main-text broad statements about corrected physical quantities do not override
Table 1's explicit flux footnote. Nebular Calzetti correction is for diagnostic
ratios; fiducial E(B-V)=-0.4±0.5 is retained, not clamped or applied to the BH
mass by this extraction. The exact dust treatment of the mass-input luminosity
is not explicitly stated, so keep its state unspecified and do not add a dust
correction. SED stellar attenuation is a separate modeled quantity.

Morishita v2 uses μ=1.85±0.02 (Schuldt model), unlike Tripodi. Its Table 1 gives spectral fluxes without an explicit lens-correction footnote;
no intrinsic flux or new mass is adopted here. Its Table 1 limits are 1 sigma
(the fitting prose discusses 3 sigma), so preserve that discrepancy if these
limits are later ingested. It newly measures Hbeta broad
3554.9±480.4 km/s (rounded 3600±500), and observed Lyalpha
1536.03±256.00 km/s, with inferred intrinsic Lyalpha 2173.49±276.63 km/s.
Keep that re-reduction and its lensing model in its own evidence provenance;
do not splice it into Tripodi's preferred mass or apply its μ to that mass.

## Publication differences and eligibility

Tripodi preprint and publication retain the same central z, headline mass,
Fiducial Hbeta flux/width, Hbeta table mass, 5100 table mass, and μ=1.07.
Published Table 3 additionally tabulates Test 1/2 mass variants. Host SED results
change substantially: preprint Table 4 has uncorrected single-model log Mstar
9.58(-0.04,+0.03) without AGN and 9.88±0.08 with AGN; publication has explicitly
corrected 9.27±0.05 and 9.65±0.08. This is more than the small μ correction.
Preprint AGN F5100=(7.1±0.3)x10^-21 and sigma=1139(-82,+133) change to
(2.0±0.4)x10^-21 and 2860(-624,+804) in the published SED table. These SED
broadening parameters are not the directly fitted Table 1 Hbeta width.
The preprint's 12+log(O/H)=7.08(-0.12,+0.14) direct estimate is superseded by
published direct-method limits (<7.9 fiducial, <6.9 Tests 1/2) and expanded
strong-line/ionization discussion. Do not import preprint metallicity or host
fits into the published measurement. The complete retained tables allow review
of other ancillary fit-parameter changes without claiming they are canonical.

Propose source-family membership **v2 and therefore v3**: this is a JWST-selected
Balmer single-epoch virial family, not a heterogeneous family made comparable
by selectively choosing a Balmer row. Propose `secure` evidence as the source's
broad-line AGN identification, with resolved identity and source-corrected
lensing. Numerical growth, method-primary, and manuscript-primary/expanded
eligibility are proposed true, subject to integration checks. The BLR/virial
interpretation and its high-redshift calibration remain assumptions; no
source-specific disputed/conditional status is claimed. If integration adopts
a stricter conditional BLR assessment, retain membership but explicitly exclude
it from primary inference under that policy. Presence in v2 alone does not
set manuscript eligibility.

Preferred measurement is the only admitted numerical record for this new object;
retain 5100 and Hgamma model alternatives as observables/sensitivities. No new
numerical growth ranks or sample counts are claimed here. No source-specific
blocker remains; registration, shared adapter wiring, manifests, publication
selection and regeneration belong to integration.

## Produced files and checks

- `data/raw/tripodi25_canucs_lrd_z86.csv`: one proposed measurement.
- `data/raw/tripodi25_canucs_agn_fit_variants.csv`: three same-object model cases.
- `data/raw/tripodi25_canucs_fiducial_lines.csv`: all 11 Fiducial line rows.
- Five `data/validation/source_inputs/canucs_*` scientific text / supplement table
  extracts, listed with their exact paths and hashes in `canucs_source_payloads.json`.
- `data/validation/canucs_expected_values.json`: source-read independent anchors.
- `data/validation/canucs_identity_screen.json`: both-version position screen,
  nearest records and complete missing-coordinate list.
- `data/validation/canucs_adapter_check.py`: conversion/hash/anchor validation.
- This source note.

Run `.venv/bin/python data/validation/canucs_adapter_check.py`. This verifies
source anchors, asymmetric mass endpoint conversion and every retained payload
hash. It does not test unmodified shared assembly or establish virial physics.

## Reviewed canonical admission

Admitted 17 October 2026 at the unchanged 3 September 2026 cutoff.
Final measurement `CANUCS5112687_tripodi25`, physical object `HZA-CANUCS-LRD-Z8-6`, host `HZS-CANUCS-LRD-Z8-6`.
Membership: **v2 and v3; primary and expanded numerical samples**. Adopted semantics: published linear mass endpoints converted to dex; no second lens correction.
Each family contributes one new physical object and one preferred measurement;
model alternatives do not add measurements or objects. The source-level screen
and exclusions above remain the scientific provenance for that decision.
The three older unresolved catalogue identity groups remain excluded from
manuscript inference. Canonical values are built by
`src/internal/october2026_additions.py`, with independent source-native fixtures
registered in the complete mass/error and redshift/coordinate checks.
Morishita v2 is registered as context under the CANUCS family; it contributes
zero additional objects or mass measurements. The publisher article number is
9830 (DOI landing page), correcting the earlier extraction metadata label.
