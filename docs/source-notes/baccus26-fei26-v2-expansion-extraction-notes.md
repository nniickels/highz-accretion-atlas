# Baccus and Fei v2 expansion extraction notes

Reviewed and implemented 2026-09-03. Both datasets are JWST/NIRSpec-identified
broad-line AGN catalogues with source-published single-epoch virial masses, so
they extend v2 and flow into v3. The admission adds only physical objects not
already represented in the catalogue.

| Source dataset | Source-level screen | New objects admitted | New growth-plottable objects | Object type | Version |
| --- | --- | ---: | ---: | --- | --- |
| Baccus et al. (2026) NIRSpec BLAGN compilation | 111 `z >= 4` rows representing 107 physical objects; 45 objects already represented and 13 new cluster-field objects lack source-published magnification corrections | 49 | 49 | Broad-line AGN | v2, flowing into v3 |
| Fei et al. (2026) GLIMPSE BLAGN sample | 10 source-table objects; all are new after catalogue crossmatch and all values are explicitly corrected for lensing magnification | 10 | 10 | Broad-line AGN, including 8 secure and 2 tentative candidates | v2, flowing into v3 |
| **Combined addition** | Identity-audited union | **59** | **59** | Broad-line AGN | **v2 and v3** |

“Growth-plottable” means that the source publishes a numerical black-hole mass
that does not assume the Eddington ratio being tested. The two tentative Fei
objects remain candidate evidence and are excluded from the primary comparison,
but their published virial masses support the broader uncertainty-aware growth
visualization.

## Baccus et al. (2026)

The extraction begins from Table 1 of the official arXiv HTML record. It keeps
the source's redshift, broad-line width, line luminosity, virial black-hole
mass, uncertainty, bolometric luminosity, Eddington ratio, host mass, and field
labels. Four multiple observations resolve to 107 physical objects among the
111 rows at `z >= 4`. Crossmatching finds 45 physical objects already in the
pre-expansion catalogue, leaving 62 potential additions.

Thirteen of those 62 potential additions lie in the GLIMPSE, MACS0416, or
MACS1149 cluster fields. The Baccus paper does not publish or apply object-level
lensing magnifications. Those rows are excluded from Baccus membership because
an uncorrected luminosity-dependent virial mass is not comparable under the
project lensing policy. The remaining 49 objects are admitted. Three have
published FWHM below 1000 km/s; they are retained as `probable` because the
source itself includes them in its BLAGN compilation, while the caveat remains
machine-readable.

Primary record: [Baccus et al. (2026)](https://arxiv.org/abs/2512.03281v1),
DOI `10.3847/1538-4357/ae7de7`. The archived source payload has SHA-256
`f165cd073c7e03cffa487c1e209a6c8ed4d2f009119e84145eca6b43e579a22a`.

The frozen Baccus measurements and screen refer to arXiv v1 Table 1. The
2026-09-04 independent audit checked coordinates, redshifts, masses, mass
uncertainties, and bolometric luminosities for all 49 admitted rows. The final
publication (v2) revises the table; its publication status must not be confused
with the measurement version. Adopting revised values needs a documented
reanalysis. This correction changes provenance, not catalogue numbers.

## Fei et al. (2026)

Tables 1 and 2 supply ten JWST/NIRSpec GLIMPSE broad-line objects. The source
publishes lensing magnifications and magnification-corrected physical values,
including virial black-hole masses. All ten are new after the catalogue identity
screen. Eight are secure and two, GLIMPSE-38548 and GLIMPSE-7404, retain the
source's tentative status as `candidate` evidence.

Three Fei objects also appear among the Baccus cluster-field rows screened out
above: GLIMPSE-5536, GLIMPSE-11026, and GLIMPSE-46938. They enter through Fei,
where the required lensing correction is explicit, and are not duplicated as
Baccus measurements.

Primary record: [Fei et al. (2026)](https://arxiv.org/abs/2509.20452v3), DOI
`10.3847/1538-4357/ae6248`. The archived source payload has SHA-256
`c619ea23d3e29b15ceb78d6a75b276a55010ff0d31b47b0a377856c0e37acde1`.

## Screened catalogue with no new objects

The Jin et al. J0226 catalogue does not add membership after the Baccus
admission: all four of its JWST-identified broad-line AGN are already present in
the admitted Baccus rows. It is therefore excluded under the requirement that a
new dataset contribute at least one new physical object.

The deterministic raw inputs are
`data/raw/baccus26_nirspec_blagn_table1_zge4_new.csv` and
`data/raw/fei26_glimpse_blagn_tables1_2_new.csv`. Source versions, checksums,
roles, and review dates are also recorded in
`data/source_provenance_registry.csv`.

The subsequent [publication-version sensitivity test](mass-error-and-publication-revision-audit.md)
compares the revised Baccus table with all 49 frozen objects. Headline growth
counts and the top five are unchanged in both tested membership treatments.
