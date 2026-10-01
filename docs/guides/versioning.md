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
Larson/CEERS 1019, Killi/J0647, Uebler/ZS7, Baccus, and Fei/GLIMPSE. These
sources share the v2 object-type scope: 218 measurements, 211 objects, and 210
hosts. Baccus cluster-field rows without source-published lensing corrections
are excluded; Fei's GLIMPSE values include explicit magnification corrections.

## v3 — JWST-identified heterogeneous atlas

Adds UHZ1's JWST/Chandra X-ray evidence history, the audited Scholtz JADES
narrow-line candidates, GN-z11's high-ionization-line accretion evidence, and
the wider heterogeneous source set documented in the extraction notes.
Added code handles distinct object
classes, evidence states, mass-comparability groups, missing/conditional masses,
and explicit no-inference cases. Source-level assignment governs membership: a
heterogeneous catalogue belongs to v3 even when individual rows resemble v2
objects. The final completion adds the heterogeneous NEXUS WFSS and COSMOS-3D
samples plus the GHZ4/GHZ7 high-ionization candidates. v3 has 350 measurements,
338 objects, and 337 hosts; 237 objects
support numerical growth inference.

## Invariants

Every version uses the latest applicable corrections and the same analysis and
figure definitions. Figures differ only because dataset membership, object
classes, or supported measurements differ.

## v4 — focused PBH growth-analysis extension

At the user's requested v4 milestone, the version label identifies a new
**analysis**, not another catalogue expansion. v4 reads the frozen v3 catalogue
and conservative publication-membership policies. It does not introduce
`data/processed/v4`, alter v1–v3 dataset contracts, or change the source cutoff.

The isolated outputs under `results/v4/` test the growth component of Dayal
(2024) for three high-pressure primary targets and GN-z11, with independent
accretion onset, Monte Carlo mass support, and astrophysical controls.
Its separate config/manifest and optional notebook are documented in
[the v4 methods](../reference/pbh-growth-v4.md). A future formation or abundance
study is outside this milestone. Manuscript and poster products remain separate.
