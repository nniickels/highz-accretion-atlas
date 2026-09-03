# Ren ALPINE--CRISTAL--JWST source extraction notes

The v2 source layer uses Ren et al., *The ALPINE--CRISTAL--JWST Survey:
Revealing Less Massive Black Holes in High-Redshift Galaxies*, MNRAS 544,
211--233, DOI `10.1093/mnras/staf1709`. The article was published on
2025-10-25 and corrected/typeset on 2025-10-28. The corresponding latest arXiv
version found in the 2026-08-25 audit is `2509.02027v2`, revised 2025-10-02.
No later arXiv revision or formal erratum was found.

Primary sources:

- Published article: https://academic.oup.com/mnras/article/544/1/211/8301219
- arXiv record: https://arxiv.org/abs/2509.02027v2
- DOI: https://doi.org/10.1093/mnras/staf1709

The arXiv v2 source archive (`https://arxiv.org/e-print/2509.02027v2`) has
SHA-256 `c528c375fda9362433184cb35775a5f4ca107014f4b1c2f6536d7f15d4f85cca`.
Its TeX Tables 1--2 were checked against the publisher rendering and the raw
CSVs.

## Authoritative source files

- `data/raw/ren25_alpine_cristal_jwst_table1.csv` contains all seven published
  Table 1 candidate-nucleus rows plus explicit annotations from the
  object-by-object discussion.
- `data/raw/ren25_alpine_cristal_jwst_table2_observables.csv` contains all 70
  Table 2 line entries in long form: 58 detections and twelve published
  3-sigma upper limits.

Table 1 supplies coordinates, far-infrared [C II] redshifts, dust-corrected
broad-Halpha fluxes, instrument-corrected broad FWHM, integrated host masses,
virial black-hole masses, bolometric luminosities, logarithmic Eddington
ratios, E(B-V), and Av. Its MBH errors are formal statistical errors propagated
from broad-flux and FWHM uncertainties. Table 2 supplies ten line fluxes or
limits for each candidate using the same aperture spectra.

The object-specific prose sometimes quotes uncorrected broad-Halpha fluxes,
which differ from the dust-corrected Table 1 values. The raw Table 1 extraction
uses only the explicitly labelled dust-corrected values. Narrative fluxes are
not substituted or mixed with them.

## Selection and evidence

The parent survey contains 18 massive main-sequence galaxies at `z=4.4--5.7`
and 33 photometric-centre aperture spectra. The line-fitting gate constrains
narrow FWHM below 600 km/s and the added broad Halpha Gaussian above
600 km/s, requires `Delta BIC > 10` and broad-flux `S/N > 3`, then evaluates
[O III] outflows and applies the published broad-to-narrow flux-ratio veto.
Ten initial broad components become nine after excluding the low-S/N ambiguous
`DC_873756`, then seven after the outflow-ratio veto. `DC_842313` lacks the
required G395M Halpha coverage.

Only `DC_536534` is the source's highly robust candidate. It has a stable
narrow+broad+outflow Halpha decomposition, an independently detected [O III]
outflow, a compact broad-component spatial profile, and detected He II. The
other six have corrected widths of 596--1618 km/s and retain the source's
explicit outflow/intermediate-width ambiguity. The canonical admission mapping is
therefore:

- `DC_536534`: `evidence_status=probable`, exploratory and primary eligible;
- remaining six: `evidence_status=candidate`, conditional on the fitted broad
  component being a BLR, exploratory eligible, and excluded from primary rank.

No per-row numerical Delta-BIC values are tabulated. None is reconstructed from
figures. Narrative outflow-detection and three-component-fit outcomes are
preserved only where the paper states them explicitly.

## Mass, luminosity, and host semantics

MBH uses Reines et al. (2013) equation 5, tagged
`single-epoch-virial-halpha-reines2013` and grouped as
`virial_balmer_single_epoch`. The paper's additional `0.4 dex` virial
systematic is stored separately from the Table 1 errors and is not applied to
the nominal masses.

Lbol is derived through the Greene & Ho (2005) broad-Halpha-to-L5100 relation
with `BC5100=9.26`. The tabulated Eddington ratios are consequently derived
from the same Lbol and MBH, not independent evidence. Their published
logarithmic values are retained, and the canonical linear ratio is an explicit
base-10 transformation.

Table 1 host masses are the integrated pre-JWST Faisst et al. (2020) SED
results. The paper discusses spatially resolved alternatives that are about
0.6 dex lower for the candidate sample, but does not provide an authoritative
per-object replacement table here. No alternate masses are invented.

`DC_848185_a` and `DC_848185_b` are two candidate nuclei in one complex merger
system. They retain separate measurement and physical-object IDs, share
`host_system_id=HZS-DC-848185`, and mark the repeated Table 1 stellar mass as a
shared system total. The seven rows therefore represent seven candidate nuclei
in six host systems. A coordinate/redshift search produces no candidate link
to the frozen broad-line foundation.

The paper gives no LRD classification, so `lrd_flag` remains missing. Lensing
is not part of the reported mass inference; the admission mapping records
`lensing_status=not_reported` and an explicit project decision that no lensing
mass correction is required. All candidates carry merger evidence from the
source discussion; the two `DC_848185` nuclei also carry the independent
`dual_nucleus` phenotype.

The source files and internal Ren adapter pass the canonical admission gate in
memory. The seven measurements are included in v2 and v3, with their candidate
evidence, shared-host scope, and conditional-mass semantics retained in the
class-aware science products. See `docs/reference/admission-schema.md`.
