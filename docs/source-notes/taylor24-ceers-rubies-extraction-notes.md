# Taylor CEERS/RUBIES Extraction Notes

## Authoritative source

- Taylor et al. (2025), *Broad-Line AGNs at 3.5<z<6: The Black Hole Mass
  Function and a Connection with Little Red Dots*, The Astrophysical Journal
  986, 165, published 2025-06-20.
- Latest primary publication: https://iopscience.iop.org/article/10.3847/1538-4357/add15b;
  DOI https://doi.org/10.3847/1538-4357/add15b.
- Corresponding latest arXiv version: `arXiv:2409.06772v2`, revised 2025-05-14:
  https://arxiv.org/abs/2409.06772v2.
- Machine-readable extraction source: the TeX for Table 1 in that v2 arXiv
  source archive, downloaded from https://arxiv.org/e-print/2409.06772v2
- Downloaded archive SHA-256:
  `50453a0a975b84f019ceba8da30663e40d83c285376cad119d83fa8e3b31aaa0`
- Official publisher PDF SHA-256:
  `b58bd18ab4d467a4bb871353ec0bdbf2fae49d93738f376abef8062820ea6b83`.
- Extraction date: 2026-08-17.

The journal Table 1 and notes were visually checked against the arXiv-derived
table. The row set, values, markers, duplicate note, and mass-systematic note
match; the TeX archive remains the extraction artifact because it is directly
machine readable.

The abstract metadata still reports the older 50-object/10-LRD result. The v2
manuscript body and Table 1 supersede those stale abstract counts.

## Verified counts

| Scope | Measurements | Physical objects | LRD | Absorption fit |
| --- | ---: | ---: | ---: | ---: |
| Full Table 1 | 63 | 62 | 21 | 4 |
| Processing selection, `z >= 4` | 37 | 36 | 17 | 3 |
| Expanded release including v1 | 60 | 59 | not pooled as a v1-wide demographic | not pooled |

The one measurement/object difference is the explicit duplicate pair
`CEERS-2782` and `RUBIES-EGS-50052`. They have independent Table 1 values and
are both preserved.

## Selection and measurements

The source selection requires JWST/NIRSpec G395M Halpha with broad-component
FWHM greater than 700 km/s, broad-flux S/N greater than 4, improvement of
`Delta BIC > 6`, a secure multi-line spectroscopic redshift, and visual quality
assessment. The processing layer applies the project threshold `z >= 4`; the
raw source file retains every published row down to `z=3.499`.

Table 1 supplies decimal coordinates, spectroscopic redshift, total/narrow/broad
Halpha fluxes and asymmetric errors, instrument-corrected broad FWHM and errors,
and virial `log(MBH/Msun)` with formal asymmetric errors. Dagger markers supply
the LRD phenotype and double-dagger markers identify spectra fit with Halpha
absorption.

Masses use the Reines et al. (2013) Halpha single-epoch virial calibration. The
source derives formal mass intervals from correlated Halpha-flux and FWHM
posteriors. These intervals exclude the approximate 0.5 dex calibration scatter,
which the paper notes may be larger at high redshift. The nominal Table 1 values
are not corrected for dust.

## Preserved caveats and limitations

- `RUBIES-EGS-50052`: retained as a BLAGN, although the paper discusses a
  possible outflow contribution. It is the preferred measurement of the object
  also observed as CEERS-2782.
- `CEERS-2782`: retained as a separate measurement, but marked nonpreferred
  because of severe spatial slit loss.
- `RUBIES-EGS-49140`: retained under the paper's BLAGN classification, with the
  alternative compact-galaxy/non-AGN broadening interpretation recorded.
- Four double-dagger Table 1 rows have explicit Halpha absorption-fit flags.
- The text states that 11 spectra have contamination issues, but Table 1 and its
  notes do not identify the complete 11-object set. No row-level contamination
  flags were guessed. This remains unavailable source metadata.
- The LRD definition is the source-adopted Kocevski et al. (2024) photometric
  selection. LRD status is not treated as an AGN class or as independent proof
  of accretion.
