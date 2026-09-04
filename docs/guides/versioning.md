# Dataset versioning

Versions identify data additions, not code milestones or public releases.
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
340 objects, and 339 hosts; 237 objects
support numerical growth inference.

## Invariants

Every version uses the latest applicable corrections and the same analysis and
figure definitions. Figures differ only because dataset membership, object
classes, or supported measurements differ. The contribution ledger is
append-only and retains historical terminology verbatim.
