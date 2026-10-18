# J1007_AGN: published-value extraction and catalogue admission

Primary source: Schindler et al., *A little red dot at z=7.3 within a large
galaxy overdensity*, Nature Astronomy 9, 1732–1744 (2025),
[DOI](https://doi.org/10.1038/s41550-025-02660-1), version of record
17 September 2025. Retrieved 17 October 2026; literature cutoff 3 September
2026. Corresponding archive is [arXiv:2411.11534v2](https://arxiv.org/html/2411.11534v2),
submitted 19 September 2025 at 11:12:33 UTC. The 18 November 2024 v1 has a
different dust model (A_V=3.26) and headline mass; do not mix its values with
this extraction. Published tables govern numerical values here. Archive v2
provides machine-readable table support, not authority to overwrite the publisher.

## Catalogue inputs and independent anchors

- `data/raw/schindler25_j1007_agn_mass_alternatives.csv`: observed and dereddened fiducial estimates, in published linear mass units.
- `data/raw/schindler25_j1007_source_screen.csv`: all nine Extended Data Table 3 sources, explicit outcomes.
- `data/validation/schindler25_j1007_expected.json`: independent transcription anchors from the viewed publisher images; errors ordered central, minus, plus.
Source versions, URLs, retrieval dates, and hashes are in the shared provenance
registry. Published table images were inspected during extraction; reference
copies are not bundled.

## Complete screen and identity

Extended Data Table 3 has one AGN, J1007_AGN, and eight galaxies:
J1007_10660, J1007_11721, J1007_11812, J1007_5524, J1007_9336,
J1007_3984, J1007_3850 and J1007_16615. Only the AGN is admitted.
The galaxies' [O III] emission and shared environment alone do not establish
AGN evidence. Table 4 repeats their environmental properties, not additional
objects. Table 5 contains clustering bins, not black holes. Figures' comparison
AGN/quasars and literature populations are context, not discoveries in this source.

J1007_AGN is at RA=151.978226, Dec=21.283994 degrees, J2000,
spectroscopic [O III] z=7.2583. Do not assign the alias J1007+2115 or
Pōniuā‘ena: that is the known ground-selected z≈7.51 field quasar, outside this
source's new JWST sample and a distinct physical object. No unsupported
coordinate-derived name is introduced.

Both v2/v3 measurement tables and object/alias records were searched for
J1007 and Schindler names: no match. Spherical positional comparison of all
available v2/v3 measurement coordinates finds no source within 1 arcminute;
nearest is DC873321_ren25 at 67517.192 arcsec (z=5.1542). The pre-admission v2/v3 catalogues were used for this screen. All 218 v2 rows
have coordinates; 27/350 v3 rows lack coordinates and were reviewed by name
search without a J1007 match. Their absence prevents a coordinate-only proof,
but no source evidence suggests an overlap. Object tables inherit measurement
coordinates; there is no competing local identity. Within the source, the
nearest companions are 17.31 and 18.33 arcsec away (Table 4), not aliases.
The catalogue admits one new physical object and one host, with no identity override needed.

## Mass, errors and preferred interpretation

Table 1 default R≈273 column gives the observed fiducial
M_BH,GH05,LHbeta = (11.52 -4.63 +10.11) ×10^7 Msun.
Table 2 gives the dereddened value (45.14 -23.20 +52.18) ×10^7 Msun.
Use the table precision rather than the methods' rounded
(4.51 -2.32 +5.22) ×10^8 or abstract's 5×10^8.

The fiducial recipe is Greene & Ho (2005), using broad Hβ FWHM and **total**
Hβ luminosity as a continuum proxy (publisher Methods explicitly says total).
Do not substitute the broad-component flux for the luminosity input.
Broad FWHM is 3370.06 -648.27 +1155.54 km/s; the fit models instrumental
resolution. Hβ-derived log Lbol is 45.52 -0.06 +0.08 observed and
46.64 -0.12 +0.13 corrected, from GH05 line-to-continuum scaling and
Lbol=9.26 L5100. Reported Eddington ratios are 0.20 -0.09 +0.13 and
0.58 -0.31 +0.62. These are correlated derived quantities, not independent
accretion constraints. The source's L5100 table is per angstrom; do not mistake
its log 40.43 for lambda Llambda.

Errors are posterior 16th–84th percentile statistical intervals. Calibration
systematics are discussed separately as approximately ±0.43 dex; do not claim
these are included in the tabulated statistical errors or add them silently.
The corrected posterior propagates sampled A_V=2.79±0.25 mag from the
reddened AGN plus scattered-light continuum model. The authors consider dust
attenuation probable and discuss the corrected estimate as the intrinsic mass,
while explicitly retaining both interpretations; it is not a uniquely measured
intrinsic mass independent of the continuum model.

The catalogue adopts observed GH05 Hβ as preferred for the conservative comparable
Balmer baseline, with the dust-corrected estimate retained as a correlated
sensitivity observable/alternative on the same measurement/object. This is a
catalogue policy choice, not a claim that the authors prefer an unattenuated
physical model. The corrected case tests the inferred growth pressure if the
source's dust-screen/scattered-light interpretation is valid. It raises log mass
by 0.59310908 dex. Do not count two black holes or statistically combine them.

Deterministic mapping: log M=log10(central×10^7);
err_minus=log10(central/(central-minus));
err_plus=log10((central+plus)/central).
Observed: 8.06145248 -0.22323326 +0.27360404 dex.
Corrected: 8.65456155 -0.31332493 +0.33364055 dex.
Other Table 1 estimators (VP06, continuum GH05, P12) and R≈278/268 resolution
trials are systematic checks, retained in source tables, not independent
catalogue measurements.

Table 1 reports z error ±0.0005, whereas main text reports ±0.0006. Preserve
both locations; the catalogue adopts the table value ±0.0005. The table and main text also disagree
on M1450; no UV magnitude is adopted here. These discrepancies do not affect
the central redshift or mass extraction.

No lens model, magnification or lens correction is applied by this blank-field
source. The catalogue records `unlensed` under its field-source convention;
raw magnification is missing, not a measured mu=1. Do not demagnify again.
Host stellar mass and uncertainties remain missing.

## Catalogue mapping and eligibility

Source/family key `schindler25_j1007`; source name Schindler et al. (2025),
GO 2073 NIRSpec/MSA PRISM J1007 field; one secure broad-line AGN, phenotype
`lrd`; Balmer single-epoch virial comparability. Preferred measurement
ID `J1007AGN_schindler25_observed`, object display/alias `J1007_AGN`, physical
object `HZA-J1007-AGN`, and host `HZS-J1007-AGN`.
Map raw coordinates/redshift directly, mass via endpoint conversion above,
`mbh_method` to GH05 Hbeta, broad Hbeta to detection evidence, and source
statistical versus additional method uncertainties separately. Raw corrected
row ID `J1007AGN_schindler25_dust_corrected` is an alternative key, not an
instruction to emit an extra independent measurement.

Family membership is **v2 and v3**, with v1 unchanged. The single-source
family has comparable Balmer virial evidence and a supported numerical mass.
Numerical-growth and manuscript-primary/expanded eligibility apply to the
observed preferred estimate: secure broad-line evidence, resolved identity,
supported recipe and field lensing treatment. Keep estimator applicability at
high redshift and continuum/dust interpretation explicit. Corrected values
belong in sensitivity comparisons, not another primary object. No growth ranks
are defined by this source note; current calculations are in `results/`.

The clustering estimate log10(f_duty)=3.66 -3.90 +5.89 measures occupation of
an observed LRD phase through halo abundance; its median is unphysical and
its uncertainty/systematics are large. The authors discuss physical values
near 100%, but this does not measure the fraction of a black hole's available
growth interval spent accreting. Do not feed either number into a growth-model
accreting-time fraction, clip the posterior to one, or infer population fractions
from this single-object discovery.

The canonical build registers the source and fixtures and applies the
deterministic mapping and preferred-observable policy.
There is no unresolved scientific admission blocker for the observed baseline;
the table/text discrepancies and dust interpretation remain documented caveats.

## Reviewed canonical admission

Admitted 17 October 2026 at the unchanged 3 September 2026 cutoff.
Final measurement `J1007AGN_schindler25_observed`, physical object `HZA-J1007-AGN`, host `HZS-J1007-AGN`.
Membership: **v2 and v3; primary and expanded numerical samples**. Adopted semantics: observed GH05 total-Hbeta baseline; dust-corrected model retained as a correlated observable and sensitivity.
Each family contributes one new physical object and one preferred measurement;
model alternatives do not add measurements or objects. The source-level screen
and exclusions above remain the scientific provenance for that decision.
The three older unresolved catalogue identity groups remain excluded from
manuscript inference. Canonical values are built by
`src/internal/october2026_additions.py`, with independent source-native fixtures
registered in the complete mass/error and redshift/coordinate checks.
