# Dataset versioning

v1–v3 identify data additions, not code milestones or public releases.
The canonical source-family review cutoff is 2026-09-03; see
[`../reference/literature-scope.md`](../reference/literature-scope.md). "Final v3"
means final within that declared admission scope, not an evergreen exhaustive
census of the literature.

## v1 — original complete analysis

The original 23-row Juodzbalis et al. JADES BLAGN catalogue. v1 contains the
complete present-day analysis: standardized catalogue, baseline evaluation,
rankings, uncertainty propagation, systematic sensitivity, duty-cycle
diagnostics, all figure types, compatibility products, and per-object gallery.
Accuracy fixes apply here unless they exist only for a later source/object type.

## v2 — expanded comparable BLAGN

Adds the comparable JWST broad-line source families from Taylor, Matthee, Lin,
Harikane, Davis/THRILS, Ren, Greene/UNCOVER, Kocevski/RUBIES, Skyfire/CEERS,
Larson/CEERS 1019, Killi/J0647, Uebler/ZS7, Baccus, Fei/GLIMPSE,
Taylor/CAPERS, Tripodi/CANUCS, Schindler/J1007, and Takechi/MACS0416-Y1. These
sources share the v2 object-type scope: 222 measurements, 215 object records, and 214
hosts. Baccus cluster-field rows without source-published lensing corrections
are excluded; Fei's GLIMPSE values include explicit magnification corrections.

## v3 — JWST-identified heterogeneous catalogue

Adds UHZ1's JWST/Chandra X-ray evidence history, the audited Scholtz JADES
narrow-line candidates, GN-z11's high-ionization-line accretion evidence, and
the wider heterogeneous source set documented in the extraction notes.
Added code handles distinct object
classes, evidence states, mass-comparability groups, missing/conditional masses,
and explicit no-inference cases. Source-level assignment governs membership: a
heterogeneous catalogue belongs to v3 even when individual rows resemble v2
objects. The final completion adds the heterogeneous NEXUS WFSS and COSMOS-3D
samples plus the GHZ4/GHZ7 high-ionization candidates. v3 has 355 measurements,
343 object records, and 342 hosts; 241 objects
support numerical growth inference.

## Invariants

Every version uses the latest applicable corrections and the same analysis and
figure definitions. Figures differ only because dataset membership, object
classes, or supported measurements differ.

## v4 — focused PBH growth-analysis extension

For v4, the version label identifies a new
**analysis**, not another catalogue expansion. v4 reads the frozen v3 catalogue
and conservative publication-membership policies. It does not introduce
`data/processed/v4`, alter v1–v3 dataset contracts, or change the source cutoff.

The isolated outputs under `results/v4/` test the growth component of Dayal
(2024) for three high-pressure primary targets and GN-z11, with independent
accretion onset, Monte Carlo mass support, and astrophysical controls.
Its separate config/manifest and optional notebook are documented in
[the v4 methods](../reference/pbh-growth-v4.md). A future formation or abundance
study is outside this analysis. Manuscript and poster products remain separate.

## 17 October 2026 membership revision

The unchanged 2026-09-03 cutoff now includes four new Balmer families
(CAPERS, CANUCS, J1007 and MACS0416-Y1) in v2/v3, and the mass-free SAPPHIRES
candidate in v3 only. Actual source retrieval/admission date is 2026-10-17.
This changes catalogue membership rather than correcting an extracted value.
The preceding scientific edition is retained at
`fc0c5501ad2271865b1c040307cad8dd8ca5721a`. v1 is unchanged. Source-specific
calibrations/errors are preserved: comparable does not mean recalibrated.
See [scope and source decisions](../reference/literature-scope.md).
