# Source Registry

**1. [source_key: juodzbalis25_jades_blagn]**
- **Citation:** Juodžbalis et al. (2025), *JADES: comprehensive census of broad-line AGN from Reionization to Cosmic Noon revealed by JWST*, MNRAS, arXiv:2504.03551
- **ADS/arXiv:** https://arxiv.org/abs/2504.03551
- **Survey/Field:** JADES / GOODS-N + GOODS-S
- **Object selection used here:** Type 1 (broad-line) AGN from JADES spectroscopy
- **Values extracted:** z, MBH, Lbol, lambda_Edd, Mstar
- **Extraction location:** Table 2 (AGN properties: coordinates, z, MBH, Lbol, lambda_Edd), Table 5 (host properties: Mstar)
- **Method notes:** MBH from single-epoch virial estimators (Balmer-line based); host Mstar from spectral decomposition (BEAGLE/CIGALE in paper; BEAGLE used in the sample rows above).
- **Columns standardized beyond paper tables:** `redshift_kind=spec` (NIRSpec spectroscopy), method fields encode the paper methodology (`single-epoch-virial-halpha`, BEAGLE-based host masses, Balmer-line bolometric correction), `agn_contam_flag=1` for this Type-1 AGN sample, and `lensing_mu` left blank because no magnification correction is reported for these sources.
- **Ingestion notes:** Numeric values copied directly; asymmetric uncertainties split into *_err_plus and *_err_minus
