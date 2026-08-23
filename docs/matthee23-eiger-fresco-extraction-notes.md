# Matthee EIGER/FRESCO extraction notes

Primary source: Matthee et al., *Little Red Dots: an abundant population of
faint AGN at z ~ 5 revealed by the EIGER and FRESCO JWST surveys*, ApJ 963:129
(2024), [doi:10.3847/1538-4357/ad2345](https://doi.org/10.3847/1538-4357/ad2345),
arXiv `2306.05448v3`.

The extraction uses the authoritative v3 arXiv source archive, SHA-256
`b3e6f5385e694d92a7456f81eb123a305468baf743cebc7aeea820befb9b1190`,
downloaded and checked on 2026-08-22. The raw CSV transcribes all 20 rows and
all columns relevant to the atlas from Tables 1--3: coordinates, redshift,
broad/total Halpha ratio, broad Halpha luminosity, broad FWHM, photometry,
equivalent width, MBH, Lbol, MUV, and continuum slopes.

Selection requires broad Halpha S/N > 5, broad luminosity > 2e42 erg/s, and
broad FWHM > 1000 km/s, followed by visual rejection of spatially broadened
impostors. All 20 rows are retained at z >= 4. The mass method is the Reines et
al. (2013) Halpha single-epoch estimator with geometric factor 1.075. The
reported statistical errors and the stated 0.5 dex estimator systematic are
kept separate. Masses and Halpha-derived bolometric luminosities are not dust
corrected.

Row caveats include the absorption fits for GOODS-N-9771 and J1148-18404, the
foreground-trace contamination affecting GOODS-S-13971, the flat-continuum
exception J0100-15157, and the complex morphology of J0148-12884. Coordinate
matching identifies GOODS-S-13971 as JADES GS-204851 (0.02 arcsec, delta-z
0.001); both measurements are retained.

The source is labelled an LRD sample at paper level (including in the title),
not with an object-by-object LRD marker in Tables 1--3. Accordingly the atlas
stores `lrd_flag=true` with `lrd_definition=paper_sample_label_little_red_dot`
rather than presenting the flag as a table-row measurement. The
flat-continuum exception remains explicit in its row caveats.
