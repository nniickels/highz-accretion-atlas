# Shen et al. GNIRS-50 v7.2 extraction and admission notes

The v7.2 catalogue admits the complete 50-object Gemini/GNIRS sample from
Shen et al. (2019), ApJ 873:35, DOI `10.3847/1538-4357/ab03d9`, arXiv
`1809.05584v1`. It is a second large `luminous_quasar_comparison` family and
does not authorize pooling with the faint JWST evidence classes.

## Authoritative inputs

The extraction uses the machine-readable files in CDS catalogue
`J/ApJ/873/35`:

- `table1.dat`: 50 sample, coordinate, redshift, photometry, and comment rows;
  SHA-256 `40ed1598d8c6d4d4a4aa580c578742f9e0334c26bb9dd762a9a0375231a7239f`.
- `table3.dat`: 50 full spectral and mass-catalogue rows; SHA-256
  `e1eae3266b9ccfc966303c6e389e9c16141678199924a67ab4c786fed3240323`.
- arXiv source `1809.05584v1`: SHA-256
  `2b4376dc136873c4b8db0e5016568b9b1d4692042f6bb035e61fa8bd76b980ef`.

`scripts/extract_shen19_cds_tables.py` verifies both CDS hashes, parses the
fixed-width and grouped formats, checks membership and scientific anchors, and
writes `data/raw/shen19_gnirs_table1.csv` and
`data/raw/shen19_gnirs_table3.csv`. The extractor converts the CDS null
sentinels (`0`, `-1`, and `-99`, depending on field) to explicit missing cells.

## Mass and uncertainty policy

The paper's fiducial mass is preserved: Mg II is used when available and C IV
otherwise. Of 50 rows, 29 have fiducial Mg II masses, 20 have C IV-only
fiducial masses, and J0055+0146 has no accepted virial mass. That last object
is retained as a complete source row with `mass_comparability_group` set to
`no_numeric_mass` and is ineligible for growth analyses.

The paper's approximately 0.4 dex single-epoch systematic is stored separately
from its Monte Carlo spectral-fit measurement errors. C IV-only masses remain
growth-eligible but are excluded from the primary Mg II comparison tier. The
published logarithmic Eddington ratios and their errors are converted to
linear ratios without overwriting the original log values in the source-local
observable table.

The 993-observable combined v7.2 table contains the inherited 364 v7.1 rows
plus 629 available GNIRS luminosity, line-width, equivalent-width, alternate-
mass, and Eddington-ratio values. Missing line measurements are not emitted as
fake zero-valued detections.

## Caveats and identity review

All eight BAL annotations and four radio-loud annotations from Table 1 are
retained. The source does not report lensing corrections, so no magnification
is inferred.

Six GNIRS measurements are reviewed as alternate measurements of XQR-30
physical objects. P060+24, J0842+1218, and J0927+2001 pass the fixed 0.5-arcsec
and delta-z 0.01 candidate gate. J0028+0457/PSO J007+04, J0836+0054, and
J2310+1855 are explicit manual assertions based on sub-arcsecond coordinates
and matching aliases because their source redshifts differ by more than 0.01.
The XQR-30 measurement remains preferred for continuity; all GNIRS
measurements and aliases remain available.

The obvious 131-object SHELLQs XVII candidate was not admitted: its public
arXiv source contains composite-level material but no authoritative 131-row
object table. Reconstructing individual values from plots would violate the
source-audit gate.
