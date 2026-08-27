# Source Registry

**1. [source_key: juodzbalis25_jades_blagn]**
- **Citation:** Juodžbalis et al. (2026), *JADES: comprehensive census of broad-line AGN from Reionization to Cosmic Noon revealed by JWST*, MNRAS 546, stag086, arXiv:2504.03551
- **ADS/arXiv:** https://arxiv.org/abs/2504.03551
- **Survey/Field:** JADES / GOODS-N + GOODS-S
- **Object selection used here:** Type 1 (broad-line) AGN from JADES spectroscopy
- **Values extracted:** z, MBH, Lbol, lambda_Edd, Mstar
- **Extraction location:** Table 2 (AGN properties: coordinates, z, MBH, Lbol, lambda_Edd), Table 5 (host properties: Mstar)
- **Method notes:** MBH from single-epoch virial estimators: Reines & Volonteri (2015) H-alpha for the main sample, with a source-stated 0.3 dex calibration uncertainty; Vestergaard & Peterson (2006) H-beta for the four high-redshift tentative candidates, for which this source does not state a numeric calibration systematic. Host Mstar follows the paper's adopted spectral-decomposition choice: BEAGLE by default, with CIGALE used when BEAGLE is unavailable or the host is significantly extended. This restores the paper-adopted CIGALE values for GS-200679, GS-20030333, and GS-164055 in the active v1 sample. The reviewed method mapping is maintained separately in `data/mass_method_registry.csv` and does not alter frozen catalogue values.
- **Detection evidence:** `GS-20057765`, `GS-20030333`, `GS-164055`, and `GN-4685` are the paper's tentative broad-H-beta emitters. Their individual broad-H-beta detections are not formally significant; the four-object stack supports the broad component. The catalogue records this as `stack_supported_tentative_hbeta` and does not treat these rows as individually confirmed detections.
- **Source consistency warning:** For GN-11836, Table 2 reports `log_mbh=6.06`, `log_lbol=44.11`, and `lambda_Edd=0.11`. The mass and luminosity imply `lambda_Edd` approximately 0.89, a -0.91 dex residual for the tabulated ratio. The catalogue preserves all three published values verbatim, flags the inconsistency structurally, and requires source clarification before choosing which value to revise.
- **Columns standardized beyond paper tables:** `redshift_kind=spec` (NIRSpec spectroscopy), method fields encode the paper methodology (`single-epoch-virial-halpha` or `single-epoch-virial-hbeta`, BEAGLE or CIGALE host decomposition, Balmer-line bolometric correction), `agn_contam_flag=1` for this Type-1 AGN sample, and `lensing_mu` left blank because no magnification correction is reported for these sources.
- **Ingestion notes:** Numeric values copied directly; asymmetric uncertainties split into *_err_plus and *_err_minus

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
- **Limitations:** The paper mentions 11 contaminated spectra without identifying the full set in Table 1, so no per-row contamination flags were inferred. See `docs/taylor24-ceers-rubies-extraction-notes.md` for object caveats.

## v4 Same-Class Broad-Line Additions

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
`docs/matthee23-eiger-fresco-extraction-notes.md` and
`docs/lin24-aspire-extraction-notes.md`.

## v5 Harikane Measurement Layer

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
  new. See `docs/harikane23-nirspec-extraction-notes.md`.

## v6 THRILS Same-Class Consolidation

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
  v6 objects. See `docs/davis26-thrils-extraction-notes.md`.

## v7 Heterogeneous Source Admission

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
  host-system ID and one integrated host mass. No v6 coordinate/redshift match
  is found. No LRD classification is published, so it remains missing.
- The validated source-admission layer is attached non-destructively to the
  catalogue-only v7 products. No v7 science ranking or figure exists yet. See
  `docs/ren25-alpine-cristal-jwst-extraction-notes.md` and
  `docs/v7-catalogue-schema.md`.

## v7.1 Luminous-Quasar Comparison Layer

- **[source_key: xqr30_mazzucchelli23] Mazzucchelli et al. (2023), A&A
  676 A71:** all 42 E-XQR-30 luminous quasars with MgII canonical masses and
  CIV alternate observables. The mass-table arXiv `2306.16474v1` archive hash
  is `412055cec92c368f711605822d806c949816695a451efee867904d2171fee53f`.
- Coordinates and canonical aliases come from the complete 42-row E-XQR-30
  table in D'Odorico et al. (2023), arXiv `2305.05053v1`, archive hash
  `1cf315f5fd4cd9f0edebb840c254dcd6bee26e2a061ce9fc9ff5bc8f344d7c42`.
- The 0.55 dex MgII scaling-relation systematic is separate from statistical
  fit errors. Seven telluric caveats, the PSO J065+01 CIV low-S/N caveat, BAL
  annotations, and uncorrected lensing for WISEA J0439+1634 are explicit.
- The paper's 23 earlier-literature repeats are audited separately; none has a
  coordinate/redshift candidate in v7.0. Four source-table Eddington-ratio
  inconsistencies are preserved and machine-flagged rather than overwritten.
  See `docs/xqr30-extraction-notes.md`.

## v7.2 GNIRS Luminous-Quasar Comparison Layer

- **[source_key: shen19_gnirs50] Shen et al. (2019), ApJ 873:35:** the
  complete 50-quasar Gemini/GNIRS sample from CDS `J/ApJ/873/35`.
- The source-fiducial mass uses MgII when available (29 rows), otherwise CIV
  (20 rows); J0055+0146 has no accepted virial mass and remains explicit but
  growth-ineligible. The source-stated 0.4 dex systematic is separate from
  Monte Carlo spectral-fit errors.
- Eight BAL and four radio-loud annotations are retained. Six measurements
  share physical identities with XQR-30; three threshold matches and three
  manual sub-arcsecond/name assertions are recorded in the reviewed registry.
- CDS Table 1 and Table 3 hashes are respectively
  `40ed1598d8c6d4d4a4aa580c578742f9e0334c26bb9dd762a9a0375231a7239f`
  and `e1eae3266b9ccfc966303c6e389e9c16141678199924a67ab4c786fed3240323`;
  arXiv `1809.05584v1` hashes to
  `2b4376dc136873c4b8db0e5016568b9b1d4692042f6bb035e61fa8bd76b980ef`.
  See `docs/shen19-gnirs50-extraction-notes.md`.
