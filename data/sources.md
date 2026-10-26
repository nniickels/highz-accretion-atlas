# Source bibliography

The [source registry](source_provenance_registry.csv) records exact publication
versions, source roles, URLs, DOIs, archive hashes, extraction dates, and
publication-status review dates. Publication status and evidence strength are
separate fields. Paper and dataset DOIs are also recorded separately.

The [literature scope](../docs/reference/literature-scope.md) defines the cutoff
and exclusions. The [source notes](../docs/source-notes/README.md) explain
extraction, adopted values, identities, and source-specific caveats.

## Sources with extraction notes

| Source | Catalogue use | Details |
| --- | --- | --- |
| Taylor CEERS/RUBIES | Broad-line measurements; CEERS-2782 and RUBIES-EGS-50052 are one object. | [Source notes](../docs/source-notes/taylor24-ceers-rubies-extraction-notes.md) |
| Matthee EIGER/FRESCO | Broad-Halpha measurements; GOODS-S-13971 matches JADES GS-204851. | [Source notes](../docs/source-notes/matthee23-eiger-fresco-extraction-notes.md) |
| Lin ASPIRE | Compact broad-Halpha emitters. | [Source notes](../docs/source-notes/lin24-aspire-extraction-notes.md) |
| Harikane NIRSpec | Broad-Halpha masses and separately recorded host-mass limits. | [Source notes](../docs/source-notes/harikane23-nirspec-extraction-notes.md) |
| Davis THRILS | Broad-Halpha measurements; coordinates from Hutchison programme tables. | [Source notes](../docs/source-notes/davis26-thrils-extraction-notes.md) |
| Ren ALPINE–CRISTAL–JWST | Seven candidate nuclei in six hosts, with distinct evidence tiers. | [Source notes](../docs/source-notes/ren25-alpine-cristal-jwst-extraction-notes.md) |
| Baccus and Fei GLIMPSE | Broad-line masses; source-specific lensing exclusions and corrections. Baccus adopted values use arXiv v1, with published-v2 changes tested separately. | [Source notes](../docs/source-notes/baccus26-fei26-v2-expansion-extraction-notes.md) |
| UHZ1: Bogdán, Goulding, and Zou | Original X-ray evidence and later disputed reanalysis; no canonical growth mass. | [Source notes](../docs/source-notes/uhz1-xray-evidence-history-extraction-notes.md) |
| Scholtz JADES narrow-line candidates | All 21 source-table rows at z ≥ 4; one overlaps a broad-line object. The paper's prose reports 42 objects but its table has 41. | [Source notes](../docs/source-notes/scholtz25-jades-narrow-line-extraction-notes.md) |
| Chisholm, Tang, Mazzolari, Leung/MEOW, Lyu/SMILES, Napolitano/GHZ9, Zhang, Chavez Ortiz/GHZ2, Mascia, Treiber, and Naidu | Eleven heterogeneous families; conditional estimates and upper limits remain contextual rather than canonical growth masses. | [Source notes](../docs/source-notes/heterogeneous-v3-expansion-extraction-notes.md) |
| Zhuang NEXUS, Lin COSMOS-3D, and Napolitano Seven Wonders | Heterogeneous v3 samples, including masses without reported errors and mass-free candidates. | [Source notes](../docs/source-notes/nexus-cosmos3d-seven-wonders-extraction-notes.md) |
| Taylor CAPERS-LRD-z9 | Broad-Hbeta virial mass with correlated dust alternatives. | [Source notes](../docs/source-notes/capers-lrd-z9-extraction-notes.md) |
| Tripodi CANUCS-LRD-z8.6; Morishita context | Lens-corrected Balmer mass; Morishita v2 adds no separate object or mass. | [Source notes](../docs/source-notes/canucs-lrd-z86-extraction-notes.md) |
| Schindler J1007_AGN | Observed Balmer baseline; dust-corrected interpretation retained separately. | [Source notes](../docs/source-notes/j1007-agn-extraction-notes.md) |
| Takechi MACS0416-Y1 | Lens-corrected candidate mass, expanded sample only. | [Source notes](../docs/source-notes/macs0416-y1-extraction-notes.md) |
| Fudamoto SAPPHIRES ID-8760 | Tentative candidate without a numerical black-hole mass. | [Source notes](../docs/source-notes/sapphires-z847-extraction-notes.md) |

## Juodžbalis JADES broad-line sample

- **Citation:** Juodžbalis et al. (2026), *JADES: comprehensive census of broad-line AGN from Reionization to Cosmic Noon revealed by JWST*, MNRAS 546, stag086, arXiv:2504.03551
- **Published record:** DOI https://doi.org/10.1093/mnras/stag086; arXiv https://arxiv.org/abs/2504.03551
- **Survey/Field:** JADES / GOODS-N + GOODS-S
- **Object selection used here:** Type 1 (broad-line) AGN from JADES spectroscopy
- **Values extracted:** z, MBH, Lbol, lambda_Edd, Mstar
- **Extraction location:** Table 2 (AGN properties: coordinates, z, MBH, Lbol, lambda_Edd), Table 5 (host properties: Mstar)
- **Method notes:** MBH from single-epoch virial estimators: Reines & Volonteri (2015) H-alpha for the main sample, with a source-stated 0.3 dex calibration uncertainty; Vestergaard & Peterson (2006) H-beta for the four high-redshift tentative candidates, for which this source does not state a numeric calibration systematic. Eddington ratios are source-derived from the same bolometric luminosities and virial masses. Host Mstar follows the paper's adopted spectral-decomposition choice: BEAGLE by default, with CIGALE used when BEAGLE is unavailable or the host is significantly extended. CIGALE is adopted for GS-200679, GS-20030333, and GS-164055. The reviewed method mapping is maintained separately in `data/mass_method_registry.csv` and does not alter frozen catalogue values.
- **Detection evidence:** `GS-20057765`, `GS-20030333`, `GS-164055`, and `GN-4685` are the paper's tentative broad-H-beta emitters. Their individual broad-H-beta detections are not formally significant; the four-object stack supports the broad component. The catalogue records this as `stack_supported_tentative_hbeta` and does not treat these rows as individually confirmed detections.
- **Source consistency warning:** For GN-11836, Table 2 reports `log_mbh=6.06`, `log_lbol=44.11`, and `lambda_Edd=0.11`. The mass and luminosity imply `lambda_Edd` approximately 0.89, a -0.91 dex residual for the tabulated ratio. The catalogue preserves all three published values verbatim, flags the inconsistency structurally, and requires source clarification before choosing which value to revise.
- **Columns standardized beyond paper tables:** `redshift_kind=spec` (NIRSpec spectroscopy), method fields encode the paper methodology (`single-epoch-virial-halpha` or `single-epoch-virial-hbeta`, BEAGLE or CIGALE host decomposition, Balmer-line bolometric correction), `agn_contam_flag=1` for this Type-1 AGN sample, and `lensing_mu` left blank because no magnification correction is reported for these sources.
- **Ingestion notes:** Numeric values copied directly; asymmetric uncertainties split into *_err_plus and *_err_minus
- **Provenance limitation:** the original extraction date is unknown
  (`not_recorded_in_frozen_v1_source_layer`). The current registry's verified
  source version, archive URL, and hash are retained separately from that history.

## Other v2 broad-line sources

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
- **[source_key: killi24_j0647_lrd_blagn] Killi et al. (2024):** J0647-1045
  LRD is admitted from its JWST/NIRSpec broad-Halpha identification and published
  virial mass. Killi et al. (2024), Section 2.1, apply no magnification correction:
  the object lies on the outskirts of the lensing field and the expected
  magnification is small. The catalogue retains that source assumption.
- **[source_key: ubler24_zs7_offset_blagn] Uebler et al. (2024):** the
  spatially offset broad-Hbeta Type-1 nucleus in the ZS7 merging system is
  admitted with its published canonical virial mass.

These additions contribute 40 unique physical objects to v2 and flow into v3.
The Jones et al. compilation contributes no further unique object after the
identity audit and is not added as new catalogue membership.

## v3 source: GN-z11 high-ionization-line candidate

- **[source_key: maiolino24_gnz11_agn] Maiolino et al. (2024):** GN-z11 is a
  JWST/NIRSpec-identified accretion candidate based on dense high-ionization and
  broad permitted-line evidence. Its published UV single-epoch mass is retained
  as a numerical secondary stratum, not folded into the primary Balmer-virial
  comparison. This heterogeneous evidence type is v3-only.

The [mass and publication-version audit](../docs/source-notes/mass-error-and-publication-revision-audit.md)
records the Killi correction, numerical-mass validation, and Baccus revision
comparison. Coordinate and context sources are identified by role in the registry.
