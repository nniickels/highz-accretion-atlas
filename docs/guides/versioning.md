# Dataset versioning

Versions identify data additions, not code milestones or public releases.
The canonical source-family review cutoff is 2026-09-03; see
[`../current/literature-scope.md`](../current/literature-scope.md). "Final v3"
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
Larson/CEERS 1019, Killi/J0647, and Uebler/ZS7. These sources share the v2
object-type scope: 159 measurements, 152 objects, and 151 hosts.

## v3 — JWST-identified heterogeneous atlas

Adds UHZ1's JWST/Chandra X-ray evidence history, the audited Scholtz JADES
narrow-line candidates, and GN-z11's high-ionization-line accretion evidence.
Added code handles distinct object
classes, evidence states, mass-comparability groups, missing/conditional masses,
and explicit no-inference cases. v3 has 183 measurements, 174 objects, and 173
hosts; 153 objects support numerical growth inference.

## Invariants

Every version uses the latest applicable corrections and the same analysis and
figure definitions. Figures differ only because dataset membership, object
classes, or supported measurements differ. The contribution ledger is
append-only and retains historical terminology verbatim.
