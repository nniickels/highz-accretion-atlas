# Dataset versioning

Versions identify data additions, not code milestones or public releases.
The canonical source-family review cutoff is 2026-08-27; see
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

Adds Taylor CEERS/RUBIES, Matthee EIGER/FRESCO, Lin ASPIRE, Harikane NIRSpec,
Davis/THRILS, and Ren ALPINE/CRISTAL candidates. These sources share the broad
scientific workflow and therefore form one expansion: 119 measurements, 112
objects, and 111 hosts.

## v3 — final heterogeneous atlas

Adds XQR-30 and GNIRS-50 luminous quasars, UHZ1's X-ray evidence history, and
the audited Scholtz narrow-line candidates. Added code handles distinct object
classes, evidence states, mass-comparability groups, missing/conditional masses,
and explicit no-inference cases. v3 has 234 measurements, 219 objects, and 218
hosts; 196 objects support numerical growth inference.

## Invariants

Every version uses the latest applicable corrections and the same analysis and
figure definitions. Figures differ only because dataset membership, object
classes, or supported measurements differ. The contribution ledger is
append-only and retains historical terminology verbatim.
