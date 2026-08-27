# XQR-30 v7.1 extraction and admission notes

The v7.1 catalogue admits the complete 42-object E-XQR-30 table from
Mazzucchelli et al. (2023), A&A 676 A71, DOI
`10.1051/0004-6361/202346317`. The canonical mass is the published MgII
single-epoch virial estimate. The CIV mass, reported CIV width and blueshift,
both continuum luminosities, MgII width, and CIV Eddington ratio remain
source-local observables.

## Authoritative inputs

- `data/raw/xqr30_mazzucchelli23_table1.csv` is extracted from Table 1 in the
  arXiv `2306.16474v1` source archive. Archive SHA-256:
  `412055cec92c368f711605822d806c949816695a451efee867904d2171fee53f`.
- `data/raw/xqr30_dodorico23_coordinates.csv` is extracted from the 42-row
  E-XQR-30 Table 1 in D'Odorico et al. (2023), MNRAS 523, 1399, arXiv
  `2305.05053v1`. Archive SHA-256:
  `1cf315f5fd4cd9f0edebb840c254dcd6bee26e2a061ce9fc9ff5bc8f344d7c42`.
- `python -m scripts.extract_xqr30_arxiv_tables MASS_ARCHIVE SAMPLE_ARCHIVE`
  verifies both hashes and the paired 42-row order before writing either CSV.

Coordinates and canonical names come from the sample paper; abbreviated mass-
table names are retained as aliases. This also preserves the mass-table spelling
`VDES J2250-5051` as an alias while using the coordinate-paper identifier
`VDES J2250-5015` for the object. No silent spelling repair is made.

## Caveats and consistency findings

- Seven named MgII fits are close to or within strong telluric absorption.
- PSO J065+01 also has very low CIV-region S/N.
- BAL classifications are retained as source caveats, not object classes.
- WISEA J0439+1634 is explicitly lensed. The published XQR-30 mass and
  luminosity are not magnification-corrected; `lensing_mu=51.3` is recorded
  from the Fan/Yang lensing provenance and the correction status remains
  `not_applied`.
- Four published MgII Eddington ratios differ by more than 0.3 dex from the
  value implied by the same table's MgII mass and bolometric luminosity:
  VST-ATLAS J025-33, WISEA J0439+1634, ULAS J1319+0950, and
  CFHQS J1509-1749. The published values are preserved, the independently
  implied values remain in `edd_ratio_from_mbh_lbol`, and all four rows carry
  `published_mgii_edd_ratio_internal_inconsistency`. No value is silently
  replaced.

## Identity audit

The coordinate/redshift search finds no candidate against the v7.0 atlas.
Section 4.4 of the mass paper identifies 23 objects with earlier measurements
in the wider literature, but those comparison measurements are not rows in
v7.0. `data/crossmatch/v7_1_external_literature_identity_audit.csv` therefore
records all 23 as reviewed external repeats and new atlas physical objects,
including the separately treated lensed quasar. The release candidate table is
empty because there is no prior-atlas pair to accept or reject.

## Release boundary

XQR-30 is a `luminous_quasar_comparison` stratum with a separate UV virial-mass
comparability group. v7.1 produces catalogue, identity, observable, and strata
products only. It does not pool this bright, preselected quasar sample into the
faint-JWST growth analysis and generates no science rankings or figures.
