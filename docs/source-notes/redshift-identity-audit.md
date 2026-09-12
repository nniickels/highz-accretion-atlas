# Redshift and identity audit — updated 7 September 2026

**Numerical source checks pass; three scientific identity groups remain open.**
The initial audit reviewed baseline `64d526e`. On 7 September 2026, two supported
duplicates were merged through the explicit, hash-pinned registry
`data/assembly/reconciled_identity_pairs.json`. All 350 source measurements and
source-native values remain; the catalogue now has 338 object records, 337 host
records, 237 numerical objects, and 101 catalogue-only records. The count remains
provisional until the three cases below are resolved.

## Resolved duplicates

| Group | Evidence and disposition |
| --- | --- |
| GS-30148179 / SMILES-MIRI-2743 | Source positions agree to 0.004 arcsec, z=5.922/5.920. Both measurements now share the JADES physical/host ID; retain the JADES mass-bearing preferred row and SMILES SED evidence as an alternate. |
| RUBIES-EGS-927271 / DJA-8219 | Source positions agree to 0.026 arcsec, z=6.786/6.785. Both measurements share the RUBIES physical/host ID; retain its mass-bearing preferred row and the alternate narrow-line interpretation. |

The audit fixture records these decisions separately from the assembly registry;
verification checks their consistency. Matching thresholds for other targets were
not widened. Four obsolete status panels were removed; source observables and
all numerical mass rows remain. These two merges do not change the numerical
growth sample or its headline requirements.

## Scope and evidence

- Checked all **350 admitted redshifts** against the recorded source versions.
- Checked all **323 available coordinate pairs**. The 27 rows without coordinates
  (25 Mazzolari objects, GHZ2 and MoM-BH*-1) remain explicitly missing; a sky search
  cannot establish their identity completeness.
- Checked the spectroscopic/photometric labels for all **31 mixed-sample rows**
  from SMILES and MEOW. The fixture contains **1,027 source-field expectations**,
  with source cells/excerpts, locators, URLs and archive/member hashes.
- Verified propagation through v1/v2/v3 measurements, preferred objects, aliases
  and measurement/object/host links. Cross-version aliases are retained by design.
- Independently computed great-circle separations using the haversine formula,
  scanning every measurement pair regardless of source family or redshift. Reviewed
  all **18 pairs within 2 arcsec or sharing a physical-object ID**. This deliberately
  avoids the existing incremental matcher's narrow redshift cut.
- Reviewed all **20 Mascia source rows**: eight retained new measurements, eleven
  matches to existing objects, and one scope exclusion. GS-3073 is **not ZS7**.
  Mascia's discussion cites its pre-JWST AGN identification (Grazian 2020); the
  project's JWST-essential identification rule supports a scope exclusion,
  not the previously asserted alias. The false alias explanation was corrected.

Expectations were read from primary TeX tables, independently retrieved HTML
cells, publisher tables and prior independent fixtures, not from generated
catalogue values. Numerical comparison uses absolute tolerance 1e-8 and no relative
tolerance; sexagesimal conversions and retained coordinate rounding are explicit.
The source checks concern central values and selected redshift-type labels, not
an exhaustive audit of redshift uncertainties or spectral reliability.

The JADES coordinate recheck used the current official DR3 GOODS-S v1.1 FITS
product: all 21 target positions agree. Its file hash differs from the originally
recorded v3.1.3 input, so this is an independent cross-check, not a claim that the
original archive was retrieved unchanged. GN-z11 coordinates were independently
checked against Oesch et al. (2016), ZS7 against the spectroscopic reanalysis by
Trefoloni et al. (2025), and UHZ1 against Bogdan's original sexagesimal position.
These supporting coordinate references do not replace admitted redshifts.

## Open scientific identity groups

| Group | Evidence | Required disposition |
| --- | --- | --- |
| Baccus GDS_1210_9515 / JADES GS-8083 / Scholtz 00008083 | 0.014–0.024 arcsec; z=4.6477/4.753/4.665 | Likely duplicate group missed by the delta-z cut. Reconcile source target identifiers, spectra/redshift versions and preferred mass before merging. |
| JADES GS-10013704 / Scholtz 00099671 | 1.332 arcsec; delta-z=0.017 | Inspect source imaging and aperture/target definitions; proximity alone cannot decide distinct galaxies versus components/images. |
| Scholtz 00016745 / 00208643 | 0.612 arcsec; delta-z=0.008 | Inspect imaging and aperture definitions before treating distinct target IDs as distinct astrophysical objects. |

The existing CEERS repeated measurements, GS-204851/GOODS-S-13971, NX10835/Mascia,
and UHZ1 links are supported. Ren's DC_848185_a and _b remain explicitly distinct
components in a shared host. UHZ1's photometric and spectroscopic redshifts are
legitimate historical measurements, not a transcription discrepancy.

The two resolved pairs include a mass-free contextual row, so merging
those pairs alone would not add a new mass or change the reference high-pressure
tail. They would change unique-object/class/coverage counts. The Baccus group
also involves competing masses and redshifts: regenerate and reassess after a
preferred-measurement decision; do not assume all object-level summaries survive.

## Executable checks

```bash
.venv/bin/python -m src.internal.verify_redshift_identity
.venv/bin/python -m src.internal.verify_redshift_identity --require-resolved
```

The first command verifies the numerical expectations and review coverage and
prints the open groups. The second is the **strict full-catalogue identity gate**
and currently fails because three groups remain open. Closure is required before
readmitting their records or claiming a final unique-object census. The
conservative manuscript excludes those records and has a separate passing
exclusion check, described below. A green regression or reproduction run is
not a claim that these groups have been resolved.

`data/validation/redshift_identity_checks.json` is pinned in the source-provenance
manifest. To extend it, retrieve the recorded URL, verify its archive/member hash,
review the source row and coordinate convention, and independently record the
expected value and evidence. Resolve each identity decision using the sources,
then update the reviewed pair disposition and regenerate affected products.
Do not silently increase match thresholds or derive expectations from outputs.

Primary references: [Mascia Table 2 and GS-3073 discussion](https://arxiv.org/html/2608.25021v1),
[official JADES DR3 coordinate catalogue](https://archive.stsci.edu/hlsps/jades/dr3/goods-s/catalogs/hlsp_jades_jwst_nirspec_goods-s_prism-line-fluxes_v1.1_catalog.fits),
[GN-z11 discovery paper](https://assets.science.nasa.gov/content/dam/science/missions/hubble/releases/2016/03/STScI-01EVSR4JPCXZB7365EVHP9905G.pdf),
[ZS7 spectroscopic reanalysis, Table 1](https://api.repository.cam.ac.uk/server/api/core/bitstreams/152489de-fd1d-4de4-b0bf-82027721d6ec/content).
Individual pair evidence is linked through the fixture's measurement source records.

## Evidence still needed (reviewed 7 September 2026)

- **Baccus/JADES 8083:** the retained Baccus v1 source table explicitly gives
  GDS_1210_9515 at z=4.6477 and log(MBH/Msun)=5.59; Scholtz explicitly identifies
  8083 as a previously known type-1 target, but these do not settle the conflicting
  source redshifts or preferred mass. Obtain a program/target crosswalk and inspect
  the associated spectra before merging. Do not average the masses or substitute
  a different publication version silently.
- **99671 / 10013704 and 16745 / 208643:** the source sample treats these as
  separate NIRSpec targets in programs 1210/3215. Target IDs, line diagnostics,
  angular proximity and similar redshifts alone do not settle distinct hosts
  versus components or repeated apertures. Review NIRCam segmentation/cutouts
  with the NIRSpec shutter footprints before assigning a shared identity.

Available source-table and source-text checks did not supply that decisive
imaging/spectral evidence. These remain actionable scientific review tasks, not
resolved cases or test failures to suppress. The ordinary `identity_resolution_status`
field records the existing assembly decision; this audit is the stricter check
of independently established astrophysical uniqueness.


## Manuscript follow-up check (7 September 2026)

The source HTML was checked again for the open groups. The
[JADES broad-line table](https://arxiv.org/html/2504.03551v2) still lists GS-8083
at z=4.753 with log(MBH/Msun)=7.10, while the retained Baccus v1 extraction
lists GDS_1210_9515 at z=4.6477 and 5.59. The
[Baccus HTML](https://arxiv.org/html/2512.03281v1) did not expose a searchable
9515 row; it provides no new target crosswalk for this decision. The
[Scholtz tables](https://arxiv.org/html/2311.18731v4) retain 16745 under program
1210 and 99671/208643 under 3215. These checks confirm the documented source
versions and target labels; they do not supply the aperture/imaging evidence
or reconcile the competing spectra. All three dispositions remain open.
The manuscript now distinguishes the assembly registry's resolved flag from
this independent scientific identity gate explicitly in its eligibility rules.


## Conservative manuscript disposition (7 September 2026)

The requested alternative is now implemented: **exclude all six object records
linked to the three open groups from manuscript inference**, including every
linked measurement when constructing the object mask. Seven source measurements
remain in the catalogue. The three mass-bearing exclusions are GDS_1210_9515,
GS-8083, and GS-10013704. The other three were already no-inference records.
At the identity-only stage, this produced 224 primary and 234 exploratory
numerical manuscript objects. These are historical counts, before the later
evidence-selection revision.

The identity registry is `paper/identity_exclusions.json`. At that stage, for all
five manuscript scenarios,
threshold counts and top-five order are unchanged; reference p16 and P>=0.95 counts
also agree. The primary reference median changed from 0.574 to 0.578.

The current manuscript additionally retains four tentative JADES detections only
in the exploratory sample under `paper/evidence_selection.json`, giving 220/234
objects. Current membership and sensitivity tables are in `paper/analysis/`.
With this evidence policy held fixed, identity exclusions change primary
membership from 223 to 220 and the median from 0.571 to 0.573, while preserving
the primary/exploratory 8/14 point, 6/10 p16, and 5/8 P>=0.95 counts.

`python -m src.internal.publication_selection` verifies complete exclusion and
stored-table reproduction, including the underlying source/identity audit.
The existing `verify_redshift_identity --require-resolved` remains unchanged and
fails while these identities remain open. Do not describe the new exclusion
check as proving identity resolution. Full-catalogue figures are explicitly
contextual and do not determine the manuscript's numerical inference samples.

A further exact-name literature search found the published Scholtz source tables
but no decisive target crosswalk or aperture/segmentation reconciliation. The
[author-repository published table](https://api.repository.cam.ac.uk/server/api/core/bitstreams/7d5f5d95-94f3-4ceb-925f-18abfe17f938/content)
retains the separate program/target labels; that alone does not settle identity.
The remaining astrophysical questions above are deferred to evidence-backed
readmission. No source value, matching threshold, or audit disposition is changed.

The subsequent manuscript-figure pass replaces the contextual full-catalogue
plots in the draft with dedicated publication-sample figures. Original catalogue
figures remain available separately; manuscript figures do not plot the excluded
measurements. The coverage panel records the exclusions only as a separate count.
