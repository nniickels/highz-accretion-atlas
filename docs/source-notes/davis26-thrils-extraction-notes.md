# Davis/THRILS source extraction notes

The v2 source layer used Davis et al., *Extreme Emission Line Galaxies in CEERS
Are Powered by Star Formation, not AGN*, arXiv `2602.23310v1`, submitted to
ApJ on 2026-02-26. No later arXiv version or refereed publication was available
on the 2026-08-25 literature check. The authoritative Appendix Table 5 contains
seven broad-Halpha measurements. The immutable extraction is
`data/raw/davis26_thrils_blagn_table5.csv`; processing, not raw storage, applies
`z >= 4` and retains six rows.

Table 5 supplies THRILS and CEERS IDs, photometric and spectroscopic redshifts,
broad- and narrow-Halpha fluxes with formal errors, and logarithmic virial MBH
with formal errors. It does not tabulate coordinates, row-level LRD labels,
stellar mass, bolometric luminosity, Eddington ratio, or per-row FWHM except
that the text reports `1696 +/- 51 km/s` for THRILS 40467. Those unavailable
values remain blank.

Coordinates and higher-precision programme redshifts are joined exactly by
THRILS ID from Hutchison et al., arXiv `2512.12509v1`, Table 3. The canonical
catalogue redshift remains the Davis Table 5 value; `program_redshift` preserves
the second source value. Both source versions, archive URLs, and source-archive
SHA-256 values are retained in every processed THRILS row.

The broad-line selection requires a broad component above 3 sigma and implied
FWHM above 1000 km/s after the source's line fitting. MBH uses Davis et al.
equation 1, the Reines & Volonteri (2015) Halpha single-epoch estimator, tagged
`single-epoch-virial-halpha-reinesvolonteri2015`. Formal errors propagate the
broad-flux/FWHM posterior. The paper's approximately `0.5 dex` intrinsic
single-epoch scatter is stored separately and is never folded into those
errors or the nominal mass.

THRILS 46155 is the sole row below the project cut and is a repeat observation
of RUBIES-EGS-50812 from Taylor. It remains in the source-native raw table but
not in the admitted dataset. A coordinate/redshift search found no previously admitted identity candidate for any
of the six retained rows within 0.5 arcsec and delta-z 0.01, so they enter as
six new physical objects.

One source caveat cannot be resolved safely: the prose and Appendix discussion
are internally inconsistent about which individual rows remain extreme EELGs,
including a duplicated THRILS ID in one list. the canonical atlas therefore records a source
caveat but does not invent a row-level extreme-EELG phenotype. The paper's
sample-level colour discussion is likewise not converted into row-level LRD
flags.

Primary sources:

- Davis et al.: https://arxiv.org/abs/2602.23310v1
- Hutchison et al. THRILS programme catalogue: https://arxiv.org/abs/2512.12509v1

