# Source Registry

**1. [source_key: juodzbalis25_jades_blagn]**
- **Citation:** Juodžbalis et al. (2026), *JADES: comprehensive census of broad-line AGN from Reionization to Cosmic Noon revealed by JWST*, MNRAS 546, stag086, arXiv:2504.03551
- **ADS/arXiv:** https://arxiv.org/abs/2504.03551
- **Survey/Field:** JADES / GOODS-N + GOODS-S
- **Object selection used here:** Type 1 (broad-line) AGN from JADES spectroscopy
- **Values extracted:** z, MBH, Lbol, lambda_Edd, Mstar
- **Extraction location:** Table 2 (AGN properties: coordinates, z, MBH, Lbol, lambda_Edd), Table 5 (host properties: Mstar)
- **Method notes:** MBH from single-epoch virial estimators (H-alpha for the main sample; H-beta for the four high-redshift tentative candidates). Host Mstar follows the paper's adopted spectral-decomposition choice: BEAGLE by default, with CIGALE used when BEAGLE is unavailable or the host is significantly extended. This restores the paper-adopted CIGALE values for GS-200679, GS-20030333, and GS-164055 in the active v1 sample.
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
