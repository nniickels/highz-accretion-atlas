# Catalogue completion record

The evidence-based final target is **340 unique objects with 237 growth-
plottable objects**, under the fixed z>=4 and JWST-identification rules. It was
implemented on 2026-09-03. This is
more defensible than forcing 350-400 total or 250 plottable objects by admitting
duplicates, conditional masses, or generic objects merely observed by JWST.

The table applies the existing rules: a source must be JWST-essential to the
identification, publish reproducible object-level rows, add physical objects
after coordinate/redshift/alias review, and preserve published mass semantics.
Each source receives one admission version. Heterogeneous catalogues belong to
v3 at source level even when some rows have broad lines. All three sources below
are JWST-identified: JWST spectroscopy or JWST spectrophotometry is essential to
the source identification and classification, rather than merely following up a
previously identified object.

| Priority source | New objects | New plottable objects | Object types | Admission version | JWST identification basis | Decision |
| --- | ---: | ---: | --- | --- | --- | --- |
| [Zhuang et al., NEXUS WFSS](https://arxiv.org/abs/2505.20393v1) | 14 | 11 | Broad-line AGN; LRD; one luminous quasar-like AGN | v3 | JWST/NIRCam WFSS line identification and classification | Added. Fifteen z>=4 rows contain 12 masses; NX10835 matches the existing massless Mascia candidate and makes that object plottable. |
| [Lin et al., COSMOS-3D](https://arxiv.org/abs/2504.08039v2) | 13 | 13 | Broad-Halpha/Hbeta AGN; LRD; blue quasar-like AGN | v3 | JWST/NIRCam grism broad-line identification and classification | Added after an alias and 10-arcsec coordinate/redshift audit found no prior object. |
| [Napolitano et al., GLASS “Seven wonders”](https://arxiv.org/abs/2410.10967) | 2 | 0 | High-ionization-line AGN candidates | v3 | JWST photometry and NIRSpec high-ionization-line identification | Added GHZ4 and GHZ7; GHZ9 was already present. |

Final v3 catalogue after these batches: **340 objects**. The plottable count is
**237** because the NEXUS mass table adds 11 new mass-bearing objects
and upgrades one existing object, while COSMOS-3D adds 13.

## Measurement upgrade outside the size target

[Juodzbalis et al. (2026)](https://arxiv.org/abs/2508.21748v2) adds no physical
object: A2744-QSO1 is already in v2/v3. A future version should add its direct
MOKA3D dynamical estimate, log(MBH/Msun)=7.7+/-0.3, and the inclination-free
lower-limit result as a separate measurement with direct-mass comparability.
It changes the preferred evidence for one object while leaving object and
plottable-object counts unchanged.

## Screened out

- Pan et al. NEXUS MSA is a heterogeneous v3 source, but its 36 LRDs do not
  publish canonical black-hole masses and largely repeat an already represented
  phenotype. Retain it for selection-function calibration rather than inflate
  catalogue membership.
- The eJWST AGN catalogue indexes observations of previously identified AGN;
  JWST is not generally the identifying instrument, so it fails the admission
  boundary.
- Compilations or reanalyses that add zero physical candidates remain
  provenance/context sources rather than new catalogue membership.

Literature membership is frozen after these three batches. Later discoveries
require a new dataset version.

> Audit update (2026-09-05): this is a historical completion record. The
> [identity audit](../source-notes/redshift-identity-audit.md) finds three duplicate
> groups and two unresolved neighbours, so the stored object count is provisional.
