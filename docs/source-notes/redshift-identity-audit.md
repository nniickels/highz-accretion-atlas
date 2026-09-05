# Redshift and identity audit — 5 September 2026

**Numerical source checks pass; scientific identity reconciliation remains open.**
Reviewed baseline: `64d526e`. The 340 stored object IDs must not yet be described
as 340 independently validated unique astrophysical objects. No catalogue
measurements, preferred rows, masses, redshifts or generated figures were changed
by this audit.

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
| GS-30148179 / SMILES-MIRI-2743 | 0.004 arcsec; z=5.922/5.920 | Merge-supported duplicate: reconcile physical/host IDs while preserving both source measurements and the mass-bearing preferred row. |
| RUBIES-EGS-927271 / DJA-8219 | 0.026 arcsec; z=6.786/6.785 | Merge-supported duplicate: retain both broad-line and narrow-line interpretations as measurements of the same target. |
| Baccus GDS_1210_9515 / JADES GS-8083 / Scholtz 00008083 | 0.014–0.024 arcsec; z=4.6477/4.753/4.665 | Likely duplicate group missed by the delta-z cut. Reconcile source target identifiers, spectra/redshift versions and preferred mass before merging. |
| JADES GS-10013704 / Scholtz 00099671 | 1.332 arcsec; delta-z=0.017 | Inspect source imaging and aperture/target definitions; proximity alone cannot decide distinct galaxies versus components/images. |
| Scholtz 00016745 / 00208643 | 0.612 arcsec; delta-z=0.008 | Inspect imaging and aperture definitions before treating distinct target IDs as distinct astrophysical objects. |

The existing CEERS repeated measurements, GS-204851/GOODS-S-13971, NX10835/Mascia,
and UHZ1 links are supported. Ren's DC_848185_a and _b remain explicitly distinct
components in a shared host. UHZ1's photometric and spectroscopic redshifts are
legitimate historical measurements, not a transcription discrepancy.

The two merge-supported pairs include a mass-free contextual row, so merging
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
prints the open groups. The second is the **publication identity gate** and
currently fails intentionally because five groups remain open. A green regression
or reproduction run is not a claim that these groups have been resolved.

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
