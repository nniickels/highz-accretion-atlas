# Scholtz et al. JADES narrow-line/high-ionization extraction

The v3 catalogue adds every row at `z >= 4` in Scholtz et al. (2025),
A&A 697, A175 (DOI `10.1051/0004-6361/202348804`; arXiv `2311.18731v4`).
The paper table supplies redshift, selection diagnostic, host stellar mass,
SFR, UV magnitude, bolometric luminosity, notes, and seven high-ionization
line fluxes. Host stellar masses come from BEAGLE fits to the full
slit-loss-corrected PRISM spectra. JADES DR3 v3.1.3 supplies target coordinates.

The paper repeatedly reports 42 candidates, but its released `Table_sample.tex`
contains 41 rows. The atlas does not manufacture the missing record: 21 of the
41 tabulated rows meet `z >= 4`, and all 21 are admitted. This discrepancy is
retained in every new row's caveat tags. Three admitted S2-VO87 rows carry the
paper's asterisk, meaning they lie within 0.1 dex of the diagnostic boundary.

All rows remain evidence-status `candidate`. No black-hole mass is published,
so host masses and bolometric luminosities are retained without deriving an
Eddington mass; the v3 growth population stays frozen. JADES 8083 is manually
linked to existing `HZA-GS-8083`: the coordinates agree to 0.013 arcsec and the
paper labels it Type 1. The existing broad-line mass measurement remains the
preferred object-level row despite the papers' differing redshift values. The
catalogue's conservative worst-evidence object aggregate is nevertheless
`candidate` for this multiply measured object, without changing its numeric
mass or growth eligibility.

Provenance hashes:

- arXiv source archive: `1754f005be9e77cc619e52c42b9d47f27fa66fd4d0e80cfd0406afdeca463624`
- JADES DR3 GOODS-S prism catalogue: `e30d7cc9be5c997e73b47023b03df79658e8f797407ea9361295dd7d488b56ba`
