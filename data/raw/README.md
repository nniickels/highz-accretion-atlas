# Raw source data

This folder contains original source tables and manual extractions. Filenames
identify their sources. Preserve reported values; apply corrections and
interpretation choices in the processing code rather than editing source values
in place. Corrections apply to every affected catalogue version.

[Sources](../sources.md) and the [source registry](../source_provenance_registry.csv)
record publication versions, source locations, archive hashes, and extraction
limits. The [versioning guide](../../docs/guides/versioning.md) defines admission rules.

## Main extraction groups

- `baccus26_nirspec_blagn_table1_zge4_new.csv` and
  `fei26_glimpse_blagn_tables1_2_new.csv` add comparable broad-line active
  galactic nuclei to v2 and v3. The Baccus extract excludes new cluster-field
  rows without published lensing corrections. The Fei extract retains the
  published GLIMPSE magnification corrections.
- `v3_jwst_heterogeneous_expansion.csv` contains 78 rows for the v3 expansion.
  Known aliases and overlaps are excluded. Proxy masses, estimates that assume
  an Eddington ratio, and upper limits are retained as context rather than used
  as numerical growth masses.
- `zhuang25_nexus_wfss_table1_zge4.csv`, `lin25_cosmos3d_blagn_table1.csv`, and
  `napolitano25_seven_wonders_agn_candidates.csv` supply further v3 measurements.
  NEXUS and COSMOS-3D retain published Balmer-line virial masses. GHZ4 and GHZ7
  remain candidates identified through high-ionization lines, without eligible
  mass estimates.

`baccus_published_table1.txt` supplies the published-revision sensitivity
calculation; the frozen catalogue retains the original preprint values. This
machine-readable table is pinned by the provenance manifest.

## Bounded October 2026 admission

- [capers-lrd-z9 source values, full screen and admission basis](../../docs/source-notes/capers-lrd-z9-extraction-notes.md).
- [canucs-lrd-z86 source values, full screen and admission basis](../../docs/source-notes/canucs-lrd-z86-extraction-notes.md).
- [j1007-agn source values, full screen and admission basis](../../docs/source-notes/j1007-agn-extraction-notes.md).
- [macs0416-y1 source values, full screen and admission basis](../../docs/source-notes/macs0416-y1-extraction-notes.md).
- [sapphires-z847 source values, full screen and admission basis](../../docs/source-notes/sapphires-z847-extraction-notes.md).

Four Balmer mass families enter v2 and v3; SAPPHIRES is v3-only without a mass.
The cutoff remains 2026-09-03; retrieval/admission was 2026-10-17. Modeling
alternatives are correlated source observables, not independent objects.
