# v1 Source Registry

Use one block per paper/source and keep `source_key` aligned with `data/raw/v1_raw.csv` and `data/processed/v1_processed.csv`.

## [source_key: example24]
- **Citation:** Example et al. (2024), Journal, DOI/arXiv
- **ADS/arXiv:** https://arxiv.org/abs/xxxx.xxxxx
- **Survey/Field:** JADES / GOODS-N
- **Object selection used here:** Broad-line AGN candidates at z >= 4
- **Values extracted:** z, MBH, M*, Lbol
- **Extraction location:** Table 2 (z, MBH), Table 3 (M*), Figure 5 (Lbol)
- **Method notes:** MBH from single-epoch virial calibration; M* from AGN+stellar SED fits.
- **Ingestion notes:** Source values entered directly into raw; uncertainties kept asymmetric where available.
