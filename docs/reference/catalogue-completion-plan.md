# Catalogue completion plan

The evidence-based final target is **about 340 unique objects with 237 growth-
plottable objects**, under the fixed z>=4 and JWST-identification rules. This is
more defensible than forcing 350-400 total or 250 plottable objects by admitting
duplicates, conditional masses, or generic objects merely observed by JWST.

The table applies the existing rules: a source must be JWST-essential to the
identification, publish reproducible object-level rows, add physical objects
after coordinate/redshift/alias review, and preserve published mass semantics.
Heterogeneous catalogues belong to v3 at source level even when some rows have
broad lines.

| Priority source | New objects | New plottable objects | Object types | Version | Decision |
| --- | ---: | ---: | --- | --- | --- |
| [Zhuang et al., NEXUS WFSS](https://arxiv.org/abs/2505.20393v1) | 14 | 11 | Broad-line AGN; LRD; one luminous quasar-like AGN | v2 and v3 | Add. Fifteen z>=4 rows contain 12 masses; NX10835 is already a massless Mascia candidate, so the source also makes that existing object plottable. |
| [Lin et al., COSMOS-3D](https://arxiv.org/abs/2504.08039v2) | 13 | 13 | Broad-Halpha/Hbeta AGN; LRD; blue quasar-like AGN | v2 and v3 | Add after final alias audit. All 13 source rows are at z>=5 and publish virial masses. |
| [Napolitano et al., GLASS “Seven wonders”](https://arxiv.org/abs/2410.10967) | 2 | 0 | High-ionization-line AGN candidates | v3 | Add GHZ4 and GHZ7; GHZ9 is already present. This is the small high-ionization extension that adds a new extreme-redshift diagnostic sample. |

Projected catalogue after these batches: **340 objects**. The plottable count
becomes **237** because the NEXUS mass table adds 11 new mass-bearing objects
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

Freeze literature membership after these three batches unless a pre-cutoff
identity audit changes the stated counts. Later discoveries should start a new
dataset version.
