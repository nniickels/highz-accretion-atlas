# v2 Candidate Black-Hole Object Papers

This is a working source list for expanding the atlas beyond the v1 JADES
broad-line AGN sample. Priority is given to papers with object-level redshift,
black-hole mass, bolometric luminosity or Eddington ratio, and host stellar mass
where available.

## Highest-priority ingestion set

These are the best candidates for v2 rows because they contain direct or
relatively direct object-level quantities that map onto the current catalogue
schema.

| Candidate source key | Paper | Main objects/sample | Why it matters for v2 | Likely fields |
| --- | --- | --- | --- | --- |
| `juodzbalis25_jades_blagn` | Juodzbalis et al. 2025, "JADES: comprehensive census of broad-line AGN from Reionization to Cosmic Noon revealed by JWST", arXiv:2504.03551 | 34 JADES Type 1 AGN, 1.5 < z < 9 | Already v1; keep as baseline and consistency check. | z, MBH, Lbol, f_Edd, Mstar |
| `harikane23_nirspec_blagn` | Harikane et al. 2023, "A JWST/NIRSpec First Census of Broad-Line AGNs at z=4-7", arXiv:2303.11946 | 10 faint Type 1 AGN at z = 4.015-6.936 | Early statistical JWST faint-BLAGN sample with host properties. | z, MBH, broad Halpha, Mstar |
| `kocevski23_ceers_hidden_monsters` | Kocevski et al. 2023, "Hidden Little Monsters", arXiv:2302.00012 | CEERS 1670 and CEERS 3210 at z > 5 | Clean low-luminosity broad-line AGN detections; good bridge between seeds and quasars. | z, MBH, Mstar, line widths |
| `larson23_ceers1019` | Larson et al. 2023, "A CEERS Discovery of an Accreting Supermassive Black Hole 570 Myr after the Big Bang", arXiv:2303.08918 | CEERS 1019 at z = 8.679 | One of the key early JWST accreting-BH objects; high-leverage under growth-model assumptions. | z, MBH, Lbol, f_Edd, Mstar |
| `uebler23_ganifs_gs3073` | Uebler et al. 2023, "GA-NIFS: A massive black hole in a low-metallicity AGN at z~5.55", arXiv:2302.06647 | GS_3073 at z = 5.55 | Low-metallicity AGN with massive BH and host comparison. | z, MBH, metallicity, outflow, host |
| `matthee23_lrd_eiger_fresco` | Matthee et al. 2023/2024, "Little Red Dots: an abundant population of faint AGN at z~5", arXiv:2306.05448 | 20 broad-Halpha LRD/faint AGN at z = 4.2-5.5 | Core LRD/faint-AGN population; useful for demographics. | z, MBH, line widths, Lbol |
| `kokorev23_uncover_z850_blagn` | Kokorev et al. 2023, "UNCOVER: A NIRSpec Identification of a Broad Line AGN at z = 8.50", arXiv:2308.11610 | UNCOVER broad-line AGN at z = 8.50 | High-redshift case with potentially elevated BH/host ratio. | z, MBH, Lbol, f_Edd, Mstar limit, lensing |
| `furtak23_a2744_qso1` | Furtak et al. 2023/2024, "A high black hole to host mass ratio in a lensed AGN in the early Universe", arXiv:2308.05735 | Abell2744-QSO1 at z = 7.045 | Strongly lensed LRD/AGN; high BH-to-host ratio. | z, MBH, Lbol, f_Edd, Mstar/lower limit, lensing |
| `maiolino23_gnz11_bh` | Maiolino et al. 2023/2024, "A small and vigorous black hole in the early Universe", arXiv:2305.12492 | GN-z11 at z = 10.6 | Extreme redshift; reported high-accretion candidate BH requiring careful interpretation. | z, MBH, f_Edd, AGN diagnostics |
| `bogdan23_uhz1_xray` | Bogdan et al. 2023, "Evidence for heavy seed origin of early supermassive black holes from a z~10 X-ray quasar", arXiv:2305.15458 | UHZ1 at z ~ 10.3 | X-ray-selected/heavily obscured candidate; useful for tracking a heavy-seed interpretation as one scenario. | z, MBH estimate, Lbol, lensing, X-ray |
| `goulding23_uhz1_nirspec` | Goulding et al. 2023, "UNCOVER: The growth of the first massive black holes...", arXiv:2308.02750 | UHZ1 at z = 10.073 | Spectroscopic redshift and improved host stellar mass for UHZ1. | z, Mstar, notes, cross-link to X-ray MBH |
| `natarajan23_uhz1_obg` | Natarajan et al. 2023/2024, "First Detection of an Over-Massive Black Hole Galaxy UHZ1", arXiv:2308.02654 | UHZ1 interpretation | Useful as an interpretation/model companion to Bogdan/Goulding. | interpretation notes |
| `taylor24_ceers_rubies_blagn` | Taylor et al. 2024, "Broad-Line AGN at 3.5<z<6", arXiv:2409.06772 | 50 CEERS/RUBIES BLAGN at 3.5 < z < 6.8 | Large JWST broad-line sample; likely high value for v2 demographics. | z, MBH, line properties, LRD flag |
| `tripodi24_canucs_lrd_z86` | Tripodi et al. 2024/2025, "Red, hot, and very metal poor...", arXiv:2412.04983 | CANUCS-LRD-z8.6 at z = 8.6319 | High-redshift, metal-poor LRD with broad Hbeta and inferred MBH ~ 1e8 Msun. | z, MBH, metallicity, host |
| `juodzbalis25_qso1_direct_mass` | Juodzbalis et al. 2025, "A direct black hole mass measurement in a Little Red Dot at the Epoch of Reionization", arXiv:2508.21748 | Abell2744-QSO1 at z = 7.04 | Direct/dynamical BH mass check on virial estimates; very important for interpretation tags. | z, dynamical MBH, Mstar limit, lensing |
| `chavezortiz25_ghz2_agn` | Chavez Ortiz et al. 2025, "Significant Evidence of an AGN Contribution in GHZ2 at z = 12.34", arXiv:2511.03035 | GHZ2/GLASS-z12 at z = 12.34 | Candidate highest-redshift AGN/BH; use with caution until interpretation settles. | z, inferred MBH, AGN fraction, caveat |

## Classical high-redshift quasar anchors

These sources are less JWST-like and often have much higher luminosities and
black-hole masses, but they are useful anchors for the high-mass end and for
sanity-checking growth tracks.

| Candidate source key | Paper | Main objects/sample | Why it matters for v2 | Likely fields |
| --- | --- | --- | --- | --- |
| `mortlock11_ulasj1120` | Mortlock et al. 2011, "A luminous quasar at a redshift of z = 7.085", arXiv:1106.6088 | ULAS J1120+0641 | First z > 7 quasar; classic massive early SMBH benchmark. | z, MBH, luminosity |
| `derosa14_zgt65_quasars` | De Rosa et al. 2014, "Black hole mass estimates and emission-line properties of a sample of redshift z>6.5 quasars", arXiv:1311.3260 | Four z > 6.5 quasars | Homogeneous early high-z quasar mass/Eddington analysis. | z, MBH, f_Edd, lines |
| `mazzucchelli17_zgt65_quasars` | Mazzucchelli et al. 2017, "Physical properties of 15 quasars at z greater than about 6.5", arXiv:1710.01251 | 15 z >= 6.5 quasars | Larger homogeneous luminous-quasar set. | z, MBH, f_Edd, MgII |
| `banados17_j1342` | Banados et al. 2017/2018, "An 800-million-solar-mass black hole in a significantly neutral Universe at redshift 7.5", arXiv:1712.01860 | ULAS J1342+0928 at z = 7.54 | Record-setting quasar; strong early-growth constraint. | z, MBH, Lbol |
| `yang20_j1007` | Yang et al. 2020, "Poniua'ena: A Luminous z=7.5 Quasar Hosting a 1.5 Billion Solar Mass Black Hole", arXiv:2006.13452 | J1007+2115 at z = 7.515 | Massive SMBH at z > 7.5. | z, MBH, host SFR |
| `wang21_j0313` | Wang et al. 2021, "A Luminous Quasar at Redshift 7.642", arXiv:2101.03179 | J0313-1806 at z = 7.642 | One of the most massive and distant known luminous quasars. | z, MBH, Lbol, host SFR |
| `onoue19_shellqs_vi` | Onoue et al. 2019, "SHELLQs. VI. Black Hole Mass Measurements of Six Quasars at 6.1<z<6.7", arXiv:1904.07278 | Six low-luminosity quasars at 6.1 < z < 6.7 | Fainter quasar comparison sample with MgII masses. | z, MBH, f_Edd |
| `takahashi23_shellqs_xvii` | Takahashi et al. 2023, "SHELLQs. XVII. Black Hole Mass Distribution at z~6", arXiv:2310.12222 | 131 low-luminosity quasars at 5.6 < z < 7.0 | Large low-luminosity z~6 quasar mass distribution; method differs from direct NIR spectroscopy. | z, MBH, f_Edd, method caveat |
| `wu22_z6_demographics` | Wu et al. 2022, "Demographics of z ~ 6 Quasars in the Black Hole Mass-Luminosity Plane", arXiv:2210.02518 | >100 quasars at 5.7 < z < 6.5 | Population-level check on mass-luminosity selection biases. | derived distributions, selection notes |

## Ingestion notes

- Treat JWST broad-line AGN, LRDs, X-ray AGN, and luminous quasars as separate
  `object_class` values. Their mass methods and selection functions are not
  interchangeable.
- Add a method/provenance field that distinguishes single-epoch virial masses,
  dynamical/spectroastrometric masses, X-ray/Eddington-assumed masses, and
  model-inferred AGN contributions.
- For objects with multiple papers, prefer one measurement row per paper rather
  than overwriting. This keeps interpretation-dependent quantities visible.
- The strongest immediate v2 additions after v1 are Harikane et al., Kocevski
  et al., Larson et al., Kokorev et al., Furtak et al., Maiolino et al.,
  Bogdan/Goulding/Natarajan for UHZ1, Matthee et al., Taylor et al., Tripodi et
  al., and the direct-mass Juodzbalis et al. QSO1 paper.
- Candidate or model-dependent objects, especially GHZ2, should be tagged as
  `candidate-agn` or similar until the observational interpretation is more
  secure.
