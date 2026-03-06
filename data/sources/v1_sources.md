# v1 Source Registry

## [source_key: juodzbalis25_jades_blagn]
- **Citation:** Juodzbalis et al. (2025), *JADES: comprehensive census of broad-line AGN from Reionization to Cosmic Noon revealed by JWST*, MNRAS, arXiv:2504.03551
- **ADS/arXiv:** https://arxiv.org/abs/2504.03551
- **Survey/Field:** JADES / GOODS-S and GOODS-N
- **Object selection used here:** Type 1 broad-line AGN sample from JADES spectroscopy, including "Robust", "Tentative", and "Tentative Hβ" subsets.
- **Values extracted:** object ID, RA, Dec, z, log MBH, log Lbol, lambda_Edd (Table 2) and host log M* (Table 5).
- **Extraction location:** `mnras_template.tex` table `\label{tab:all_objecs}` (AGN properties) and table `\label{tab:host_prop}` (host properties).
- **Method notes:**
  - MBH: single-epoch virial Balmer-line estimators (Hα for main sample; tentative Hβ subset handled as in paper workflow).
  - Lbol: Hα-based bolometric conversion (`L_bol = 130 L_Halpha`) following Stern calibration as stated in Section 4.
  - M*: host-constrained values from BEAGLE/CIGALE decomposition table; rows with dagger use CIGALE as best estimate per caption note.
  - AGN contamination: explicitly modeled in host analyses (spectroscopic and imaging decomposition), so `agn_contam_flag=1` for these rows.
- **Ingestion notes:**
  - Asymmetric uncertainties split into `_err_plus` and `_err_minus`.
  - `redshift_kind=spec` for all entries (NIRSpec spectroscopic sample).
  - `lensing_mu` and `lensing_mu_err` left blank because this paper does not provide per-object lensing magnification corrections for this JADES sample.
