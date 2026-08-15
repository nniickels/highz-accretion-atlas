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
