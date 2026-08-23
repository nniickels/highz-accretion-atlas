# Lin ASPIRE extraction notes

Primary source: Lin et al., *ASPIRE: Broad-line AGN at z = 4--5 revealed by
JWST/NIRCam WFSS*, ApJ 974:147 (2024),
[doi:10.3847/1538-4357/ad6565](https://doi.org/10.3847/1538-4357/ad6565),
arXiv `2407.17570v1`.

The extraction uses the authoritative v1 arXiv source archive, SHA-256
`fc1c4d96e4a568b09b3caefa0fdde1c7fabe8decad71fb6423ff37c912b024cd`,
checked on 2026-08-22. The raw CSV transcribes all 16 rows and the atlas-relevant
columns from Tables 1--3: coordinates and redshift errors, F356W photometry,
broad/narrow FWHM, broad and total Halpha luminosity, equivalent width, MBH,
Lbol, MUV, and continuum slopes.

The sample is compact-red preselected, then requires integrated line S/N > 5
and a robust broad component with FWHM > 1000 km/s. Table 1 explicitly labels
all 16 as LRDs; `lrd` remains a phenotype and the object class remains
`broad-line-agn`. The Reines et al. (2013) Halpha mass estimator and its stated
0.5 dex intrinsic uncertainty are recorded separately from formal line-fit
errors. Dust correction was not applied.

Three rows carry possible blueshifted Halpha absorption fits:
J0923P0402-BHAE-1, J1526M2050-BHAE-1, and J1526M2050-BHAE-3. The paper states
that absorption versus complex emission remains uncertain. Two rows use the
FWHM and luminosity of the entire multi-broad-component profile for MBH:
J0430M1445-BHAE-1 and J0923P0402-BHAE-1.
