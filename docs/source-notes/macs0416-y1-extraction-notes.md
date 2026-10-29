# MACS0416-Y1: published-value extraction and admission basis

Primary measurement: Takechi et al., *DREAMS. JWST Spectroscopy of a z=8.3
Galaxy with an ALMA Dust Continuum Detection: Early Dust, Very High Tdust,
and a Multi-wavelength [OIII] Ratio Discrepancy*,
[arXiv:2605.14922v1](https://arxiv.org/abs/2605.14922v1), submitted
14 May 2026, 14:55:45 UTC. Retrieved and reviewed 17 October 2026 against the
3 September 2026 literature cutoff. The arXiv metadata checked on that date
lists only v1 and says “Submitted to ApJ”; it has no journal reference or
publisher DOI. This verifies the archive's stated status, not an independent
assertion that no later publication exists. All scientific fields below use v1. The archive DOI is 10.48550/arXiv.2605.14922.

## Source coverage and identity

The complete TeX source was retrieved and inspected, including the end of the
paper: it contains 18 figures and no numerical source tables or active appendix.
There is no machine-readable AGN table to expand. Section IV.2.1 and Figures 6–7
contain the one broad-line mass estimate. The source-local screen enumerates
10 entities: Y1/D2; the E, C, W UV clumps; dust peak D1; observational target
LAP1-B; and the four Figure 13 comparison galaxies ID4590, J0217-0208,
SXDF-NB1106-2 and COS-2987. Literature examples and schematic nebular zones
are not additional catalogue targets. Only Y1/D2 supplies an admitted measurement.

Y1 is the host galaxy at systemic spectroscopic z=8.312, taken by Takechi from
ALMA [O III] 88 micron and [C II] 158 micron work. No uncertainty is attached
to that rounded redshift in the adopted source; the catalogue leaves its
error missing. Three UV peaks E/C/W and two FIR peaks D1/D2 are spatial
components of the same system. Only one MSA spaxel passes the Hbeta broad-line
selection; it coincides with western dust peak D2. D1 has no significant broad
component. E/C/W each occupy the empirical MEx AGN region, but that diagnostic
was calibrated at 0.3<z<1 and the authors caution against direct extrapolation.
It cannot establish three accreting black holes. D2 identifies the dust peak,
not the entire W UV component or a globally unique object.

Canonical identities: measurement `MACS0416Y1_takechi26`, physical object
`HZA-MACS0416-Y1`, host `HZS-MACS0416-Y1`; preferred display `MACS0416-Y1`.
Aliases: `MACS J0416-Y1`, `MACS0416_Y1`, `Y1` (source-local only). One measurement,
one admitted object and one host. It is distinct from the SAPPHIRES z~8.479
candidate. HST identification of the galaxy and ALMA redshift confirmation
predate JWST, but do not establish prior AGN discovery. Takechi also explicitly
cites Harshan et al. (2024) as earlier *possible* AGN evidence from JWST line
diagnostics. Takechi supplies the new broad-Hbeta mass measurement, meeting
the JWST evidence scope, rather than the first suggestion of AGN activity.

Takechi does not tabulate a numeric D2 nucleus coordinate. For crossmatching,
the catalogue uses the host UV centroid from Tamura et al.
[arXiv:1806.04132v2](https://arxiv.org/abs/1806.04132v2), Section 2.3:
04:16:09.415, -24:05:35.54 ICRS, or 64.0392291667, -24.0932055556 degrees.
This is the Gaia-registered centroid, not the earlier phase-tracking position
04:16:09.4010, -24:05:35.470. It is not a precise D2 black-hole position.
Takechi's newer alignment uses Gaia DR3 with ~10 mas mean reference offsets;
that number is not an uncertainty on this older host centroid.

All coordinate-bearing measurements in both v2 (218) and v3 (350 total, 323
with coordinates) were screened by great-circle separation. None is within
10 arcsec of the host centroid. The nearest is J0430M1445-BHAE-1 at
35713.39 arcsec and z=4.0947. Identifier/alias/name fields in both versions'
processed and crossmatch files have no MACS0416/Y1 match. All 27 v3 records
without coordinates are enumerated in the crossmatch fixture: 25 CEERS/Mazzolari
objects, GHZ2 and MoM-BH*-1, with incompatible fields/source identities or
redshifts. None is a supported Y1 alias. Missing coordinates cannot prove
all-sky uniqueness, but there is no specific unresolved Y1 match. Existing
unresolved identity groups remain untouched.

## Measurements, corrections and caveats

Section III.3 fits profiles with emcee; flux errors are posterior p16/p84.
Reported velocity FWHMs are intrinsic, after Gaussian LSF deconvolution using
Isobe et al.'s planetary-nebula LSF. They are not velocity dispersions and do
not need a factor 2.355 or a second instrumental correction.

Section IV.2.1 reports Hbeta FWHM = 1100 (+800/-500) km/s and observed broad
flux = 1.43 (+0.62/-0.60) x 10^-19 erg/s/cm². Broad Hbeta is selected when
AIC(double)-AIC(single)<-10; only one spaxel passes. The exact Hbeta delta-AIC
and a Gaussian-equivalent detection significance are not published. The flux
central/error ratio is about 2.3–2.4, not a claimed 5-sigma detection; a model
selection threshold has no stated Gaussian-sigma equivalent.

The same spaxel's broad [O III] 5007 fit has delta-AIC=-7 and FWHM
420 (+120/-100) km/s, below the broad-component adoption criterion. Its width
difference from Hbeta is only ~1 sigma. The authors argue against an outflow
origin using the width difference, collisional suppression in dense BLRs,
and typical non-AGN outflows <=~500 km/s. This is supportive but not decisive;
the Hbeta lower interval endpoint is 600 km/s. An outflow/weak-broad-line
caveat remains. The galaxy and all UV clumps fail the paper's LRD criteria;
the catalogue does not assign the `lrd` phenotype. Neither stellar dust heating nor AGN dust heating
establishes an additional black hole.

Section II.2.2 gives mu=1.60 (+0.01/-0.02), attributed to Harshan using the
Rihtarsic lens model, and says quantities are generally *uncorrected* unless
stated. Section IV.2.1 explicitly states that the BH mass is *after correcting
for lensing magnification*: MBH=1.6 (+3.0/-1.0) x 10^6 Msun, Greene & Ho
(2005), ApJ 630, 122, DOI 10.1086/431897. The catalogue retains that
lens-corrected mass without another division by mu or sqrt(mu). Observed line flux remains observed; a separately
labelled intrinsic flux could be derived by dividing by mu, but is not needed
for adopting the published mass. Width is unchanged by this scalar correction.
No differential-lensing model is supplied. No independent Eddington-ratio
assumption is used to obtain this virial mass.

The mass is a comparable Balmer single-epoch virial estimate, not a dynamical
mass. The target paper cites the calibration without printing coefficients;
the catalogue retains the reported mass without revising the calibration.
Its asymmetric mass/FWHM interval confidence level and calibration-scatter
inclusion are not explicitly specified. The flux percentile convention therefore
does not establish the mass-error convention. Method-scatter numeric fields
remain missing; no additional scatter is assumed.
The TeX contains a *commented-out* no-extinction statement immediately below
the mass paragraph; it is not part of the published rendered text and cannot
establish a broad-line extinction correction. The integrated IFU Hgamma/Hbeta
0.47 (+0.05/-0.04) in Section V.2 is compatible with low optical attenuation,
but the paper emphasizes spatially distinct dusty/optical regions. Broad-line
attenuation treatment remains unspecified; the separate A_V~1.7 nebular
illustration is not applied to the black-hole mass.

The deterministic conversion uses endpoints 0.6e6 and 4.6e6 Msun:
log10(MBH/Msun)=6.2041199827, minus error 0.4259687323 dex, plus error
0.4586378490 dex. Taking logs of 1.0e6/3.0e6 error bars is incorrect.
Approximate host stellar mass ~10^9 Msun is contextual, imported by the paper
from Harshan; no canonical stellar mass/error is adopted here. Lbol,
Eddington ratio, nuclear coordinate errors and redshift errors remain missing.

## Admission and field mappings

Family `takechi26_macs0416_y1` belongs to **v2 and v3**, with v1 unchanged.
It is a one-target Balmer virial source family. Tentative evidence affects
inference eligibility independently of membership, as for tentative Fei rows.
There is no heterogeneous set of independently massed clumps in this source.
The catalogue records `object_class=broad_line_agn`, `spectroscopic_type=type1_broad_line`,
`evidence_status=candidate` on conservative review, with the author's BLAGN
interpretation retained in the evidence basis. Candidate rather than secure
reflects weak flux significance, wide FWHM uncertainty and the weak outflow
separation, not absence of a numerical estimate.

Numerical-growth eligibility is true, `mass_comparability_group=
virial_balmer_single_epoch`, primary-growth flag false; manuscript primary
false and expanded true under the standard catalogue and publication rules.
The supported source-reported virial mass, systemic redshift, one-host identity
and explicit lens correction satisfy numerical-growth eligibility. Growth
calculations use the published asymmetric interval with the catalogue's
approximate mass-error sampling; its confidence convention and calibration-scatter
coverage remain unspecified. Current growth
results are in `results/`. This is the sole preferred measurement
for this object; alternative calibrations and integrated/spaxel data are not
additional independent measurements.

Registry mapping: source key as above; arXiv v1 primary
record and retrieval date in provenance registry; `mbh_method=
single-epoch-virial-hbeta-greeneho2005`, calibration tag `greene-ho2005-hbeta`,
Hbeta species and Section IV.2.1 support in the mass-method registry;
`lensing_status=lensed`, source-corrected mass and Section II.2.2/IV.2.1
provenance. The shared provenance registry records the source archive hash;
independent fixtures identify the reviewed source member. Selection completeness
is unknown, with no population weight: this
was a serendipitous MSA-footprint target of DREAMS GO-4750 observed 5 November
2024, combined with CANUCS IFU data. It is not an unbiased AGN survey.
The focused source validator checks identities, coordinates, redshift, converted
mass/errors, and eligibility. The shared builder populates the canonical schema
and registers the raw FWHM, flux, and magnification observables.

## Catalogue inputs and independent validation files

- `data/raw/takechi26_macs0416_y1.csv`: one native-value mass/line/lensing record.
- `data/raw/takechi26_macs0416_y1_screen.csv`: all 10 screen entities and outcomes.
- `data/validation/takechi26_macs0416_y1_expected.json`: independently read
  native mass endpoints, line, magnification, redshift and coordinate anchors.
- `data/validation/takechi26_macs0416_y1_crossmatch.json`: input hashes, nearest
  neighbours and all missing-coordinate baseline records.
- `data/validation/takechi26_macs0416_y1_adapter.py`: deterministic conversion
  and focused source-value validation; run with Python 3 from any directory.

Source versions, URLs, retrieval dates, and hashes are in the shared provenance
registry, including Tamura's separate coordinate source. Reference copies are
not bundled.

Focused checks pass for mass and both interval endpoints, flux/FWHM/mu errors,
redshift, sexagesimal coordinate conversion, screen cardinality. These checks establish transcription/conversion, not AGN
certainty or virial-calibration validity. Nuclear astrometry, exact mass-error
semantics, and stronger rejection of an outflow remain follow-up limitations.
Shared registries, canonical outputs, and manifests include the admitted candidate.
