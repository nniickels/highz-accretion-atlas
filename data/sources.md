# Source Registry

## Machine-readable provenance supplement

`data/source_provenance_registry.csv` records one row per primary,
reanalysis, coordinate, or context source used by the current catalogue. Its
controlled `publication_status`, `evidence_status`, and `source_role` fields
separate publication maturity, scientific evidence strength, and actual use;
these concepts must not be inferred from one another. Paper DOIs and dataset
DOIs are separate fields. Exact source-archive hashes, extraction dates, the
2026-09-03 status-verification date, and scheduled preprint reviews are
machine checked by `python -m src.internal.verify_source_provenance`.

The supplement backfills the current exact Juodžbalis record as MNRAS 546,
stag086 / arXiv `2504.03551v2`, DOI `10.1093/mnras/stag086`, with source-archive
SHA-256
`0347b4942f1a3cb417d626bd5ba76ab0af25e59ab8013b3ed4ac0a61a04e0efd`.
This is deliberately not represented as the unknown historical v1 extraction:
the frozen rows retain `not_recorded_in_frozen_v1_source_layer`, and no frozen
catalogue value is changed. The registry also records the Shen catalogue DOI
`10.26093/cds/vizier.18730035` independently of the paper DOI.

As verified on 2026-09-03, Davis `2602.23310v1`, Hutchison `2512.12509v1`,
Zou `2603.24893v1`, and Skyfire `2609.00112v1` remain preprints in their official
arXiv records. The first three require another status review by 2026-11-27;
Skyfire is due by 2026-12-03. The Davis objects'
photometric-EELG parent selection remains context rather than evidence against
the later broad-line detections; the UHZ1 reanalysis retains `disputed`
evidence explicitly.

**1. [source_key: juodzbalis25_jades_blagn]**
- **Citation:** Juodžbalis et al. (2026), *JADES: comprehensive census of broad-line AGN from Reionization to Cosmic Noon revealed by JWST*, MNRAS 546, stag086, arXiv:2504.03551
- **Published record:** DOI https://doi.org/10.1093/mnras/stag086; arXiv https://arxiv.org/abs/2504.03551
- **Survey/Field:** JADES / GOODS-N + GOODS-S
- **Object selection used here:** Type 1 (broad-line) AGN from JADES spectroscopy
- **Values extracted:** z, MBH, Lbol, lambda_Edd, Mstar
- **Extraction location:** Table 2 (AGN properties: coordinates, z, MBH, Lbol, lambda_Edd), Table 5 (host properties: Mstar)
- **Method notes:** MBH from single-epoch virial estimators: Reines & Volonteri (2015) H-alpha for the main sample, with a source-stated 0.3 dex calibration uncertainty; Vestergaard & Peterson (2006) H-beta for the four high-redshift tentative candidates, for which this source does not state a numeric calibration systematic. Host Mstar follows the paper's adopted spectral-decomposition choice: BEAGLE by default, with CIGALE used when BEAGLE is unavailable or the host is significantly extended. This restores the paper-adopted CIGALE values for GS-200679, GS-20030333, and GS-164055 in the active v1 sample. The reviewed method mapping is maintained separately in `data/mass_method_registry.csv` and does not alter frozen catalogue values.
- **Detection evidence:** `GS-20057765`, `GS-20030333`, `GS-164055`, and `GN-4685` are the paper's tentative broad-H-beta emitters. Their individual broad-H-beta detections are not formally significant; the four-object stack supports the broad component. The catalogue records this as `stack_supported_tentative_hbeta` and does not treat these rows as individually confirmed detections.
- **Source consistency warning:** For GN-11836, Table 2 reports `log_mbh=6.06`, `log_lbol=44.11`, and `lambda_Edd=0.11`. The mass and luminosity imply `lambda_Edd` approximately 0.89, a -0.91 dex residual for the tabulated ratio. The catalogue preserves all three published values verbatim, flags the inconsistency structurally, and requires source clarification before choosing which value to revise.
- **Columns standardized beyond paper tables:** `redshift_kind=spec` (NIRSpec spectroscopy), method fields encode the paper methodology (`single-epoch-virial-halpha` or `single-epoch-virial-hbeta`, BEAGLE or CIGALE host decomposition, Balmer-line bolometric correction), `agn_contam_flag=1` for this Type-1 AGN sample, and `lensing_mu` left blank because no magnification correction is reported for these sources.
- **Ingestion notes:** Numeric values copied directly; asymmetric uncertainties split into *_err_plus and *_err_minus
- **Frozen-v1 provenance limitation:** the current catalogue retains
  `extraction_date=not_recorded_in_frozen_v1_source_layer` and has no archived
  source checksum for these 23 rows. The DOI and source URL are documented
  here, but the missing historical extraction date/checksum must not be
  represented as complete row-level provenance.

**2. [source_key: taylor24_ceers_rubies_blagn]**
- **Citation:** Taylor et al. (2025), *Broad-Line AGNs at 3.5<z<6: The Black Hole Mass Function and a Connection with Little Red Dots*, The Astrophysical Journal 986, 165
- **Primary version:** Published 2025-06-20; https://iopscience.iop.org/article/10.3847/1538-4357/add15b; DOI https://doi.org/10.3847/1538-4357/add15b. The corresponding latest arXiv source is v2, revised 2025-05-14: https://arxiv.org/abs/2409.06772v2.
- **Survey/Field:** CEERS and RUBIES / EGS and UDS
- **Object selection used here:** Source-selected broad-Halpha AGN; FWHM >700 km/s, broad-flux S/N >4, Delta BIC >6, secure multi-line spectroscopic redshift, and visual QA. Raw storage includes all Table 1 rows; processing applies `z >= 4`.
- **Values extracted:** coordinates, spectroscopic redshift, total/narrow/broad Halpha fluxes and asymmetric errors, instrument-corrected broad FWHM and errors, virial MBH and formal errors, LRD marker, and Halpha absorption-fit marker
- **Extraction location:** Table 1 and its notes in the v2 TeX source; sample selection and caveats from the surrounding manuscript text
- **Mass method:** Reines et al. (2013) Halpha single-epoch virial calibration, tagged `single-epoch-virial-halpha-reines2013`. The approximate 0.5 dex virial-calibration systematic is separate from the formal posterior errors and is not applied to the nominal mass.
- **Identity decision:** `CEERS-2782` and `RUBIES-EGS-50052` are linked to one physical object while retaining both measurements. The RUBIES measurement is preferred in the object view.
- **Phenotype:** `lrd` is an independent source-adopted phenotype; all rows retain `object_class=broad-line-agn`.
- **Missingness:** Mstar, Lbol, and Eddington ratio are not published in Table 1 and remain blank rather than being inferred.
- **Verified anchors:** 63 measurements / 62 physical objects in Table 1; 37 / 36 at `z >= 4`; 21 LRD rows full / 17 filtered; 4 absorption-fit rows full / 3 filtered.
- **Extraction archive:** https://arxiv.org/e-print/2409.06772v2; SHA-256 `50453a0a975b84f019ceba8da30663e40d83c285376cad119d83fa8e3b31aaa0`; extracted 2026-08-17
- **Limitations:** The paper mentions 11 contaminated spectra without identifying the full set in Table 1, so no per-row contamination flags were inferred. See `docs/source-notes/taylor24-ceers-rubies-extraction-notes.md` for object caveats.

## v2 sources: Matthee and Lin

- **[source_key: matthee23_eiger_fresco_blagn] Matthee et al. (2024),
  EIGER/FRESCO:** 20 broad-Halpha emitters at
  `4.163 <= z <= 5.538`, extracted from Tables 1--3 of arXiv `2306.05448v3` /
  ApJ 963:129. Raw values: `data/raw/matthee23_eiger_fresco_blagn_tables1_3.csv`.
  Selection requires broad-Halpha S/N > 5, luminosity > 2e42 erg/s, and FWHM
  > 1000 km/s, followed by visual rejection of spatial broadening.
  The 0.5 dex Reines-calibration uncertainty is separate from formal errors.
  The source archive SHA-256 is
  `b3e6f5385e694d92a7456f81eb123a305468baf743cebc7aeea820befb9b1190`.
  GOODS-S-13971 is crossmatched to the existing JADES GS-204851 object. The
  LRD flag is a paper-level sample label, not a row marker in Tables 1--3.
- **[source_key: lin24_aspire_blagn] Lin et al. (2024), ASPIRE:** 16 compact
  broad-Halpha emitters at
  `4.0639 <= z <= 5.0369`, extracted from Tables 1--3 of arXiv `2407.17570v1` /
  ApJ 974:147. Raw values: `data/raw/lin24_aspire_blagn_tables1_3.csv`.
  Selection uses compact-red preselection, then integrated line S/N > 5 and
  broad FWHM > 1000 km/s. The source archive SHA-256 is
  `fc1c4d96e4a568b09b3caefa0fdde1c7fabe8decad71fb6423ff37c912b024cd`.
  All 16 are explicitly called LRDs in Table 1; LRD remains a phenotype, not
  the object class.

Detailed extraction and caveat notes are in
`docs/source-notes/matthee23-eiger-fresco-extraction-notes.md` and
`docs/source-notes/lin24-aspire-extraction-notes.md`.

## v2 source: Harikane

- **[source_key: harikane23_nirspec_blagn] Harikane et al. (2023), ApJ
  959:39:** ten Type 1 broad-Halpha AGN at `z=4.015--6.936`, extracted from
  Tables 1--3 of arXiv `2303.11946v3`; DOI
  `10.3847/1538-4357/ad029e`. The source archive SHA-256 is
  `02c2951b4594234f8cc015fc811f1ed438d35997249138af4d756d02d44ca4b4`.
  Selection requires broad-Halpha FWHM greater than 1000 km/s and S/N greater
  than 5, narrow forbidden lines, and rejection of outflow-only explanations;
  all final rows have Delta AIC greater than 20. MBH uses the Greene & Ho
  (2005) Halpha estimator and extinction-corrected broad-Halpha luminosity.
  The source gives no numeric virial systematic, so none is inferred. Six host
  masses and four upper limits are preserved distinctly. The paper's typical
  `0.2 dex` host-mass systematic from its fixed SED-fitting prior is recorded
  separately and not applied. No row-level LRD marker is published;
  red/compact descriptions remain separate phenotypes.
  Five measurements crossmatch existing CEERS physical objects and five are
  new. See `docs/source-notes/harikane23-nirspec-extraction-notes.md`.

## v2 source: Davis/THRILS

- **[source_key: davis26_thrils_blagn] Davis et al. (2026), submitted to
  ApJ:** seven deep-G395M broad-Halpha measurements at `z=3.52--6.57`,
  extracted from Appendix Table 5 of arXiv `2602.23310v1`. Six pass the project
  `z >= 4` cut. Selection requires a broad component above 3 sigma and implied
  FWHM above 1000 km/s. MBH uses the Reines & Volonteri (2015) Halpha
  single-epoch calibration; the approximately `0.5 dex` recipe scatter is
  stored separately from formal posterior errors. Table 5 does not publish
  row-level LRD, Mstar, Lbol, or Eddington-ratio values, so none is inferred.
  Coordinates are exact THRILS-ID joins from Hutchison et al. programme Table 3,
  arXiv `2512.12509v1`, with independent provenance. The Davis and Hutchison
  source-archive SHA-256 values are respectively
  `13274268d718138119dbbb818d58e3f5255ce0a34f80f9d8a7a0d0013f16153b`
  and `584a56f5867e816c6220ea52f55fc0411f2fc745544ecccfb6ea4ad42c445fdc`.
  The only known Taylor repeat is below `z=4`; all six retained rows are new
  v2 objects. See `docs/source-notes/davis26-thrils-extraction-notes.md`.

## v2 source: Ren ALPINE--CRISTAL

- **[source_key: ren25_alpine_cristal_jwst_blagn_candidates] Ren et al.
  (2025), MNRAS 544, 211--233:** seven Type-1 AGN candidate nuclei in six
  ALPINE--CRISTAL--JWST host systems, extracted from the published Tables 1--2.
  The latest primary record used is the corrected/typeset MNRAS article, DOI
  `10.1093/mnras/staf1709`, corresponding to arXiv `2509.02027v2`; the source
  archive SHA-256 is
  `c528c375fda9362433184cb35775a5f4ca107014f4b1c2f6536d7f15d4f85cca`.
- Table 1 raw storage preserves all seven rows; all are already at `z>5`.
  Table 2 raw storage preserves 70 line entries: 58 detections and twelve
  3-sigma upper limits. No figure values or unreported per-row Delta-BIC values
  are reconstructed.
- MBH uses `single-epoch-virial-halpha-reines2013`; the paper's `0.4 dex`
  systematic remains separate from formal Table 1 errors. `DC_536534` maps to
  probable evidence and primary eligibility. The other six are candidate,
  BLR-conditional masses retained only in the exploratory diagnostic tier.
- `DC_848185_a` and `DC_848185_b` are separate candidate nuclei sharing one
  host-system ID and one integrated host mass. No earlier-source coordinate/redshift match
  is found. No LRD classification is published, so it remains missing.
- The validated source-admission layer is attached non-destructively to the
  canonical v2 and v3 products; its eligible probable row participates in the
  shared science and figures. See
  `docs/source-notes/ren25-alpine-cristal-jwst-extraction-notes.md` and
  `docs/current/v3-catalogue-schema.md`.

## v2 canonical-mass additions reviewed 2026-09-03

- **[source_key: greene24_uncover_blagn] Greene et al. (2024), UNCOVER:** nine
  unique, JWST/NIRSpec-confirmed broad-Balmer AGN with published virial masses
  are admitted from Tables 1 and 3. One A2744-QSO1 image represents the multiply
  imaged physical source. Published lensing magnifications and demagnified
  masses are retained.
- **[source_key: kocevski25_lrd_blagn] Kocevski et al. (2025), RUBIES:** six
  unique `z >= 4` JWST broad-line LRDs with numerical dust-corrected virial
  masses are admitted after coordinate/redshift overlap removal against the
  existing Taylor ingestion.
- **[source_key: skyfire26_ceers_blagn] Skyfire (2026), CEERS:** 22 unique
  `z >= 4` JWST/NIRSpec broad-Halpha objects with numerical masses are admitted
  from Table 3. The v1 preprint status and scheduled review remain explicit.
- **[source_key: larson23_ceers1019] Larson et al. (2023):** CEERS 1019 is
  admitted from its JWST/NIRSpec broad-Hbeta identification and published
  single-epoch mass.
- **[source_key: killi24_j0647_lrd_blagn] Killi et al. (2024):** the lensed
  J0647-1045 LRD is admitted from its JWST/NIRSpec broad-Halpha identification
  and published, magnification-corrected virial mass.
- **[source_key: ubler24_zs7_offset_blagn] Uebler et al. (2024):** the
  spatially offset broad-Hbeta Type-1 nucleus in the ZS7 merging system is
  admitted with its published canonical virial mass.

These additions contribute 40 unique physical objects to v2 and flow into v3.
The Jones et al. compilation contributes no further unique object after this
identity audit, so it is not duplicated as new catalogue membership; it remains
a future alternate-measurement/reanalysis source.

## v3 source: GN-z11 high-ionization-line candidate

- **[source_key: maiolino24_gnz11_agn] Maiolino et al. (2024):** GN-z11 is a
  JWST/NIRSpec-identified accretion candidate based on dense high-ionization and
  broad permitted-line evidence. Its published UV single-epoch mass is retained
  as a numerical secondary stratum, not folded into the primary Balmer-virial
  comparison. This heterogeneous evidence type is v3-only.

## v3 source: UHZ1 X-ray evidence history

- **[source_key: uhz1_xray_evidence_history] UHZ1 / UNCOVER-26185:** two
  measurement versions preserve the original Bogdán et al. (2024) X-ray AGN
  interpretation and the Zou et al. (2026) full-data reanalysis as one physical
  object. Their source-archive SHA-256 values are
  `d1446d873c81c0ee83f7cc1c0648d85f8a93b0967eb5d14ef7b46d0564ab2e6c`
  and `2690ce8d6345a097ebc642232205d0337eabe76f582c661db815bff4912f77d4`.
  The companion Goulding et al. (2023) spectroscopy paper (ApJL 955 L24, DOI
  `10.3847/2041-8213/acf7c5`, arXiv `2308.02750v3`) archive hashes to
  `73628a4c4632871e6b3888b61f2e6cedf28ead1d1af7f45a20cac20f8988b729`.
- The original 4.2--4.4 sigma claim is `candidate`; the current 2.3--2.9 sigma,
  nonpersistent reanalysis is preferred and `disputed`. The nine MIRI upper
  limits and bolometric limit are censored observables.
- The published `10^7--10^8 Msun` Eddington-assumed range is not converted to a
  canonical point mass. Both rows remain growth-ineligible. See
  `docs/source-notes/uhz1-xray-evidence-history-extraction-notes.md` and
  `docs/current/v3-catalogue-schema.md`.

## v3 source: Scholtz JADES narrow-line candidates

- **[source_key: scholtz25_jades_narrow_line_agn] Scholtz et al. (2025),
  A&A 697, A175:** all 20 entries at `z >= 4` from the paper's 41-row source
  table. The prose reports 42 candidates; that unresolved discrepancy is
  retained as provenance rather than filled by inference.
- Three S2-VO87 rows retain the paper's tentative asterisk and seven detected
  Ne IV, Ne V, or N V fluxes are stored as observables. JADES DR3 supplies
  target coordinates.
- JADES 8083 is linked to the existing broad-line physical object; the earlier
  numeric-mass measurement remains preferred. No new row has a numeric BH
  mass or enters growth ranking. See
  `docs/source-notes/scholtz25-jades-narrow-line-extraction-notes.md` and
  `docs/current/v3-catalogue-schema.md`.

## v3 Scholtz provenance correction

- The complete 41-row source-native TeX table proves that 21, not 20, rows meet
  `z >= 4`. v3 includes the previously omitted
  `JADES-NS-GS00099671` measurement with no inferred black-hole mass.
- The source family therefore has 21 admitted measurements and 21 source
  physical IDs. One row, JADES 8083, is linked to an existing broad-line object,
  so the combined v3 object-class view contains 20 narrow-line candidate
  objects contributed by this family.
- The current dataset counts and evidence aggregation are documented in
  `docs/current/v3-catalogue-schema.md` and `docs/current/v3-notes.md`.
