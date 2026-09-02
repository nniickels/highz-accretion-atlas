# Harikane et al. (2023) NIRSpec extraction notes

## Authoritative source and scope

The v2 source layer uses Harikane et al. (2023), ApJ 959:39,
DOI `10.3847/1538-4357/ad029e`, and the latest primary arXiv source
`2303.11946v3`. The downloaded source archive has SHA-256
`02c2951b4594234f8cc015fc811f1ed438d35997249138af4d756d02d44ca4b4`.
The immutable extraction is `data/raw/harikane23_nirspec_blagn_tables1_3.csv`.

The final sample has ten Type 1 broad-Halpha AGN at `z=4.015--6.936`.
Selection began from 185 NIRSpec galaxies at `zspec=3.8--8.9` and required a
permitted broad component with FWHM greater than 1000 km/s and S/N greater than
5, narrow forbidden lines, and an outflow-component veto. Every retained row
has the source's reported Delta AIC greater than 20.

## Preserved measurements

The raw file preserves Tables 1--3 coordinates, redshift, MUV, metallicity,
reddening, broad-Halpha S/N, Delta AIC, extinction-corrected broad-Halpha
luminosity, broad/narrow ratio, broad FWHM, black-hole mass, bolometric
luminosity, Eddington ratio, and host stellar mass information with asymmetric
errors. Linear mass and luminosity values are retained alongside deterministic
log transforms. Four host values are upper limits; they remain in
`log_mstar_upper_limit_msun` and do not populate the canonical measured-Mstar
field.

The paper states that the stellar-mass systematic from the fixed SED-fitting
prior is typically about `0.2 dex`, smaller than the reported statistical
uncertainty. the canonical atlas records this as `log_mstar_systematic_dex=0.2` with
`mstar_systematic_applied_flag=false`; it is not folded into the tabulated host
errors or any growth diagnostic.

The mass tag is `single-epoch-virial-halpha-greeneho2005`, following Greene &
Ho (2005). The source does not publish a numeric virial-calibration systematic,
so `log_mbh_systematic_dex` remains blank and the canonical atlas does not invent a
Harikane-specific shift scenario. Published asymmetric statistical errors are
propagated separately.

Harikane et al. do not publish an object-level LRD marker. `lrd_flag` therefore
remains missing. The paper's red-AGN and compact-source descriptions are stored
as independent phenotype tags, not converted into LRD labels.

## Identity and caveats

Coordinate, redshift, and source-identifier review links five Harikane rows to
existing physical objects: CEERS-01244, CEERS-00746, CEERS-00672, CEERS-02782,
and CEERS-00397. CEERS-02782 joins the existing Taylor CEERS-2782 and
RUBIES-EGS-50052 measurements, so that physical object has three retained
measurements. Existing release-default measurements remain preferred for
longitudinal reproducibility. The five GLASS/CEERS objects without a verified
prior-release match receive new stable physical IDs.

Row caveats preserve the two narrow-[O III] outflow components, the CEERS-01236
dual-AGN interpretation, broad-C IV/tentative-He II for CEERS-00397, host upper
limits, dust corrections, compactness, and red-AGN descriptions. These tags
support follow-up triage; they do not override the published broad-line-AGN
classification.
